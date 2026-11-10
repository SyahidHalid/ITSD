#!/usr/bin/env python3
"""
UDX SME Golden Record Engine v3
--------------------------------
Reads five Excel source files from ./input, uses ELSA as the primary source
for business/profile attributes, consolidates SMEs, and writes four JSON files
plus one consolidated Excel workbook (udx_outputs.xlsx).

Requirements:
    pip install pandas openpyxl rapidfuzz

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
from datetime import datetime, date, timedelta, timezone
from time import perf_counter
from pathlib import Path
from difflib import SequenceMatcher
try:
    from rapidfuzz.fuzz import ratio as _rapidfuzz_ratio
except ImportError:
    _rapidfuzz_ratio = None
from typing import Any, Dict, List, Optional, Tuple
from functools import lru_cache
from copy import copy as copy_style

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

# Confirmed source-specific SSM/Registration No. mappings. For sources marked
# None, the source is not expected to provide an SSM number; do not guess from
# another column or map a similarly named field accidentally.
SSM_SOURCE_COLUMNS = {
    "ELSA": "Nombor Pendaftaran Baru",
    "CBRS": "NO PENDAFTARAN SYARIKAT YANG DIDAFTARKAN (SSM/PBT)",
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
    "module": ["module", "program module", "programme module"],
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


def normalize_ssm(value: Any) -> Optional[str]:
    """Normalize an SSM/registration identifier for canonical output and matching.

    Excel numeric cells such as 201901234567.0 are cleaned, whitespace and
    formatting punctuation are removed, and letters are uppercased. The raw
    source value remains available under each record's RAW fields.
    """
    if is_blank(value):
        return None
    text = str(value).strip().upper()
    # Remove the common decimal suffix caused by Excel numeric formatting.
    text = re.sub(r"\.0+$", "", text)
    # SSM identifiers are matched consistently regardless of spaces, hyphens,
    # slashes or other display separators.
    normalized = re.sub(r"[^A-Z0-9]", "", text)
    return normalized or None


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
    """Fast normalized similarity. RapidFuzz is preferred; stdlib is fallback."""
    aa, bb = normalized_text(a), normalized_text(b)
    if not aa or not bb:
        return 0.0
    if aa == bb:
        return 1.0
    if _rapidfuzz_ratio is not None:
        return _rapidfuzz_ratio(aa, bb) / 100.0
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


def read_source(source: str, filename: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
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
        # SSM is mapped only using the confirmed source-specific column below.
        # Do not apply the generic SSM aliases across all source systems.
        if field == "ssm":
            continue
        found = first_matching_column(list(df.columns), aliases)
        if found is not None:
            column_map[field] = found

    configured_ssm_header = SSM_SOURCE_COLUMNS.get(source)
    if configured_ssm_header:
        # Match the configured header exactly after normalizing capitalization,
        # whitespace and punctuation, so minor Excel header formatting does not
        # break the mapping while unrelated columns are not selected.
        expected_header_key = header_key(configured_ssm_header)
        ssm_column = next(
            (col for col in df.columns if header_key(col) == expected_header_key),
            None,
        )
        if ssm_column is not None:
            column_map["ssm"] = ssm_column
        else:
            print(
                f"WARNING: Configured SSM column not found for {source}: "
                f"'{configured_ssm_header}'. SSM values for this source will be null."
            )

    # Convert the source DataFrame to dictionaries once. iterrows() creates a
    # Series for every row and is substantially slower for wide Excel exports.
    records: List[Dict[str, Any]] = []
    source_rows = df.to_dict(orient="records")
    # Keep original worksheet row numbers even when fully blank rows were dropped.
    original_indices = list(df.index)
    for row_idx, row in zip(original_indices, source_rows):
        row_number = int(row_idx) + 2
        raw = {str(k): clean_value(v) for k, v in row.items()}
        canonical = {}
        for field, col in column_map.items():
            value = clean_value(row.get(col))
            canonical[field] = normalize_ssm(value) if field == "ssm" else value
        canonical["ssm"] = canonical.get("ssm")
        canonical.setdefault("business_name", None)
        canonical.setdefault("phone", None)
        canonical.setdefault("email", None)
        canonical.setdefault("address", None)
        records.append({
            "source_system": source,
            "source_record_id": f"{source}-{row_number}",
            "source_row_number": row_number,
            "raw": raw,
            "canonical": canonical,
        })

    metadata = {
        "filename": filename,
        "sheet": sheet or str(pd.ExcelFile(path).sheet_names[0]),
        "record_count": len(records),
        "columns": list(df.columns),
        "mapped_fields": column_map,
        "ssm_source_column_configured": configured_ssm_header,
        "ssm_source_column_found": column_map.get("ssm"),
        "unmapped_canonical_fields": [f for f in ALIASES if f not in column_map],
    }
    return records, metadata


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
    ssm_a, ssm_b = normalize_ssm(ca.get("ssm")), normalize_ssm(cb.get("ssm"))
    if ssm_a and ssm_b:
        # SSM is the strongest identifier: exact match consolidates; conflict blocks merge.
        return ssm_a == ssm_b
    # When SSM is unavailable on either side, apply the agreed weighted score.
    return pair_match_score(a, b) >= float(MATCHING_RULES["MATCH_THRESHOLD"])


MATCH_REVIEW_CANDIDATES = []

def make_groups(records: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """Greedy entity resolution with indexed candidate generation.

    The original implementation compared each incoming record with every group
    and member, which approaches O(n^2). This version indexes prior records by
    exact SSM and company-name character bigrams. Since name-based consolidation
    requires a SequenceMatcher score >= 95%, viable fuzzy name candidates share
    character bigrams in normal business-name strings; exact SSM candidates are
    always included separately. Candidate groups are checked in their original
    creation order to preserve the previous greedy grouping behaviour.
    """
    global MATCH_REVIEW_CANDIDATES
    MATCH_REVIEW_CANDIDATES = []
    groups: List[List[Dict[str, Any]]] = []
    group_for_record: List[int] = []
    ssm_index: Dict[str, List[int]] = {}
    name_bigram_index: Dict[str, List[int]] = {}
    exact_name_index: Dict[str, List[int]] = {}
    phone_index: Dict[str, List[int]] = {}
    email_index: Dict[str, List[int]] = {}
    overloaded_grams = set()
    overloaded_phones = set()
    overloaded_emails = set()
    MAX_BIGRAM_POSTING = 200
    MAX_CONTACT_POSTING = 200

    def bigrams(text: str) -> set:
        if len(text) < 2:
            return set()
        return {text[i:i + 2] for i in range(len(text) - 1)}

    for record_idx, record in enumerate(records):
        canonical = record["canonical"]
        ssm = normalized_text(canonical.get("ssm"))
        name = normalized_text(canonical.get("business_name"))

        candidate_indices = set()
        if ssm:
            candidate_indices.update(ssm_index.get(ssm, ()))
        if name:
            candidate_indices.update(exact_name_index.get(name, ()))
            for gram in bigrams(name):
                if gram not in overloaded_grams:
                    candidate_indices.update(name_bigram_index.get(gram, ()))
        phone = normalize_phone(canonical.get("phone"))
        email = normalize_email(canonical.get("email"))
        if phone and phone not in overloaded_phones:
            candidate_indices.update(phone_index.get(phone, ()))
        if email and email not in overloaded_emails:
            candidate_indices.update(email_index.get(email, ()))

        # Preserve original semantics: test candidate groups by group creation
        # order and members within each group by source encounter order.
        candidates_by_group: Dict[int, List[int]] = {}
        for prior_idx in sorted(candidate_indices):
            group_idx = group_for_record[prior_idx]
            candidates_by_group.setdefault(group_idx, []).append(prior_idx)

        placed_group: Optional[int] = None
        for group_idx in sorted(candidates_by_group):
            for prior_idx in candidates_by_group[group_idx]:
                prior = records[prior_idx]
                ssm_new, ssm_old = normalize_ssm(canonical.get("ssm")), normalize_ssm(prior["canonical"].get("ssm"))
                if ssm_new and ssm_old and ssm_new != ssm_old:
                    continue
                candidate_score = pair_match_score(record, prior)
                if are_same_entity(record, prior):
                    placed_group = group_idx
                    break
                if float(MATCHING_RULES["REVIEW_THRESHOLD"]) <= candidate_score < float(MATCHING_RULES["MATCH_THRESHOLD"]):
                    MATCH_REVIEW_CANDIDATES.append({
                        "RECORD_1": record["source_record_id"], "SOURCE_1": record["source_system"],
                        "RECORD_2": prior["source_record_id"], "SOURCE_2": prior["source_system"],
                        "MATCH_SCORE": candidate_score, "DECISION": "MANUAL_REVIEW_REQUIRED"
                    })
            if placed_group is not None:
                break

        if placed_group is None:
            placed_group = len(groups)
            groups.append([record])
        else:
            groups[placed_group].append(record)
        group_for_record.append(placed_group)

        if ssm:
            ssm_index.setdefault(ssm, []).append(record_idx)
        if name:
            exact_name_index.setdefault(name, []).append(record_idx)
            for gram in bigrams(name):
                if gram in overloaded_grams:
                    continue
                posting = name_bigram_index.setdefault(gram, [])
                posting.append(record_idx)
                if len(posting) > MAX_BIGRAM_POSTING:
                    # Common fragments (e.g. SDN BHD) create huge candidate
                    # sets but have little discriminating value. Keep exact
                    # name, contact and SSM blocks active for these fragments.
                    overloaded_grams.add(gram)
                    name_bigram_index.pop(gram, None)
        if phone and phone not in overloaded_phones:
            posting = phone_index.setdefault(phone, [])
            posting.append(record_idx)
            if len(posting) > MAX_CONTACT_POSTING:
                overloaded_phones.add(phone)
                phone_index.pop(phone, None)
        if email and email not in overloaded_emails:
            posting = email_index.setdefault(email, [])
            posting.append(record_idx)
            if len(posting) > MAX_CONTACT_POSTING:
                overloaded_emails.add(email)
                email_index.pop(email, None)

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


@lru_cache(maxsize=8192)
def _questionnaire_header_matches_cached(header_text: str, aliases_key: Tuple[str, ...]) -> bool:
    """Cached normalized header comparison; aliases are immutable cache keys."""
    header = header_text
    aliases = list(aliases_key)
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


def questionnaire_header_matches(header: Any, aliases: List[str]) -> bool:
    """Match question columns; cache repeated header/alias comparisons."""
    return _questionnaire_header_matches_cached(str(header), tuple(aliases))


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



# ---------------------------------------------------------------------------
# UDX CONFIGURATION-DRIVEN GOLDEN RECORD + LEAD ENGINE
# ---------------------------------------------------------------------------

MYT = timezone(timedelta(hours=8))
CONFIG_DIR = BASE_DIR / "config"
EXISTING_GOLDEN_CANDIDATES = (OUTPUT_DIR / "sme_golden_records.json", INPUT_DIR / "sme_golden_records.json")

DEFAULT_MATCHING_CONFIG = MATCHING_RULES
DEFAULT_FINANCING_CONFIG = {
    "SCORING_VERSION": "1.0",
    "ELSA_ASSESSMENT_SHARE": 0.35,
    "RAW_DATA_SHARE": 0.65,
    "WEIGHTS": {"FINANCING_DEMAND": 35, "GROWTH_POTENTIAL": 25, "FINANCIAL_READINESS": 25, "SUSTAINABILITY": 15},
    "TIERS": {"HIGH": 80, "MEDIUM": 60, "EMERGING": 40},
    "REQUIRE_ACTIVE_STATUS": True,
    "REQUIRE_SME_CLASSIFICATION": False,
    "POINTS": {
        "MARKET_EXPANSION": 10, "CAPITAL_INVESTMENT": 10, "NEW_PRODUCT_DEVELOPMENT": 10,
        "PREVIOUS_FINANCING_ATTEMPT": 5, "BUSINESS_PERFORMANCE_IMPROVING": 5, "PRODUCT_GROWTH": 5,
        "INDUSTRY_GROWTH_STAGE": 5, "PRODUCT_GROWTH_STAGE": 5, "REVENUE_DATA_AVAILABLE": 5,
        "REGISTERED_BUSINESS_BANK_ACCOUNT": 5, "AUDITED_BUSINESS_ACCOUNTS": 5, "SST_REGISTERED": 3,
        "FINANCIAL_LIFECYCLE": 6, "FINANCIAL_SYSTEM_LIFECYCLE": 6,
        "OPERATING_EXPERIENCE_OVER_5_YEARS": 5, "ACTIVE_BUSINESS": 3,
        "INDUSTRY_PERFORMANCE_GOOD": 3, "NO_LATE_PAYMENT_PROBLEM": 2, "WORKFORCE_PRESENT": 2
    }
}
DEFAULT_INTERVENTION_CONFIG = {
    "SCORING_VERSION": "1.0",
    "ELSA_ASSESSMENT_SHARE": 0.50,
    "RAW_DATA_SHARE": 0.50,
    "TIERS": {"HIGH": 80, "MEDIUM": 60, "EMERGING": 40},
    "RULE_POINTS": {
        "WORKFORCE_SKILLS_REQUESTED": 25, "NO_WORKPLACE_TRAINING": 10, "NO_EMPLOYEE_HANDBOOK_SOP": 8,
        "NO_WRITTEN_EMPLOYMENT_CONTRACT": 6, "NO_DOCUMENTED_PERFORMANCE_REVIEW": 6, "NO_ORGANISATION_CHART": 5,
        "NO_DOCUMENTED_BUSINESS_PLAN": 5, "NO_INVENTORY_SYSTEM": 12, "NO_PAYROLL_SYSTEM": 8,
        "NO_SALES_INVOICING_SYSTEM": 10, "NO_POS_SYSTEM": 8, "NO_ONLINE_MARKETING": 5,
        "NO_WEBSITE": 5, "NO_SOCIAL_MEDIA": 5, "NO_THIRD_PARTY_PLATFORM": 5, "NO_DIGITAL_PAYMENT": 15,
        "MARKET_EXPANSION_REQUESTED": 35, "PRODUCT_SERVICE_GROWTH": 20, "INDUSTRY_GROWTH_POTENTIAL": 20,
        "LEADERSHIP_DEVELOPMENT_REQUESTED": 40, "SUCCESSION_PLANNING_GAP": 30,
        "NO_PERFORMANCE_REVIEW": 25, "NO_AUDITED_ACCOUNTS": 30, "NO_BUSINESS_BANK_ACCOUNT": 25,
        "FINANCIAL_SYSTEM_GAP": 25, "SST_REGISTRATION_NOT_PRESENT": 20
    },
}


def now_myt() -> datetime:
    return datetime.now(MYT)


def fmt_dt(value=None) -> str:
    value = value or now_myt()
    if isinstance(value, str):
        return value[:19].replace("T", " ")
    if isinstance(value, pd.Timestamp):
        value = value.to_pydatetime()
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=MYT)
        return value.astimezone(MYT).strftime("%Y-%m-%d %H:%M:%S")
    return now_myt().strftime("%Y-%m-%d %H:%M:%S")


def write_default_config(path: Path, config: dict) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Created default configuration: {path}")
        return config
    with path.open("r", encoding="utf-8") as f:
        loaded = json.load(f)
    return loaded


def load_configs():
    matching = write_default_config(CONFIG_DIR / "golden_record_rules.json", DEFAULT_MATCHING_CONFIG)
    financing = write_default_config(CONFIG_DIR / "financing_scoring.json", DEFAULT_FINANCING_CONFIG)
    intervention = write_default_config(CONFIG_DIR / "intervention_scoring.json", DEFAULT_INTERVENTION_CONFIG)
    MATCHING_RULES.update(matching)
    return matching, financing, intervention


def find_existing_golden_file():
    for path in EXISTING_GOLDEN_CANDIDATES:
        if path.exists():
            return path
    return None


def load_existing_golden():
    path = find_existing_golden_file()
    if not path:
        print("No existing Golden Record JSON found; new SME_IDs will be generated for all confirmed entities.")
        return [], None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data.get("GOLDEN_RECORDS", data.get("RECORDS", [])) if isinstance(data, dict) else data
        rows = rows if isinstance(rows, list) else []
        print(f"Existing Golden Records loaded: {len(rows):,} from {path}")
        return rows, path
    except Exception as exc:
        raise ValueError(f"Unable to read existing Golden Record JSON {path}: {exc}")


def norm_sme_name(v):
    return normalized_text(v)


def build_existing_record_indexes(existing_records):
    """Build blocking indexes once; avoids O(new_groups x historical_records)."""
    indexes = {"ssm": {}, "phone": {}, "email": {}, "name_prefix": {}}
    overloaded_name_prefixes = set()
    MAX_EXISTING_NAME_BUCKET = 200
    for old in existing_records:
        old_id = old.get("SME_ID")
        if not old_id:
            continue
        ssm = normalize_ssm(old.get("SSM") or old.get("ssm") or old.get("SSM_NEW_NO") or old.get("SSM_OLD_NO"))
        phone = normalize_phone(old.get("PHONE") or old.get("phone"))
        email = normalize_email(old.get("EMAIL") or old.get("email"))
        name = norm_sme_name(old.get("BUSINESS_NAME") or old.get("business_name") or old.get("COMPANY_NAME"))
        if ssm:
            indexes["ssm"].setdefault(ssm, []).append(old)
        if phone:
            indexes["phone"].setdefault(phone, []).append(old)
        if email:
            indexes["email"].setdefault(email, []).append(old)
        if name:
            prefix = name[:3]
            if prefix not in overloaded_name_prefixes:
                bucket = indexes["name_prefix"].setdefault(prefix, [])
                bucket.append(old)
                if len(bucket) > MAX_EXISTING_NAME_BUCKET:
                    overloaded_name_prefixes.add(prefix)
                    indexes["name_prefix"].pop(prefix, None)
    return indexes


def existing_id_for_group(group, existing_records, indexes=None):
    """Reuse an existing SME_ID on a strong, non-conflicting identity match."""
    if indexes is None:
        indexes = build_existing_record_indexes(existing_records)
    current = group[0]["canonical"]
    c_ssm = normalize_ssm(current.get("ssm"))
    if c_ssm:
        for old in indexes["ssm"].get(c_ssm, ()):
            if old.get("SME_ID"):
                return str(old["SME_ID"])

    phone = normalize_phone(current.get("phone"))
    email = normalize_email(current.get("email"))
    name = norm_sme_name(current.get("business_name"))
    candidates = {}
    if phone:
        for old in indexes["phone"].get(phone, ()):
            candidates[id(old)] = old
    if email:
        for old in indexes["email"].get(email, ()):
            candidates[id(old)] = old
    if name:
        for old in indexes["name_prefix"].get(name[:3], ()):
            candidates[id(old)] = old

    best = None
    for old in candidates.values():
        old_id = old.get("SME_ID")
        if not old_id:
            continue
        o_ssm = normalize_ssm(old.get("SSM") or old.get("ssm") or old.get("SSM_NEW_NO") or old.get("SSM_OLD_NO"))
        # A valid conflicting SSM must never be auto-reused.
        if c_ssm and o_ssm and c_ssm != o_ssm:
            continue
        name_score = similarity(current.get("business_name"), old.get("BUSINESS_NAME") or old.get("business_name") or old.get("COMPANY_NAME"))
        old_phone = normalize_phone(old.get("PHONE") or old.get("phone"))
        old_email = normalize_email(old.get("EMAIL") or old.get("email"))
        phone_match = bool(phone and phone == old_phone)
        email_match = bool(email and email == old_email)
        address_score = similarity(current.get("address"), old.get("ADDRESS") or old.get("address") or old.get("BUSINESS_ADDRESS"))
        if name_score >= 0.97 and (phone_match or email_match or address_score >= 0.90):
            candidate = (name_score + (0.02 if phone_match else 0) + (0.02 if email_match else 0), str(old_id))
            if best is None or candidate[0] > best[0]:
                best = candidate
    return best[1] if best else None


def parse_module(value):
    """Return clean unique module tags; missing is represented by literal NA."""
    if is_blank(value):
        return []
    if isinstance(value, (list, tuple, set)):
        vals = list(value)
    else:
        text = str(value).strip()
        try:
            parsed = json.loads(text)
            vals = parsed if isinstance(parsed, list) else [parsed]
        except Exception:
            # Handle simple comma/semicolon-delimited exports.
            vals = re.split(r"[,;|]", text.strip("[]"))
    out, seen = [], set()
    for item in vals:
        if is_blank(item):
            continue
        tag = str(item).strip().strip("'\"").upper()
        if tag and tag not in seen and tag != "NA":
            seen.add(tag)
            out.append(tag)
    return out


def get_module_tags(group):
    tags = []
    for rec in group:
        raw = rec.get("raw", {})
        # Exact MODULE header preferred; alias-mapped canonical value as fallback.
        value = None
        for header, raw_value in raw.items():
            if header_key(header) == "module":
                value = raw_value
                break
        if value is None:
            value = rec.get("canonical", {}).get("module")
        tags.extend(parse_module(value))
    # Stable ordering follows source encounter order; deduplicate.
    unique = []
    for tag in tags:
        if tag not in unique:
            unique.append(tag)
    return unique if unique else "NA"


_RAW_HEADER_CACHE = {}

def _resolve_raw_header(headers, aliases):
    cache_key = (tuple(headers), tuple(str(a) for a in aliases))
    cached = _RAW_HEADER_CACHE.get(cache_key, ...)
    if cached is not ...:
        return cached
    found = None
    for header in headers:
        if questionnaire_header_matches(header, aliases):
            found = header
            break
    # Bound cache growth for files with many different header variants.
    if len(_RAW_HEADER_CACHE) > 20000:
        _RAW_HEADER_CACHE.clear()
    _RAW_HEADER_CACHE[cache_key] = found
    return found

def raw_field(group, aliases, prefer_elsa=True):
    # Groups are already ELSA-first when built by build_outputs; avoid sorting
    # the same rows repeatedly for every scoring indicator.
    ordered = group
    if prefer_elsa and group and group[0].get("source_system") != "ELSA":
        ordered = sorted(group, key=lambda r: (r.get("source_system") != "ELSA", r.get("source_system", "")))
    for rec in ordered:
        raw = rec.get("raw") or {}
        header = _resolve_raw_header(raw.keys(), aliases)
        if header is not None:
            value = raw.get(header)
            if not is_blank(value):
                return value, rec.get("source_system"), header
    return None, None, None


def yes_no(value):
    flag = numeric_flag(value)
    if flag is not None:
        return flag == 1
    if is_blank(value):
        return None
    text = str(value).strip().lower()
    if text in {"yes", "ya", "y", "true", "ada", "semakin baik"}:
        return True
    if text in {"no", "tidak", "n", "false", "tiada", "tiada masalah"}:
        return False
    return None


def stage_factor(value):
    if is_blank(value): return None
    t = str(value).strip().upper()
    return {"TAKEOFF": 1.0, "MATURITY": 1.0, "PRE-TAKEOFF": 0.6, "STAGNATION": 0.3, "RENEWAL": 0.5}.get(t)


def score_tier(score, tiers):
    if score >= float(tiers.get("HIGH", 80)): return "HIGH"
    if score >= float(tiers.get("MEDIUM", 60)): return "MEDIUM"
    if score >= float(tiers.get("EMERGING", 40)): return "EMERGING"
    return "LOW"


def assessment_priority_score(group, prefixes):
    """Normalise existing ELSA priority/tier/lifecycle assessment to 0-100."""
    vals = []
    for prefix in prefixes:
        priority, _, _ = raw_field(group, [f"{prefix}_PRIORITY"])
        tier, _, _ = raw_field(group, [f"{prefix}_TIER"])
        desired, _, _ = raw_field(group, [f"{prefix}_DESIRED_SCORE"])
        if str(priority).strip().upper() == "PRIORITY": vals.append(100)
        elif not is_blank(tier):
            t = str(tier).lower()
            vals.append(85 if "tier 3" in t else 65 if "tier 2" in t else 40 if "tier 1" in t else 50)
        else:
            factor = stage_factor(desired)
            if factor is not None: vals.append(factor * 100)
    return round(sum(vals) / len(vals), 2) if vals else None


def capped_points(condition, points):
    return float(points) if condition is True else 0.0


def financing_score(group, golden, config):
    reasons, breakdown = [], {}
    points = config.get("POINTS", DEFAULT_FINANCING_CONFIG["POINTS"])
    # Demand (35): explicit questionnaire intentions are strongest.
    demand = 0.0
    criteria = [
        ("Meningkatkan perolehan dengan meneroka pasaran baru", ["Meningkatkan perolehan dengan meneroka pasaran baru", "Meningkatkan perolehan dengan meneroka pasaran baharu"], points.get("MARKET_EXPANSION",10), "MARKET_EXPANSION"),
        ("Pelaburan modal", ["Pelaburan modal"], points.get("CAPITAL_INVESTMENT",10), "CAPITAL_INVESTMENT"),
        ("Membangunkan dan melancarkan produk/perkhidmatan baru", ["Membangunkan dan melancarkan produk perkhidmatan baru", "Membangunkan dan melancarkan produk perkhidmatan baharu"], points.get("NEW_PRODUCT_DEVELOPMENT",10), "NEW_PRODUCT_DEVELOPMENT"),
        ("Pernah mencuba mendapatkan pembiayaan", ["Adakah anda pernah mencuba mendapatkan pembiayaan untuk perniagaan anda sejak dua tahun kebelakangan ini"], points.get("PREVIOUS_FINANCING_ATTEMPT",5), "PREVIOUS_FINANCING_ATTEMPT"),
    ]
    for label, aliases, pts, code in criteria:
        val, _, _ = raw_field(group, aliases)
        if yes_no(val) is True:
            demand += pts; reasons.append(code)
    breakdown["FINANCING_DEMAND"] = min(35, demand)

    growth = 0.0
    val, _, _ = raw_field(group, ["Bagaimana anda menilai prestasi perniagaan anda sepanjang tahun"])
    if val and "baik" in str(val).lower(): growth += points.get("BUSINESS_PERFORMANCE_IMPROVING",5); reasons.append("BUSINESS_PERFORMANCE_IMPROVING")
    val, _, _ = raw_field(group, ["Adakah jumlah produk perkhidmatan anda meningkat kekal sama atau menurun dalam dua tahun terakhir"])
    if val and "meningkat" in str(val).lower(): growth += points.get("PRODUCT_GROWTH",5); reasons.append("PRODUCT_GROWTH")
    for field_alias, pts, code in [("Potensi Pertumbuhan Industri Skor",points.get("INDUSTRY_GROWTH_STAGE",5),"INDUSTRY_GROWTH_STAGE"),("Produk dan Perkhidmatan Skor",points.get("PRODUCT_GROWTH_STAGE",5),"PRODUCT_GROWTH_STAGE")]:
        val, _, _ = raw_field(group, [field_alias])
        factor = stage_factor(val)
        if factor is not None: growth += pts * factor
        if factor and factor >= .6: reasons.append(code)
    revenue = golden.get("ANNUAL_REVENUE")
    if not is_blank(revenue): growth += points.get("REVENUE_DATA_AVAILABLE",5); reasons.append("REVENUE_DATA_AVAILABLE")
    breakdown["GROWTH_POTENTIAL"] = min(25, growth)

    readiness = 0.0
    for aliases, pts, code in [
        (["Adakah anda mempunyai akaun bank berdaftar untuk syarikat anda"],points.get("REGISTERED_BUSINESS_BANK_ACCOUNT",5),"REGISTERED_BUSINESS_BANK_ACCOUNT"),
        (["Adakah anda mempunyai akaun perniagaan yang diaudit"],points.get("AUDITED_BUSINESS_ACCOUNTS",5),"AUDITED_BUSINESS_ACCOUNTS"),
        (["Adakah anda berdaftar dengan SST"],points.get("SST_REGISTERED",3),"SST_REGISTERED"),
    ]:
        val, _, _ = raw_field(group, aliases)
        if yes_no(val) is True: readiness += points.get(code,pts); reasons.append(code)
    for aliases, pts, code in [(["Kewangan Skor"],points.get("FINANCIAL_LIFECYCLE",6),"FINANCIAL_LIFECYCLE"),(["Sistem Kewangan Skor"],points.get("FINANCIAL_SYSTEM_LIFECYCLE",6),"FINANCIAL_SYSTEM_LIFECYCLE")]:
        val, _, _ = raw_field(group, aliases); factor = stage_factor(val)
        if factor is not None: readiness += pts * factor
        if factor and factor >= .6: reasons.append(code)
    breakdown["FINANCIAL_READINESS"] = min(25, readiness)

    sustainability = 0.0
    val, _, _ = raw_field(group, ["Sejarah Pengalaman Operasi"])
    if val and ("> 5" in str(val) or "lebih 5" in str(val).lower()): sustainability += points.get("OPERATING_EXPERIENCE_OVER_5_YEARS",5); reasons.append("OPERATING_EXPERIENCE_OVER_5_YEARS")
    if str(golden.get("BUSINESS_STATUS", "")).strip().upper() == "ACTIVE": sustainability += points.get("ACTIVE_BUSINESS",3)
    val, _, _ = raw_field(group, ["Bagaimana anda menilai prestasi industri anda sepanjang tahun"])
    if val and "baik" in str(val).lower(): sustainability += points.get("INDUSTRY_PERFORMANCE_GOOD",3)
    val, _, _ = raw_field(group, ["Adakah anda mempunyai masalah dengan pelanggan yang membuat pembayaran lebih dari tempoh yang anda kehendaki dalam perniagaan anda"])
    if yes_no(val) is False: sustainability += points.get("NO_LATE_PAYMENT_PROBLEM",2)
    employees, _, _ = raw_field(group, ["Berapakah jumlah pekerja yang bekerja secara sepenuh masa", "Berapakah jumlah pekerja dalam perniagaan anda"])
    try:
        if float(re.sub(r"[^0-9.]", "", str(employees))) > 0: sustainability += points.get("WORKFORCE_PRESENT",2)
    except Exception: pass
    breakdown["SUSTAINABILITY"] = min(15, sustainability)

    # Rescale the four dimension subtotals to the configurable dimension weights.
    configured_weights = config.get("WEIGHTS", DEFAULT_FINANCING_CONFIG["WEIGHTS"])
    base_caps = {"FINANCING_DEMAND": 35, "GROWTH_POTENTIAL": 25, "FINANCIAL_READINESS": 25, "SUSTAINABILITY": 15}
    for dimension, base_cap in base_caps.items():
        configured_cap = float(configured_weights.get(dimension, base_cap))
        breakdown[dimension] = round((breakdown[dimension] / base_cap) * configured_cap, 2) if base_cap else 0.0
    raw_total = sum(breakdown.values())
    assessment = assessment_priority_score(group, ["FR", "BR", "IG"])
    share_e = float(config.get("ELSA_ASSESSMENT_SHARE", .35)); share_r = float(config.get("RAW_DATA_SHARE", .65))
    if assessment is None: final = raw_total
    else: final = raw_total * share_r + assessment * share_e
    final = round(max(0, min(100, final)), 2)
    status = str(golden.get("BUSINESS_STATUS") or "").upper()
    category = str(golden.get("BUSINESS_SIZE") or "").lower()
    eligible = True
    exclusions = []
    if config.get("REQUIRE_ACTIVE_STATUS", True) and status not in {"ACTIVE", "AKTIF"}:
        eligible = False; exclusions.append("BUSINESS_STATUS_NOT_CONFIRMED" if not status else "BUSINESS_NOT_ACTIVE")
    if config.get("REQUIRE_SME_CLASSIFICATION", False) and (not category or category in {"large", "unclassified"}):
        eligible = False; exclusions.append("SME_CLASSIFICATION_NOT_CONFIRMED")
    return final, breakdown, sorted(set(reasons)), assessment, raw_total, eligible, exclusions


def intervention_scores(group, golden, config):
    outputs = []
    tiers = config.get("TIERS", DEFAULT_INTERVENTION_CONFIG["TIERS"])
    # Helper to award points for explicit Yes/No indicators.
    def flag(aliases):
        v, _, _ = raw_field(group, aliases)
        return yes_no(v)
    def stage(prefixes): return assessment_priority_score(group, prefixes)
    specs = {
      "TRAINING": {"assessment": ["LC","PR"], "signals": [
        ("Meningkatkan kemahiran tenaga kerja", ["Meningkatkan kemahiran tenaga kerja"], 25, True, "WORKFORCE_SKILLS_REQUESTED"),
        ("No employee training at workplace", ["Latihan di Tempat Kerja"], 10, False, "NO_WORKPLACE_TRAINING"),
        ("No employee handbook/SOP", ["Buku Panduan Pekerja Prosedur Operasi Standard"], 8, False, "NO_EMPLOYEE_HANDBOOK_SOP"),
        ("No written employment contract", ["Kontrak Pekerjaan Bertulis"], 6, False, "NO_WRITTEN_EMPLOYMENT_CONTRACT"),
        ("No documented performance review", ["Adakah anda mempunyai tinjauan deskripsi pekerjaan prestasi kerja kakitangan yang didokumentasikan"], 6, False, "NO_DOCUMENTED_PERFORMANCE_REVIEW"),
        ("No organisation chart", ["Adakah anda mempunyai carta struktur organisasi"], 5, False, "NO_ORGANISATION_CHART"),
        ("No documented business plan", ["Adakah anda mempunyai Perancangan Perniagaan yang didokumentasikan untuk syarikat anda"], 5, False, "NO_DOCUMENTED_BUSINESS_PLAN")], "cap": 100},
      "DIGITALISATION": {"assessment": ["SR"], "signals": [
        ("No inventory system", ["Pemantauan Stok Pengimbasan Kod Bar Pengurusan Inventori"], 12, False, "NO_INVENTORY_SYSTEM"),
        ("No payroll system", ["Pengurusan Penggajian Pekerja"], 8, False, "NO_PAYROLL_SYSTEM"),
        ("No sales/invoicing system", ["Laporan Jualan Invois"], 10, False, "NO_SALES_INVOICING_SYSTEM"),
        ("No POS system", ["Sistem Pusat Jualan"], 8, False, "NO_POS_SYSTEM"),
        ("No online marketing", ["Pemasaran Dalam Talian"], 5, False, "NO_ONLINE_MARKETING"),
        ("No website", ["Laman web rasmi"], 5, False, "NO_WEBSITE"),
        ("No social media presence", ["Melalui Sosial Media"], 5, False, "NO_SOCIAL_MEDIA"),
        ("No third-party platform", ["Melalui Platform Pihak Ketiga"], 5, False, "NO_THIRD_PARTY_PLATFORM"),
        ("No digital payments", ["Pembayaran Digital termasuk Kad Kredit Kad Debit Grab Pay"], 15, False, "NO_DIGITAL_PAYMENT")], "cap": 100},
      "BUSINESS_DEVELOPMENT": {"assessment": ["BR","IG"], "signals": [
        ("Market expansion requested", ["Meningkatkan perolehan dengan meneroka pasaran baru"], 35, True, "MARKET_EXPANSION_REQUESTED"),
        ("No documented business plan", ["Adakah anda mempunyai Perancangan Perniagaan yang didokumentasikan untuk syarikat anda"], 25, False, "NO_DOCUMENTED_BUSINESS_PLAN"),
        ("Product/service growth", ["Adakah jumlah produk perkhidmatan anda meningkat kekal sama atau menurun dalam dua tahun terakhir"], 20, "INCREASE", "PRODUCT_SERVICE_GROWTH"),
        ("Industry growth potential", ["Potensi Pertumbuhan Industri Skor"], 20, "STAGE", "INDUSTRY_GROWTH_POTENTIAL")], "cap": 100},
      "LEADERSHIP_CAPACITY": {"assessment": ["LC"], "signals": [
        ("Leadership capability requested", ["Meningkatkan keupayaan kepimpinan pengurus"], 40, True, "LEADERSHIP_DEVELOPMENT_REQUESTED"),
        ("No organisation chart", ["Adakah anda mempunyai carta struktur organisasi"], 30, False, "NO_ORGANISATION_CHART"),
        ("No documented succession/transition plan", ["Pelan Peralihan Kepimpinan Skor"], 30, "STAGE_LOW", "SUCCESSION_PLANNING_GAP")], "cap": 100},
      "HUMAN_RESOURCES": {"assessment": ["PR"], "signals": [
        ("No workplace training", ["Latihan di Tempat Kerja"], 40, False, "NO_WORKPLACE_TRAINING"),
        ("No handbook/SOP or contracts", ["Buku Panduan Pekerja Prosedur Operasi Standard"], 20, False, "NO_EMPLOYEE_HANDBOOK_SOP"),
        ("No written employment contract", ["Kontrak Pekerjaan Bertulis"], 15, False, "NO_WRITTEN_EMPLOYMENT_CONTRACT"),
        ("No performance review", ["Adakah anda mempunyai tinjauan deskripsi pekerjaan prestasi kerja kakitangan yang didokumentasikan"], 25, False, "NO_PERFORMANCE_REVIEW")], "cap": 100},
      "FINANCIAL_MANAGEMENT": {"assessment": ["FR"], "signals": [
        ("No audited business accounts", ["Adakah anda mempunyai akaun perniagaan yang diaudit"], 30, False, "NO_AUDITED_ACCOUNTS"),
        ("No registered business bank account", ["Adakah anda mempunyai akaun bank berdaftar untuk syarikat anda"], 25, False, "NO_BUSINESS_BANK_ACCOUNT"),
        ("No financial system", ["Sistem Kewangan Skor"], 25, "STAGE_LOW", "FINANCIAL_SYSTEM_GAP"),
        ("No SST registration", ["Adakah anda berdaftar dengan SST"], 20, False, "SST_REGISTRATION_NOT_PRESENT")], "cap": 100}
    }
    for kind, spec in specs.items():
        raw_score, reasons = 0.0, []
        rule_points = config.get("RULE_POINTS", DEFAULT_INTERVENTION_CONFIG["RULE_POINTS"])
        effective_points = []
        for label, aliases, pts, expected, code in spec["signals"]:
            pts = float(rule_points.get(code, pts))
            effective_points.append(pts)
            value, _, _ = raw_field(group, aliases)
            qualifies = False
            if expected is True: qualifies = yes_no(value) is True
            elif expected is False: qualifies = yes_no(value) is False
            elif expected == "INCREASE": qualifies = "meningkat" in str(value).lower() if value is not None else False
            elif expected == "STAGE_LOW":
                factor = stage_factor(value); qualifies = factor is not None and factor <= .5
            elif expected == "STAGE":
                factor = stage_factor(value); qualifies = factor is not None and factor >= .6
            if qualifies:
                raw_score += pts; reasons.append(code)
        max_points = sum(effective_points) or 1.0
        raw_score = min(100, (raw_score / max_points) * 100.0)
        assessment = stage(spec["assessment"])
        share_e = float(config.get("ELSA_ASSESSMENT_SHARE", .5)); share_r = float(config.get("RAW_DATA_SHARE", .5))
        score = raw_score if assessment is None else raw_score * share_r + assessment * share_e
        score = round(max(0, min(100, score)), 2)
        tier = score_tier(score, tiers)
        # Do not create empty/no-signal lead records. Assessment priority can independently qualify.
        if raw_score > 0 or (assessment is not None and assessment >= float(tiers.get("MEDIUM",60))):
            outputs.append({
                "LEAD_ID": f"{kind[:2]}-{golden['SME_ID']}",
                "SME_ID": golden["SME_ID"],
                "COMPANY_NAME": golden.get("BUSINESS_NAME"),
                "INTERVENTION_TYPE": kind,
                "SCORE": score,
                "TIER": tier,
                "SCORE_BREAKDOWN": {"RAW_DATA_SCORE": round(raw_score,2), "ELSA_ASSESSMENT_SCORE": assessment, "RAW_DATA_SHARE": share_r, "ELSA_ASSESSMENT_SHARE": share_e},
                "REASONS": sorted(set(reasons)) or ["ELSA_ASSESSMENT_PRIORITY"],
                "READINESS": "TO_BE_ASSESSED",
                "SOURCE_SYSTEMS": golden.get("SOURCE_SYSTEMS", []),
                "REVIEW_REQUIRED": True
            })
    return outputs


def confirmed_new_entity(group):
    """Require a registration number, or business name plus corroborating contact/location."""
    for record in group:
        c = record.get("canonical", {})
        if normalize_ssm(c.get("ssm")):
            return True
        name = c.get("business_name")
        corroboration = c.get("phone") or c.get("email") or c.get("address")
        if not is_blank(name) and not is_blank(corroboration):
            return True
    return False


def build_outputs(all_records, source_meta, existing_records, financing_config, intervention_config):
    groups = make_groups(all_records)
    used_ids = {str(r.get("SME_ID")) for r in existing_records if r.get("SME_ID")}
    golden_records, group_by_sme_id = [], {}
    old_by_id = {str(r.get("SME_ID")): r for r in existing_records if r.get("SME_ID")}
    existing_indexes = build_existing_record_indexes(existing_records)
    profile_fields = ["business_name", "ssm", "phone", "email", "address", "postcode", "city", "state", "sector", "business_size", "business_status", "annual_revenue", "financing_status", "financing_need", "training_status", "digitalisation", "entrepreneur_id", "contact_person", "programme"]
    reused_count, new_count, changed_count = 0, 0, 0
    assigned_ids = set()

    # PASS 1: Build and write-ready all Golden Records before lead scoring starts.
    for group_index, group in enumerate(groups):
        group_sorted = sorted(group, key=lambda r: (r["source_system"] != "ELSA", r["source_system"]))
        values, provenance = {}, {}
        for field in profile_fields:
            value, source = pick_value(group_sorted, field)
            values[field] = value
            provenance[field] = {"SOURCE_SYSTEM": source, "CANONICAL_FIELD": field} if source else None
        values["business_size"] = normalize_business_size(values.get("business_size"))
        confidence = 100.0 if len(group) == 1 else 0.0
        if len(group) > 1:
            for i in range(len(group) - 1):
                for j in range(i + 1, len(group)):
                    score = pair_match_score(group[i], group[j])
                    if score > confidence:
                        confidence = score
                    if confidence >= 100.0:
                        break
                if confidence >= 100.0:
                    break
        reused_id = existing_id_for_group(group_sorted, existing_records, existing_indexes)
        identity_confirmed = bool(reused_id) or confirmed_new_entity(group_sorted)
        if reused_id and reused_id not in assigned_ids:
            sme_id = reused_id
            reused_count += 1
        else:
            # SME_ID is the Golden Record primary key and must never be null.
            # For sparse records, make_sme_id falls back to the source record IDs.
            # Unknown/unmapped state is represented by the MY state-code segment.
            sme_id = make_sme_id(group_sorted, used_ids)
            new_count += 1
        assigned_ids.add(sme_id)
        exact_ssm_match = any(
            normalize_ssm(group[i]["canonical"].get("ssm"))
            and normalize_ssm(group[i]["canonical"].get("ssm")) == normalize_ssm(group[j]["canonical"].get("ssm"))
            for i in range(len(group)) for j in range(i + 1, len(group))
        )
        match_status = (
            "IDENTITY_REVIEW_REQUIRED" if not identity_confirmed
            else ("SINGLE_SOURCE" if len(group) == 1
                  else ("AUTO_MATCH" if exact_ssm_match or confidence >= MATCHING_RULES["MATCH_THRESHOLD"] else "REVIEW"))
        )
        if sme_id:
            used_ids.add(sme_id)
        source_systems = sorted(set(r["source_system"] for r in group))
        module_tags = get_module_tags(group_sorted)
        source_records = [{"SOURCE_SYSTEM": r["source_system"], "SOURCE_RECORD_ID": r["source_record_id"], "SOURCE_ROW_NUMBER": r["source_row_number"]} for r in group]
        rec = {
            "SME_ID": sme_id, "BUSINESS_NAME": values.get("business_name"), "SSM": values.get("ssm"),
            "PHONE": values.get("phone"), "EMAIL": values.get("email"), "ADDRESS": values.get("address"),
            "POSTCODE": values.get("postcode"), "CITY": values.get("city"), "STATE": values.get("state"),
            "SECTOR": values.get("sector"), "BUSINESS_SIZE": values.get("business_size"),
            "BUSINESS_STATUS": values.get("business_status"), "ANNUAL_REVENUE": values.get("annual_revenue"),
            "FINANCING_STATUS": values.get("financing_status"), "FINANCING_NEED": values.get("financing_need"),
            "TRAINING_STATUS": values.get("training_status"), "DIGITALISATION": values.get("digitalisation"),
            "PROGRAMME": values.get("programme"), "MODULE": module_tags,
            "MATCH_CONFIDENCE": confidence, "MATCH_STATUS": match_status, "SOURCE_SYSTEMS": source_systems,
            "SOURCE_RECORD_COUNT": len(group), "SOURCE_RECORDS": source_records,
            "SOURCE_FIELD_PROVENANCE": provenance
        }
        old = old_by_id.get(sme_id, {})
        created_at = old.get("CREATED_AT") or old.get("created_at") or fmt_dt()
        legacy_aliases = {"BUSINESS_NAME":"business_name","SSM":"ssm","PHONE":"phone","EMAIL":"email","ADDRESS":"address","POSTCODE":"postcode","CITY":"city","STATE":"state","SECTOR":"sector","BUSINESS_SIZE":"business_size","BUSINESS_STATUS":"business_status","ANNUAL_REVENUE":"annual_revenue","FINANCING_STATUS":"financing_status","FINANCING_NEED":"financing_need","TRAINING_STATUS":"training_status","DIGITALISATION":"digitalisation","PROGRAMME":"programme"}
        compare_keys = [k for k in rec if k not in {"MATCH_CONFIDENCE"}]
        changed = any(old.get(k, old.get(legacy_aliases.get(k, "__missing__"))) != rec.get(k) for k in compare_keys)
        rec["CREATED_AT"] = created_at
        previous_updated = old.get("UPDATED_AT") or old.get("updated_at") or created_at
        rec["UPDATED_AT"] = fmt_dt() if (not old or changed) else previous_updated
        if old and changed: changed_count += 1
        golden_records.append(rec)
        group_by_sme_id[sme_id if sme_id else f"__GROUP_{group_index}"] = group_sorted

    # Primary-key integrity: no null/blank SME_ID values and no duplicates.
    generated_ids = [str(record.get("SME_ID") or "").strip() for record in golden_records]
    missing_ids = [idx for idx, value in enumerate(generated_ids) if not value]
    seen_ids = set()
    duplicate_ids = set()
    for value in generated_ids:
        if value in seen_ids:
            duplicate_ids.add(value)
        seen_ids.add(value)
    duplicate_ids = sorted(duplicate_ids)
    if missing_ids or duplicate_ids:
        raise RuntimeError(
            "Golden Record SME_ID integrity check failed: "
            f"{len(missing_ids)} missing IDs; duplicate IDs: {duplicate_ids[:10]}"
        )

    golden_payload = {
        "UDX_VERSION": UDX_VERSION, "GENERATED_BY": "UDX Integrated SME Golden Record and Lead Engine",
        "GENERATED_AT": fmt_dt(), "SOURCE_SUMMARY": source_meta, "MATCHING_RULES": MATCHING_RULES,
        "RECORD_COUNT": len(golden_records), "SME_ID_NULL_COUNT": 0,
        "SME_ID_UNIQUE_COUNT": len(generated_ids),
        "SME_BY_BUSINESS_SIZE": business_size_distribution(golden_records),
        "MATCH_REVIEW_CANDIDATE_COUNT": len(MATCH_REVIEW_CANDIDATES),
        "MATCH_REVIEW_CANDIDATES": MATCH_REVIEW_CANDIDATES,
        "GOLDEN_RECORDS": golden_records
    }
    # Persist the complete Golden Record output before starting either lead engine.
    golden_path = OUTPUT_DIR / "sme_golden_records.json"
    with golden_path.open("w", encoding="utf-8") as golden_file:
        json.dump(golden_payload, golden_file, ensure_ascii=False, indent=2, default=str)
    print(f"Golden Record stage completed and saved: {golden_path}")

    # PASS 2: Only after the complete Golden Record collection exists, generate leads from it.
    financing_leads, intervention_leads = [], []
    for rec_index, rec in enumerate(golden_records):
        group_key = rec["SME_ID"] if rec.get("SME_ID") else f"__GROUP_{rec_index}"
        group = group_by_sme_id[group_key]
        if not rec.get("SME_ID"):
            continue
        fscore, fbreak, freasons, assessment, raw_total, eligible, exclusions = financing_score(group, rec, financing_config)
        ftiers = financing_config.get("TIERS", DEFAULT_FINANCING_CONFIG["TIERS"])
        if fscore >= float(ftiers.get("EMERGING",40)):
            financing_leads.append({
                "LEAD_ID": f"FIN-{rec['SME_ID']}", "SME_ID": rec["SME_ID"], "COMPANY_NAME": rec.get("BUSINESS_NAME"),
                "SSM": rec.get("SSM"), "PHONE": rec.get("PHONE"), "EMAIL": rec.get("EMAIL"), "STATE": rec.get("STATE"), "SECTOR": rec.get("SECTOR"),
                "ANNUAL_REVENUE": rec.get("ANNUAL_REVENUE"), "TOTAL_SCORE": fscore, "TIER": score_tier(fscore, ftiers),
                "SCORE_BREAKDOWN": fbreak, "RAW_DATA_SCORE": raw_total, "ELSA_ASSESSMENT_SCORE": assessment,
                "REASONS": freasons, "ELIGIBILITY_STATUS": "PENDING_ASSESSMENT" if eligible else "NOT_ELIGIBLE_PENDING_REVIEW",
                "ELIGIBILITY_FLAGS": exclusions, "READINESS": "TO_BE_ASSESSED", "SOURCE_SYSTEMS": rec["SOURCE_SYSTEMS"], "REVIEW_REQUIRED": True
            })
        intervention_leads.extend(intervention_scores(group, rec, intervention_config))

    financing_payload = {"UDX_VERSION": UDX_VERSION, "SCORING_VERSION": financing_config.get("SCORING_VERSION","1.0"), "GENERATED_AT": fmt_dt(), "LEAD_TYPE": "FINANCING", "LEAD_COUNT": len(financing_leads), "FINANCING_POTENTIAL_LEADS": financing_leads}
    intervention_payload = {"UDX_VERSION": UDX_VERSION, "SCORING_VERSION": intervention_config.get("SCORING_VERSION","1.0"), "GENERATED_AT": fmt_dt(), "LEAD_TYPE": "INTERVENTION", "LEAD_COUNT": len(intervention_leads), "INTERVENTION_POTENTIAL_LEADS": intervention_leads}
    stats = {"EXISTING_SME_IDS_REUSED": reused_count, "NEW_SME_IDS_GENERATED": new_count, "EXISTING_RECORDS_CHANGED": changed_count}
    return golden_payload, financing_payload, intervention_payload, stats


def _excel_safe_frame(rows):
    """Convert nested JSON values to readable Excel cell strings."""
    frame = pd.json_normalize(rows, sep=".") if rows else pd.DataFrame()
    for col in frame.columns:
        if frame[col].map(lambda v: isinstance(v, (dict, list, tuple, set))).any():
            frame[col] = frame[col].map(
                lambda v: json.dumps(v, ensure_ascii=False, default=str)
                if isinstance(v, (dict, list, tuple, set)) else v
            )
    return frame


def write_excel_outputs(golden, financing, intervention, summary, path):
    """Write all engine outputs to one Excel workbook with analysis-ready sheets."""
    path.parent.mkdir(parents=True, exist_ok=True)
    golden_rows = golden.get("GOLDEN_RECORDS", [])
    financing_rows = financing.get("FINANCING_POTENTIAL_LEADS", [])
    intervention_rows = intervention.get("INTERVENTION_POTENTIAL_LEADS", [])
    source_rows = []
    for source, details in (summary.get("SOURCE_SUMMARY") or {}).items():
        row = {"SOURCE_SYSTEM": source}
        row.update(details if isinstance(details, dict) else {"DETAILS": details})
        source_rows.append(row)
    review_rows = golden.get("MATCH_REVIEW_CANDIDATES", [])
    summary_rows = [{"METRIC": k, "VALUE": json.dumps(v, ensure_ascii=False, default=str) if isinstance(v, (dict, list)) else v}
                    for k, v in summary.items()]

    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        _excel_safe_frame(golden_rows).to_excel(writer, sheet_name="Golden Records", index=False)
        _excel_safe_frame(financing_rows).to_excel(writer, sheet_name="Financing Leads", index=False)
        _excel_safe_frame(intervention_rows).to_excel(writer, sheet_name="Intervention Leads", index=False)
        _excel_safe_frame(source_rows).to_excel(writer, sheet_name="Source Summary", index=False)
        _excel_safe_frame(review_rows).to_excel(writer, sheet_name="Match Review", index=False)
        _excel_safe_frame(summary_rows).to_excel(writer, sheet_name="Run Summary", index=False)

        # Practical worksheet defaults for large output tables.
        for ws in writer.book.worksheets:
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            for cell in ws[1]:
                font = copy_style(cell.font)
                font.bold = True
                cell.font = font
            # Bound column sizing cost; avoid scanning every cell in huge sheets.
            for col_cells in ws.iter_cols(min_row=1, max_row=min(ws.max_row, 200)):
                values = [len(str(c.value)) for c in col_cells if c.value is not None]
                if values:
                    width = min(max(max(values) + 2, 12), 42)
                    ws.column_dimensions[col_cells[0].column_letter].width = width


def main():
    # Capture and display the process start timestamp before processing begins.
    process_start = now_myt()
    tick = perf_counter()
    print("=" * 72)
    print("UDX SME GOLDEN RECORD ENGINE")
    print(f"PROCESS START DATETIME : {fmt_dt(process_start)} (Malaysia time, UTC+08:00)")
    print("=" * 72)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True); CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    matching_config, financing_config, intervention_config = load_configs()
    existing_records, existing_path = load_existing_golden()
    source_files = discover_source_files()
    all_records, source_meta = [], {}
    timings = {}
    t = perf_counter()
    for source, filename in source_files.items():
        records, metadata = read_source(source, filename)
        source_meta[source] = metadata; all_records.extend(records)
    timings["SOURCE_LOADING_AND_NORMALISATION"] = round(perf_counter()-t,3)
    t = perf_counter()
    golden, financing, intervention, id_stats = build_outputs(all_records, source_meta, existing_records, financing_config, intervention_config)
    timings["MATCHING_AND_LEAD_SCORING"] = round(perf_counter()-t,3)
    outputs = {
        "sme_golden_records.json": golden,
        "financing_potential_leads.json": financing,
        "intervention_potential_leads.json": intervention
    }
    for filename, payload in outputs.items():
        path = OUTPUT_DIR / filename
        with path.open("w", encoding="utf-8") as f: json.dump(payload, f, ensure_ascii=False, indent=2, default=str)
        print(f"Created: {path}")
    end = now_myt()
    runtime = round(perf_counter() - tick, 3)
    runtime_hours = round(runtime / 3600, 6)
    whole = int(runtime)
    hh, rem = divmod(whole, 3600)
    mm, ss = divmod(rem, 60)
    intervention_counts = {}
    for lead in intervention["INTERVENTION_POTENTIAL_LEADS"]:
        key = lead["INTERVENTION_TYPE"]; intervention_counts[key] = intervention_counts.get(key,0)+1
    summary = {
        "UDX_VERSION": UDX_VERSION, "GENERATED_AT": fmt_dt(end), "PROCESS_START_DATETIME": fmt_dt(process_start), "PROCESS_END_DATETIME": fmt_dt(end),
        "TOTAL_RUNTIME_SECONDS": runtime,
        "TOTAL_RUNTIME_HOURS": runtime_hours,
        "TOTAL_RUNTIME_HH_MM_SS": f"{hh:02d}:{mm:02d}:{ss:02d}",
        "INPUT_DIRECTORY": str(INPUT_DIR), "OUTPUT_DIRECTORY": str(OUTPUT_DIR), "EXISTING_GOLDEN_RECORD_FILE": str(existing_path) if existing_path else None,
        "SOURCE_RECORDS_READ": sum(m["record_count"] for m in source_meta.values()), "SOURCE_SUMMARY": source_meta, "PROCESSING_TIMINGS_SECONDS": timings,
        "IDENTITY_STATISTICS": id_stats,
        "OUTPUT_COUNTS": {"GOLDEN_RECORDS": golden["RECORD_COUNT"], "FINANCING_LEADS": financing["LEAD_COUNT"], "INTERVENTION_LEADS": intervention["LEAD_COUNT"], "INTERVENTION_BY_TYPE": intervention_counts},
        "MATCHING_STATISTICS": {status: sum(1 for r in golden["GOLDEN_RECORDS"] if r.get("MATCH_STATUS") == status) for status in sorted(set(r.get("MATCH_STATUS") for r in golden["GOLDEN_RECORDS"]))},
        "DATA_QUALITY": {
            "GOLDEN_RECORDS_WITHOUT_SME_ID": sum(1 for r in golden["GOLDEN_RECORDS"] if is_blank(r.get("SME_ID"))),
            "GOLDEN_RECORDS_WITH_DUPLICATE_SME_ID": len(golden["GOLDEN_RECORDS"]) - len({r.get("SME_ID") for r in golden["GOLDEN_RECORDS"]}),
            "GOLDEN_RECORDS_WITHOUT_COMPANY_NAME": sum(1 for r in golden["GOLDEN_RECORDS"] if is_blank(r.get("BUSINESS_NAME"))),
            "GOLDEN_RECORDS_WITHOUT_SSM": sum(1 for r in golden["GOLDEN_RECORDS"] if is_blank(r.get("SSM"))),
            "GOLDEN_RECORDS_WITHOUT_PHONE": sum(1 for r in golden["GOLDEN_RECORDS"] if is_blank(r.get("PHONE"))),
            "GOLDEN_RECORDS_WITHOUT_EMAIL": sum(1 for r in golden["GOLDEN_RECORDS"] if is_blank(r.get("EMAIL"))),
            "GOLDEN_RECORDS_WITH_MODULE_NA": sum(1 for r in golden["GOLDEN_RECORDS"] if r.get("MODULE") == "NA"),
            "IDENTITY_REVIEW_REQUIRED": sum(1 for r in golden["GOLDEN_RECORDS"] if r.get("MATCH_STATUS") == "IDENTITY_REVIEW_REQUIRED")
        },
        "MODULE_RULE": "MODULE is always present in every Golden Record; unique tags are combined across matched source rows; missing MODULE is the string NA.",
        "TIMESTAMP_RULE": "Malaysia time UTC+08:00 displayed as YYYY-MM-DD HH:MM:SS. Existing CREATED_AT is preserved; UPDATED_AT changes only when the consolidated record changes.",
        "NOTES": [
            "Five input source systems are required: MIS4, CBRS, ELSA, EPC and JOMXCESS.",
            "Golden Records are generated before financing and intervention lead outputs.",
            "Every Golden Record has a unique, non-null SME_ID. Existing IDs are reused on strong identity matches; otherwise a new deterministic ID is generated, including for sparse records.",
            "When state cannot be identified, the SME_ID state segment defaults to MY; the STATE profile field remains blank rather than asserting an unknown state.",
            "SSM mapping is configured for ELSA and CBRS only; EPC, JOMXCESS and MIS4 are not guessed as SSM sources.",
            "SSM conflicts prevent automatic merging. Matching review thresholds remain configurable.",
            "MODULE is a programme/record tag, not a matching key or mandatory eligibility attribute; output is array or NA.",
            "Scoring weights and tier thresholds are configuration-driven and initial rules require business validation.",
            "Scores are prioritisation indicators, not financing approvals or confirmed programme eligibility.",
            "A SME may receive multiple intervention leads. Lead IDs are deterministic per SME and intervention type."
        ]
    }
    summary_path=OUTPUT_DIR/"udx_run_summary.json"
    summary_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str),encoding="utf-8")

    # One consolidated Excel workbook alongside the four JSON outputs.
    excel_start = perf_counter()
    excel_path = OUTPUT_DIR / "udx_outputs.xlsx"
    write_excel_outputs(golden, financing, intervention, summary, excel_path)
    timings["EXCEL_GENERATION"] = round(perf_counter() - excel_start, 3)
    summary["EXCEL_OUTPUT_FILE"] = str(excel_path)
    timings["EXCEL_GENERATION"] = round(perf_counter() - excel_start, 3)
    summary["PROCESSING_TIMINGS_SECONDS"] = timings
    end = now_myt()
    runtime = round(perf_counter() - tick, 3)
    runtime_hours = round(runtime / 3600, 6)
    whole = int(runtime)
    hh, rem = divmod(whole, 3600)
    mm, ss = divmod(rem, 60)
    summary["TOTAL_RUNTIME_SECONDS"] = runtime
    summary["TOTAL_RUNTIME_HOURS"] = runtime_hours
    summary["TOTAL_RUNTIME_HH_MM_SS"] = f"{hh:02d}:{mm:02d}:{ss:02d}"
    summary["PROCESS_END_DATETIME"] = fmt_dt(end)
    summary["GENERATED_AT"] = fmt_dt(end)
    # Refresh the workbook so its Run Summary sheet includes Excel generation.
    excel_refresh_start = perf_counter()
    write_excel_outputs(golden, financing, intervention, summary, excel_path)
    timings["EXCEL_GENERATION"] = round(timings.get("EXCEL_GENERATION", 0.0) + perf_counter() - excel_refresh_start, 3)
    summary["PROCESSING_TIMINGS_SECONDS"] = timings
    # Include both workbook writes in the exact JSON/console runtime.
    end = now_myt()
    runtime = round(perf_counter() - tick, 3)
    runtime_hours = round(runtime / 3600, 6)
    whole = int(runtime)
    hh, rem = divmod(whole, 3600)
    mm, ss = divmod(rem, 60)
    summary["TOTAL_RUNTIME_SECONDS"] = runtime
    summary["TOTAL_RUNTIME_HOURS"] = runtime_hours
    summary["TOTAL_RUNTIME_HH_MM_SS"] = f"{hh:02d}:{mm:02d}:{ss:02d}"
    summary["PROCESS_END_DATETIME"] = fmt_dt(end)
    summary["GENERATED_AT"] = fmt_dt(end)
    summary_path.write_text(json.dumps(summary,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    print(f"Created Excel workbook: {excel_path}")
    print("\nUDX processing completed.")
    print(f"Golden Records: {golden['RECORD_COUNT']:,}")
    print(f"Financing leads: {financing['LEAD_COUNT']:,}")
    print(f"Intervention leads: {intervention['LEAD_COUNT']:,}")
    print(f"SME_ID reused: {id_stats['EXISTING_SME_IDS_REUSED']:,}; generated: {id_stats['NEW_SME_IDS_GENERATED']:,}")
    print(f"PROCESS START DATETIME : {fmt_dt(process_start)} (Malaysia time, UTC+08:00)")
    print(f"PROCESS END DATETIME   : {fmt_dt(end)} (Malaysia time, UTC+08:00)")
    print(f"TOTAL RUNNING TIME     : {runtime_hours:.6f} hours ({hh:02d}:{mm:02d}:{ss:02d})")
    print(f"Runtime: {runtime}s ({summary['TOTAL_RUNTIME_HH_MM_SS']})")
    print(f"Summary: {summary_path}")


if __name__ == "__main__":
    main()
