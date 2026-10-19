#!/usr/bin/env python3
"""
UDX SME Golden Record Engine
----------------------------
Reads five Excel source files from ./input, uses ELSA as the primary source
for business/profile attributes, consolidates SMEs, and writes:
  1) sme_golden_records.json
  2) financing_potential_leads.json
  3) development_training_potential.json
  4) udx_run_summary.json

Requirements:
    pip install pandas openpyxl

Input filenames: any Excel filenames containing ELSA, CBRS, EPC, JOMXCESS, and MIS4 respectively.

Important:
- The script does not hardcode source records.
- RAW/source values are not overwritten; normalization is used for matching.
- Lead outputs are candidate lists for human review, not credit/eligibility decisions.
- Update the column aliases and business rules below to reflect the actual source
  workbook headers and approved programme criteria.
"""

from __future__ import annotations

import json
import re
import hashlib
from datetime import datetime, date
from pathlib import Path
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

import pandas as pd


# ---------------------------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "input"
OUTPUT_DIR = BASE_DIR / "output"

# Source systems to discover in INPUT_DIR. Filenames may contain prefixes,
# suffixes, dates, version labels, spaces, or other text, e.g.:
#   "Source 3-ELSA-Dummy.xlsx", "ELSA_EXPANDED.xlsx", "my_CBRS_export_2026.xlsx"
# The script searches filenames case-insensitively for each keyword.
SOURCE_KEYWORDS = ("ELSA", "CBRS", "EPC", "JOMXCESS", "MIS4")

# Optional per-source sheet overrides. Leave None to use the first worksheet.
# Keys are source-system names; values are worksheet names.
SHEET_NAMES = {
    "CBRS": None,
    "ELSA": None,
    "EPC": None,
    "JOMXCESS": None,
    "MIS4": None,
}


def discover_source_files() -> Dict[str, str]:
    """Discover one Excel file per source by keyword; never hardcode filenames."""
    if not INPUT_DIR.exists():
        raise FileNotFoundError(
            f"Input folder not found: {INPUT_DIR}. Create it and add the five source workbooks."
        )

    excel_files = [
        p for p in INPUT_DIR.iterdir()
        if p.is_file() and p.suffix.lower() in {".xlsx", ".xlsm", ".xls"}
        and not p.name.startswith("~$")
    ]

    discovered: Dict[str, str] = {}
    for source in SOURCE_KEYWORDS:
        matches = [p for p in excel_files if source.lower() in p.name.lower()]
        if not matches:
            raise FileNotFoundError(
                f"No Excel filename containing '{source}' was found in {INPUT_DIR}. "
                f"Available files: {[p.name for p in excel_files]}"
            )
        # If multiple matches exist, prefer the most recently modified file.
        # This supports keeping historical exports in input without renaming them.
        matches.sort(key=lambda p: (p.stat().st_mtime, p.name.lower()), reverse=True)
        discovered[source] = matches[0].name
        if len(matches) > 1:
            print(
                f"WARNING: Multiple files match {source}: {[p.name for p in matches]}. "
                f"Using latest modified file: {matches[0].name}"
            )

    return discovered

UDX_VERSION = "1.0"

MATCHING_RULES = {
    "BLOCK": ["SSM", "COMPANY_NAME"],
    "SSM_FALLBACK": "COMPANY_NAME",
    "WEIGHTS": {
        "SSM": 40,
        "COMPANY_NAME": 25,
        "PHONE": 15,
        "EMAIL": 10,
        "ADDRESS": 10,
    },
    "MATCH_THRESHOLD": 90,
    "REVIEW_THRESHOLD": 75,
    "NAME_MATCH_THRESHOLD": 95,
    "NAME_REVIEW_THRESHOLD": 85,
}

# Column aliases: first match found in the source headers will be used.
# Add actual header names here if your Excel files use different terminology.
ALIASES = {
    "business_name": [
        "business name", "company name", "enterprise name", "name of business",
        "name of company", "nama perniagaan", "nama syarikat", "business",
        "company", "entrepreneur name", "nama usahawan", "customer name",
    ],
    "ssm": [
        "ssm", "ssm no", "ssm number", "registration no", "registration number",
        "company registration no", "company registration number", "business registration no",
        "no pendaftaran", "no pendaftaran syarikat", "no daftar perniagaan",
    ],
    "phone": [
        "phone", "telephone", "mobile", "mobile no", "mobile number", "contact no",
        "contact number", "phone number", "telefon", "no telefon", "no tel",
        "handphone", "hp no",
    ],
    "email": ["email", "email address", "e-mail", "emel", "alamat emel"],
    "address": [
        "address", "business address", "registered address", "alamat",
        "alamat perniagaan", "alamat syarikat", "premise address",
    ],
    "postcode": ["postcode", "postal code", "post code", "poskod", "zip code"],
    "city": ["city", "town", "bandar", "daerah"],
    "state": ["state", "negeri"],
    "sector": [
        "sector", "business sector", "industry", "industry sector", "business nature",
        "nature of business", "jenis perniagaan", "sektor", "bidang perniagaan",
    ],
    "business_size": [
        "kategori sme", "sme category", "business size", "size of business",
        "enterprise size", "kategori perusahaan", "saiz perniagaan", "saiz perusahaan",
    ],
    "business_status": [
        "business status", "company status", "status perniagaan", "status syarikat",
        "status", "operating status",
    ],
    "annual_revenue": [
        "annual revenue", "revenue", "sales turnover", "annual sales", "turnover",
        "pendapatan tahunan", "jualan tahunan", "hasil tahunan",
    ],
    "financing_status": [
        "financing status", "loan status", "application status", "financing application",
        "loan application status", "status pembiayaan", "financing",
    ],
    "financing_need": [
        "financing need", "financing required", "loan requirement", "funding need",
        "amount requested", "financing amount", "jumlah pembiayaan",
    ],
    "training_status": [
        "training status", "training attended", "course attended", "development programme",
        "program attended", "status latihan", "latihan", "training",
    ],
    "digitalisation": [
        "digitalisation", "digitalization", "digital readiness", "digital adoption",
        "digital status", "pendigitalan",
    ],
    "entrepreneur_id": [
        "entrepreneur id", "sme id", "customer id", "client id", "participant id",
        "id usahawan", "id pelanggan",
    ],
    "contact_person": [
        "contact person", "pic", "person in charge", "owner name", "pemilik",
        "nama pemilik", "contact name",
    ],
    "programme": [
        "programme", "program", "programme name", "program name", "nama program",
        "initiative", "campaign",
    ],
}

# Lead-generation signals are intentionally broad and configurable.
# A record is included when a relevant ELSA/source field has a positive signal.
FINANCING_POSITIVE_TERMS = (
    "need", "required", "interested", "apply", "application", "pending",
    "financing", "funding", "loan", "pembiayaan", "memohon", "berminat",
)
FINANCING_NEGATIVE_TERMS = (
    "rejected", "declined", "cancelled", "canceled", "withdrawn", "not interested",
    "ditolak", "batal",
)
TRAINING_POSITIVE_TERMS = (
    "need", "required", "interested", "not attended", "pending", "gap",
    "training", "development", "digital", "capacity building", "latihan",
    "pembangunan", "belum", "required",
)
TRAINING_NEGATIVE_TERMS = (
    "completed", "attended", "graduated", "not interested", "complete",
    "selesai", "telah hadir",
)

# Explicit ELSA questionnaire rules supplied for LT (Lead for Training) and
# LF (Lead for Financing). A lead is qualified only when the source-cell value
# equals the configured numeric value. Header matching ignores punctuation,
# capitalization and repeated whitespace.
QUESTIONNAIRE_RULES = [
    {
        "criterion": "Pemasaran Dalam Talian",
        "headers": ["Pemasaran Dalam Talian"],
        "lead_types": {"LT": 0},
    },
    {
        "criterion": "Meningkatkan perolehan dengan meneroka pasaran baru",
        "headers": ["Meningkatkan perolehan dengan meneroka pasaran baru", "Meningkatkan perolehan dengan meneroka pasaran baharu"],
        "lead_types": {"LF": 1},
    },
    {
        "criterion": "Meningkatkan kemahiran tenaga kerja",
        "headers": ["Meningkatkan kemahiran tenaga kerja"],
        "lead_types": {"LT": 1},
    },
    {
        "criterion": "Meningkatkan keupayaan kepimpinan pengurus",
        "headers": ["Meningkatkan keupayaan kepimpinan pengurus"],
        "lead_types": {"LT": 1},
    },
    {
        "criterion": "Pelaburan modal (dalam premis, mesin dll)",
        "headers": ["Pelaburan modal dalam premis mesin dll", "Pelaburan modal"],
        "lead_types": {"LF": 1},
    },
    {
        "criterion": "Membangunkan dan melancarkan produk/perkhidmatan baru",
        "headers": ["Membangunkan dan melancarkan produk perkhidmatan baru", "Membangunkan dan melancarkan produk perkhidmatan baharu"],
        "lead_types": {"LF": 1, "LT": 1},
    },
    {
        "criterion": "Pernah mencuba mendapatkan pembiayaan dalam dua tahun kebelakangan ini",
        "headers": ["Adakah anda pernah mencuba mendapatkan pembiayaan untuk perniagaan anda sejak dua tahun kebelakangan ini"],
        "lead_types": {"LF": 1},
    },
    {
        "criterion": "Persatuan Perniagaan",
        "headers": ["Persatuan Perniagaan"],
        "lead_types": {"LF": 1},
    },
    {
        "criterion": "Keluarga/Kawan",
        "headers": ["Keluarga Kawan", "Keluarga", "Kawan"],
        "lead_types": {"LF": 1},
    },
]


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def is_blank(value: Any) -> bool:
    if value is None:
        return True
    try:
        if pd.isna(value):
            return True
    except (TypeError, ValueError):
        pass
    return str(value).strip().lower() in {"", "nan", "none", "null", "nat", "-"}


def clean_value(value: Any) -> Any:
    if is_blank(value):
        return None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return value.isoformat()
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()
    return value


def normalize_business_size(value: Any) -> str:
    """Normalize an existing SME category; do not infer size from revenue or employees."""
    if is_blank(value):
        return "Unclassified"
    text = re.sub(r"\s+", " ", str(value)).strip().lower()
    compact = re.sub(r"[^a-z]", "", text)
    if compact in {"micro", "microenterprise", "mikro", "mikroenterprise", "mikroperusahaan"} or "micro" in compact or "mikro" in compact:
        return "Micro"
    if compact in {"small", "smallenterprise", "kecil", "perusahaankecil"} or "small" in compact or "kecil" in compact:
        return "Small"
    if compact in {"medium", "mediumenterprise", "sederhana", "perusahaansederhana"} or "medium" in compact:
        return "Medium"
    if compact in {"large", "largeenterprise", "besar", "perusahaanbesar"} or "large" in compact or "besar" in compact:
        return "Large"
    # Preserve unrecognised source classifications for traceability in a separate bucket.
    return "Unclassified"


def business_size_distribution(golden_records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Count unified golden profiles by the existing source SME category."""
    categories = ["Micro", "Small", "Medium", "Large", "Unclassified"]
    counts = {category: 0 for category in categories}
    for record in golden_records:
        category = normalize_business_size(record.get("BUSINESS_SIZE"))
        counts[category] = counts.get(category, 0) + 1
    return {
        "TITLE": "SME by Business Size",
        "DESCRIPTION": "Distribution of unified SME master profiles",
        "TOTAL_PROFILES": len(golden_records),
        "DISTRIBUTION": [
            {"BUSINESS_SIZE": category, "COUNT": counts[category]}
            for category in categories
        ],
    }


def header_key(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def normalized_text(value: Any) -> str:
    if is_blank(value):
        return ""
    text = str(value).upper().strip()
    text = text.replace("&", " AND ")
    text = re.sub(r"\b(SDN BHD|SDN\. BHD\.|SENDIRIAN BERHAD)\b", " SDN BHD ", text)
    text = re.sub(r"\b(ENTERPRISES|ENTERPRISE)\b", " ENTERPRISE ", text)
    return re.sub(r"[^A-Z0-9]", "", text)


def normalize_phone(value: Any) -> str:
    digits = re.sub(r"\D", "", "" if is_blank(value) else str(value))
    if digits.startswith("0060"):
        digits = digits[2:]
    if digits.startswith("60"):
        return digits
    if digits.startswith("0"):
        return "6" + digits
    return digits


def normalize_email(value: Any) -> str:
    return "" if is_blank(value) else str(value).strip().lower()


def normalize_address(value: Any) -> str:
    return normalized_text(value)


def similarity(a: Any, b: Any) -> float:
    aa, bb = normalized_text(a), normalized_text(b)
    if not aa or not bb:
        return 0.0
    if aa == bb:
        return 1.0
    return SequenceMatcher(None, aa, bb).ratio()


def first_matching_column(columns: List[Any], aliases: List[str]) -> Optional[Any]:
    normalized_columns = {header_key(c): c for c in columns}
    # Exact normalized match first
    for alias in aliases:
        key = header_key(alias)
        if key in normalized_columns:
            return normalized_columns[key]
    # Then allow alias phrase contained in the header, avoiding too-short aliases.
    for alias in aliases:
        key = header_key(alias)
        if len(key) >= 5:
            for col_key, original in normalized_columns.items():
                if key in col_key or col_key in key:
                    return original
    return None


def read_source(source: str, filename: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    path = INPUT_DIR / filename
    if not path.exists():
        raise FileNotFoundError(
            f"Missing input file: {path}\n"
            f"Place {filename} in the input folder or update SOURCE_FILES."
        )

    sheet = SHEET_NAMES.get(source)
    df = pd.read_excel(path, sheet_name=sheet if sheet else 0, dtype=object)
    df = df.dropna(how="all").copy()
    df.columns = [str(c).strip() for c in df.columns]

    column_map = {}
    for field, aliases in ALIASES.items():
        found = first_matching_column(list(df.columns), aliases)
        if found is not None:
            column_map[field] = found

    records = []
    for row_idx, row in df.iterrows():
        raw = {str(k): clean_value(v) for k, v in row.to_dict().items()}
        record = {
            "source_system": source,
            "source_record_id": f"{source}-{row_idx + 2}",
            "source_row_number": int(row_idx) + 2,
            "raw": raw,
            "canonical": {},
        }
        for field, col in column_map.items():
            record["canonical"][field] = clean_value(row.get(col))
        record["canonical"]["business_name"] = record["canonical"].get("business_name")
        record["canonical"]["ssm"] = record["canonical"].get("ssm")
        record["canonical"]["phone"] = record["canonical"].get("phone")
        record["canonical"]["email"] = record["canonical"].get("email")
        record["canonical"]["address"] = record["canonical"].get("address")
        records.append(record)

    metadata = {
        "filename": filename,
        "sheet": sheet or str(pd.ExcelFile(path).sheet_names[0]),
        "record_count": len(records),
        "columns": list(df.columns),
        "mapped_fields": column_map,
        "unmapped_canonical_fields": [f for f in ALIASES if f not in column_map],
    }
    return pd.DataFrame(records), metadata


def canonical_key(record: Dict[str, Any]) -> str:
    c = record["canonical"]
    ssm = normalized_text(c.get("ssm"))
    if ssm:
        return "SSM:" + ssm
    name = normalized_text(c.get("business_name"))
    if name:
        return "NAME:" + name
    # Keep records with no identifiers separate and traceable.
    return "ROW:" + record["source_record_id"]


def pair_match_score(a: Dict[str, Any], b: Dict[str, Any]) -> float:
    ca, cb = a["canonical"], b["canonical"]
    weights = MATCHING_RULES["WEIGHTS"]
    score, available_weight = 0.0, 0.0

    pairs = [
        ("SSM", "ssm", lambda x, y: 1.0 if normalized_text(x) and normalized_text(x) == normalized_text(y) else 0.0),
        ("COMPANY_NAME", "business_name", similarity),
        ("PHONE", "phone", lambda x, y: 1.0 if normalize_phone(x) and normalize_phone(x) == normalize_phone(y) else 0.0),
        ("EMAIL", "email", lambda x, y: 1.0 if normalize_email(x) and normalize_email(x) == normalize_email(y) else 0.0),
        ("ADDRESS", "address", lambda x, y: similarity(x, y)),
    ]
    for weight_name, field, fn in pairs:
        av, bv = ca.get(field), cb.get(field)
        if is_blank(av) or is_blank(bv):
            continue
        weight = weights[weight_name]
        score += weight * fn(av, bv)
        available_weight += weight

    if available_weight == 0:
        return 0.0
    return round((score / available_weight) * 100, 2)


def are_same_entity(a: Dict[str, Any], b: Dict[str, Any]) -> bool:
    ca, cb = a["canonical"], b["canonical"]
    ssm_a, ssm_b = normalized_text(ca.get("ssm")), normalized_text(cb.get("ssm"))
    if ssm_a and ssm_b and ssm_a == ssm_b:
        return True

    # Do not merge conflicting non-empty registration numbers just because names match.
    if ssm_a and ssm_b and ssm_a != ssm_b:
        return False

    name_score = similarity(ca.get("business_name"), cb.get("business_name")) * 100
    if name_score >= MATCHING_RULES["NAME_MATCH_THRESHOLD"]:
        phone_a, phone_b = normalize_phone(ca.get("phone")), normalize_phone(cb.get("phone"))
        email_a, email_b = normalize_email(ca.get("email")), normalize_email(cb.get("email"))
        addr_score = similarity(ca.get("address"), cb.get("address")) * 100
        corroboration = (
            (phone_a and phone_a == phone_b)
            or (email_a and email_a == email_b)
            or addr_score >= 85
        )
        # If no corroborating data exists, only merge exact normalized names.
        return bool(corroboration or normalized_text(ca.get("business_name")) == normalized_text(cb.get("business_name")))
    return False


def make_groups(records: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Greedy entity resolution. Exact SSM is strongest; name matches need corroboration."""
    groups: List[List[Dict[str, Any]]] = []
    for record in records:
        placed = False
        for group in groups:
            if any(are_same_entity(record, existing) for existing in group):
                group.append(record)
                placed = True
                break
        if not placed:
            groups.append([record])
    return groups


def pick_value(group: List[Dict[str, Any]], field: str) -> Tuple[Any, Optional[str]]:
    """
    Prefer ELSA for most profile attributes, then prefer the most frequent non-empty
    value. Registry/CBRS are fallback sources for registration and official identity.
    """
    elsa_values = [
        (r["canonical"].get(field), r["source_system"])
        for r in group if r["source_system"] == "ELSA" and not is_blank(r["canonical"].get(field))
    ]
    if elsa_values:
        return elsa_values[0]

    values = [(r["canonical"].get(field), r["source_system"]) for r in group
              if not is_blank(r["canonical"].get(field))]
    if not values:
        return None, None

    # For registration number, prefer CBRS when available; otherwise most common.
    if field == "ssm":
        cbrs = [(v, s) for v, s in values if s == "CBRS"]
        if cbrs:
            return cbrs[0]

    counts: Dict[str, List[Tuple[Any, str]]] = {}
    for value, source in values:
        counts.setdefault(normalized_text(value), []).append((value, source))
    chosen = max(counts.values(), key=len)
    return chosen[0]


def make_sme_id(group: List[Dict[str, Any]], used_ids: set) -> str:
    c = group[0]["canonical"]
    state = ""
    for r in group:
        state = str(r["canonical"].get("state") or "").strip()
        if state:
            break
    state_code = {
        "SELANGOR": "SL", "KUALA LUMPUR": "KL", "WILAYAH PERSEKUTUAN KUALA LUMPUR": "KL",
        "JOHOR": "JH", "PENANG": "PG", "PULAU PINANG": "PG", "PERAK": "PK",
        "KEDAH": "KD", "KELANTAN": "KN", "TERENGGANU": "TR", "PAHANG": "PH",
        "MELAKA": "MK", "NEGERI SEMBILAN": "NS", "PERLIS": "PL", "SABAH": "SB",
        "SARAWAK": "SW", "PUTRAJAYA": "PJ", "LABUAN": "LB",
    }.get(state.upper(), "MY")

    ssm = normalized_text(c.get("ssm"))
    name = normalized_text(c.get("business_name"))
    seed = ssm or name or "|".join(sorted(r["source_record_id"] for r in group))
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest().upper()
    # Avoid confusing characters: 0, 1, O, I.
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    token = "".join(alphabet[int(digest[i:i+2], 16) % len(alphabet)] for i in range(0, 10, 2))
    sme_id = f"MY-{state_code}-{token}"
    suffix = 2
    base = sme_id
    while sme_id in used_ids:
        sme_id = f"{base}-{suffix}"
        suffix += 1
    used_ids.add(sme_id)
    return sme_id


def numeric_flag(value: Any) -> Optional[float]:
    """Parse binary Excel flags, including numeric cells and labels such as '1 - Yes'."""
    if is_blank(value):
        return None
    if isinstance(value, bool):
        return 1.0 if value else 0.0

    text = str(value).strip().lower()
    # Excel exports sometimes turn coded responses into strings, e.g. "1 - Yes",
    # "0 (No)", or "1.0: selected". Accept a leading 0/1 only when clearly
    # separated from the descriptive label; do not treat arbitrary text as a flag.
    try:
        number = float(text)
        return number if number in (0.0, 1.0) else None
    except (TypeError, ValueError):
        pass

    match = re.match(r"^([01])(?:\.0+)?(?:\s*(?:[-–—:.)]|\s)\s*.+)?$", text)
    if match:
        return float(match.group(1))
    return None


def questionnaire_header_matches(header: Any, aliases: List[str]) -> bool:
    """Match question columns despite punctuation, line breaks, and minor header variations."""
    raw_header = header_key(header)
    compact_header = re.sub(r"[^a-z0-9]", "", raw_header)
    for alias in aliases:
        alias_norm = header_key(alias)
        compact_alias = re.sub(r"[^a-z0-9]", "", alias_norm)
        if not compact_alias:
            continue
        # Exact/contained phrase matching handles extra instructions in column names.
        if alias_norm in raw_header or raw_header in alias_norm:
            return True
        if compact_alias in compact_header or compact_header in compact_alias:
            return True
        # Handle small export differences (e.g. punctuation/wording changes).
        if len(compact_alias) >= 18 and SequenceMatcher(None, compact_alias, compact_header).ratio() >= 0.88:
            return True
    return False


def questionnaire_signals(source_records: List[Dict[str, Any]], lead_type: str) -> List[Dict[str, Any]]:
    """Return criteria whose configured 0/1 value qualifies this SME for LT/LF."""
    signals: List[Dict[str, Any]] = []
    # Only the ELSA questionnaire is authoritative for these criteria when an ELSA
    # record exists. Fall back to other source rows only for SMEs without ELSA.
    ordered_records = sorted(source_records, key=lambda r: (r.get("source_system") != "ELSA", r.get("source_system", "")))
    elsa_records = [r for r in ordered_records if r.get("source_system") == "ELSA"]
    if elsa_records:
        ordered_records = elsa_records

    for rule in QUESTIONNAIRE_RULES:
        expected = rule["lead_types"].get(lead_type)
        if expected is None:
            continue
        matched = False
        for record in ordered_records:
            raw = record.get("raw") or {}
            for header, value in raw.items():
                if not questionnaire_header_matches(header, rule["headers"]):
                    continue
                actual = numeric_flag(value)
                if actual == float(expected):
                    signals.append({
                        "CRITERION": rule["criterion"],
                        "SOURCE_SYSTEM": record.get("source_system"),
                        "SOURCE_FIELD": header,
                        "SOURCE_VALUE": clean_value(value),
                        "RULE": f"{lead_type} = YES when value = {expected}",
                    })
                    matched = True
                    break
            if matched:
                break
    return signals


def source_signal(source_records: List[Dict[str, Any]], field: str, positive_terms: tuple, negative_terms: tuple) -> Tuple[bool, str]:
    """Qualify LT/LF strictly from the configured Malay questionnaire rules."""
    lead_type = "LF" if field == "financing" else "LT"
    explicit_signals = questionnaire_signals(source_records, lead_type)
    if explicit_signals:
        criteria = "; ".join(
            f"{item['CRITERION']} (value={item['SOURCE_VALUE']})"
            for item in explicit_signals
        )
        return True, f"{lead_type} questionnaire rule matched: {criteria}"
    return False, f"No {lead_type} questionnaire criterion matched its configured value"


def build_outputs(all_records: List[Dict[str, Any]], source_meta: Dict[str, Any]) -> Dict[str, Any]:
    groups = make_groups(all_records)
    used_ids = set()
    golden_records = []
    financing_leads = []
    training_leads = []

    profile_fields = [
        "business_name", "ssm", "phone", "email", "address", "postcode", "city",
        "state", "sector", "business_size", "business_status", "annual_revenue", "financing_status",
        "financing_need", "training_status", "digitalisation", "entrepreneur_id",
        "contact_person", "programme",
    ]

    for group in groups:
        # Prefer ELSA's row as the canonical starting record where available.
        group_sorted = sorted(group, key=lambda r: (r["source_system"] != "ELSA", r["source_system"]))
        values, provenance = {}, {}
        for field in profile_fields:
            value, source = pick_value(group_sorted, field)
            values[field] = value
            provenance[field] = {"source_system": source, "source_field": field} if source else None

        # Use the source's existing SME category (e.g. Kategori SME). Do not infer
        # business size from revenue or employee count because no thresholds were supplied.
        values["business_size"] = normalize_business_size(values.get("business_size"))

        scores = []
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                scores.append(pair_match_score(group[i], group[j]))
        confidence = max(scores) if scores else 100.0
        match_status = (
            "AUTO_MATCH" if len(group) == 1 or confidence >= MATCHING_RULES["MATCH_THRESHOLD"]
            else "REVIEW"
        )

        sme_id = make_sme_id(group_sorted, used_ids)
        source_systems = sorted(set(r["source_system"] for r in group))
        rec = {
            "SME_ID": sme_id,
            **values,
            "MATCH_CONFIDENCE": confidence,
            "MATCH_STATUS": match_status,
            "SOURCE_SYSTEMS": source_systems,
            "SOURCE_RECORD_COUNT": len(group),
            "SOURCE_RECORDS": [
                {
                    "source_system": r["source_system"],
                    "source_record_id": r["source_record_id"],
                    "source_row_number": r["source_row_number"],
                } for r in group
            ],
            "PROVENANCE": provenance,
        }
        golden_records.append(rec)

        # Lead lists only include records with a mapped positive signal.
        financing_ok, financing_reason = source_signal(group_sorted, "financing", FINANCING_POSITIVE_TERMS, FINANCING_NEGATIVE_TERMS)
        financing_criteria = questionnaire_signals(group_sorted, "LF")
        if financing_ok:
            financing_leads.append({
                "SME_ID": sme_id,
                "BUSINESS_NAME": values.get("business_name"),
                "SSM": values.get("ssm"),
                "PHONE": values.get("phone"),
                "EMAIL": values.get("email"),
                "STATE": values.get("state"),
                "SECTOR": values.get("sector"),
                "ANNUAL_REVENUE": values.get("annual_revenue"),
                "FINANCING_STATUS": values.get("financing_status"),
                "FINANCING_NEED": values.get("financing_need"),
                "LEAD_REASON": financing_reason,
                "LEAD_TYPE": "LF",
                "LEAD_CRITERIA": financing_criteria,
                "LEAD_SOURCE_PRIORITY": "ELSA",
                "SOURCE_SYSTEMS": source_systems,
                "REVIEW_REQUIRED": True,
            })

        training_ok, training_reason = source_signal(group_sorted, "training", TRAINING_POSITIVE_TERMS, TRAINING_NEGATIVE_TERMS)
        training_criteria = questionnaire_signals(group_sorted, "LT")
        if training_ok:
            training_leads.append({
                "SME_ID": sme_id,
                "BUSINESS_NAME": values.get("business_name"),
                "SSM": values.get("ssm"),
                "PHONE": values.get("phone"),
                "EMAIL": values.get("email"),
                "STATE": values.get("state"),
                "SECTOR": values.get("sector"),
                "TRAINING_STATUS": values.get("training_status"),
                "DIGITALISATION": values.get("digitalisation"),
                "PROGRAMME": values.get("programme"),
                "LEAD_REASON": training_reason,
                "LEAD_TYPE": "LT",
                "LEAD_CRITERIA": training_criteria,
                "LEAD_SOURCE_PRIORITY": "ELSA",
                "SOURCE_SYSTEMS": source_systems,
                "REVIEW_REQUIRED": True,
            })

    return {
        "golden": {
            "UDX_VERSION": UDX_VERSION,
            "GENERATED_BY": "UDX SME Golden Record Engine",
            "GENERATED_AT": datetime.now().astimezone().isoformat(timespec="seconds"),
            "SOURCE_SUMMARY": source_meta,
            "MATCHING_RULES": MATCHING_RULES,
            "RECORD_COUNT": len(golden_records),
            "SME_BY_BUSINESS_SIZE": business_size_distribution(golden_records),
            "GOLDEN_RECORDS": golden_records,
        },
        "financing": {
            "UDX_VERSION": UDX_VERSION,
            "GENERATED_BY": "UDX Financing Potential Lead Engine",
            "GENERATED_AT": datetime.now().astimezone().isoformat(timespec="seconds"),
            "SOURCE_PRIORITY": "ELSA",
            "LEAD_COUNT": len(financing_leads),
            "DISCLAIMER": "Candidate lead list only. Validate financing need, eligibility, consent and current application status before outreach or decisioning.",
            "FINANCING_POTENTIAL_LEADS": financing_leads,
        },
        "training": {
            "UDX_VERSION": UDX_VERSION,
            "GENERATED_BY": "UDX Development Training Potential Engine",
            "GENERATED_AT": datetime.now().astimezone().isoformat(timespec="seconds"),
            "SOURCE_PRIORITY": "ELSA",
            "LEAD_COUNT": len(training_leads),
            "DISCLAIMER": "Candidate development/training list only. Validate current needs, prior participation and programme eligibility before referral.",
            "DEVELOPMENT_TRAINING_POTENTIAL": training_leads,
        },
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    all_records: List[Dict[str, Any]] = []
    source_meta: Dict[str, Any] = {}

    source_files = discover_source_files()
    print("Discovered input files:")
    for source, filename in source_files.items():
        print(f"  {source}: {filename}")

    for source, filename in source_files.items():
        df, metadata = read_source(source, filename)
        source_meta[source] = metadata
        all_records.extend(df.to_dict(orient="records"))

    outputs = build_outputs(all_records, source_meta)

    files = {
        "sme_golden_records.json": outputs["golden"],
        "financing_potential_leads.json": outputs["financing"],
        "development_training_potential.json": outputs["training"],
        "udx_run_summary.json": {
            "UDX_VERSION": UDX_VERSION,
            "GENERATED_AT": datetime.now().astimezone().isoformat(timespec="seconds"),
            "INPUT_DIRECTORY": str(INPUT_DIR),
            "OUTPUT_DIRECTORY": str(OUTPUT_DIR),
            "SOURCE_RECORDS_READ": sum(m["record_count"] for m in source_meta.values()),
            "SOURCE_SUMMARY": source_meta,
            "OUTPUT_COUNTS": {
                "GOLDEN_RECORDS": outputs["golden"]["RECORD_COUNT"],
                "SME_BY_BUSINESS_SIZE": outputs["golden"]["SME_BY_BUSINESS_SIZE"],
                "FINANCING_POTENTIAL_LEADS": outputs["financing"]["LEAD_COUNT"],
                "DEVELOPMENT_TRAINING_POTENTIAL": outputs["training"]["LEAD_COUNT"],
            },
            "NOTES": [
                "ELSA is preferred for mapped profile attributes when a value exists.",
                "Exact SSM match is the strongest entity resolution key.",
                "Conflicting non-empty SSM numbers are not merged based on name alone.",
                "LT/LF lead qualification applies the configured Malay questionnaire 0/1 rules before fallback keyword rules.",
                "Questionnaire criteria and source field/value are included in each lead's LEAD_CRITERIA array.",
                "Review SOURCE_SUMMARY unmapped fields and adjust ALIASES to match workbook headers.",
            ],
        },
    }

    for filename, payload in files.items():
        path = OUTPUT_DIR / filename
        with path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
        print(f"Created: {path}")

    print("\nUDX run complete")
    print(f"Source records read: {sum(m['record_count'] for m in source_meta.values())}")
    print(f"Golden Records: {outputs['golden']['RECORD_COUNT']}")
    print(f"Financing potential leads: {outputs['financing']['LEAD_COUNT']}")
    print(f"Development/training potential: {outputs['training']['LEAD_COUNT']}")
    print("\nCheck output/udx_run_summary.json for detected columns and unmapped fields.")


if __name__ == "__main__":
    main()
