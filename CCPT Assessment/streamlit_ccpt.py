import csv
import io
import os
from datetime import date, datetime

import streamlit as st


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Group CCPT Assessment",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>
        /* Main application background */
        .stApp {
            background-color: #e5e5e5;
        }

        /* Hide Streamlit menu and footer */
        #MainMenu {
            visibility: hidden;
        }

        footer {
            visibility: hidden;
        }

        /* Main content container */
        .block-container {
            max-width: 1000px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            padding-left: 2.5rem;
            padding-right: 2.5rem;
            background-color: #ffffff;
            box-shadow: 0 2px 14px rgba(0, 0, 0, 0.15);
        }

        /* Main title */
        .main-title {
            text-align: center;
            font-size: 30px;
            font-weight: 700;
            color: #000000;
            margin-top: 5px;
            margin-bottom: 18px;
        }

        /* Section title */
        .section-title {
            width: 78%;
            margin: 0 auto 28px auto;
            padding: 8px 15px;
            border: 2px solid #111111;
            text-align: center;
            font-size: 21px;
            font-weight: 700;
            background-color: #ffffff;
        }

        /* Form labels */
        .field-label {
            min-height: 42px;
            display: flex;
            align-items: center;
            font-size: 14px;
            font-weight: 700;
            color: #111111;
        }

        /* Reduce default Streamlit spacing */
        div[data-testid="stVerticalBlock"] {
            gap: 0.5rem;
        }

        /* Text input styling */
        div[data-testid="stTextInput"] input {
            border: 1px solid #333333;
            border-radius: 0;
            min-height: 42px;
            font-size: 14px;
        }

        /* Text area styling */
        div[data-testid="stTextArea"] textarea {
            border: 1px solid #333333;
            border-radius: 0;
            font-size: 14px;
            min-height: 95px;
        }

        /* Select box styling */
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {
            border: 1px solid #333333;
            border-radius: 0;
            min-height: 42px;
        }

        /* Focus styling */
        div[data-testid="stTextInput"] input:focus,
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #ffc400;
            box-shadow: 0 0 0 1px #ffc400;
            background-color: #fffbea;
        }

        /* Approval section */
        .approval-title {
            color: #0047d7;
            font-size: 15px;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .approval-role {
            font-size: 12px;
            color: #333333;
            margin-top: 3px;
        }

        .approval-date {
            font-size: 12px;
            color: #0047d7;
            margin-top: 5px;
        }

        /* Approval container */
        div[data-testid="stExpander"] {
            border: 2px solid #111111;
            border-radius: 0;
            background-color: #ffffff;
        }

        div[data-testid="stExpander"] details summary {
            font-size: 17px;
            font-weight: 700;
        }

        /* Buttons */
        div.stButton > button {
            min-height: 42px;
            border-radius: 4px;
            font-weight: 700;
            padding-left: 24px;
            padding-right: 24px;
        }

        /* Primary button */
        div.stButton > button[kind="primary"] {
            background-color: #003b80;
            color: #ffffff;
            border: none;
        }

        div.stButton > button[kind="primary"]:hover {
            background-color: #00295b;
            color: #ffffff;
        }

        /* Download button */
        div[data-testid="stDownloadButton"] > button {
            width: 100%;
            min-height: 42px;
            border-radius: 4px;
            background-color: #175c23;
            color: #ffffff;
            font-weight: 700;
            border: none;
        }

        /* Mobile responsive design */
        @media screen and (max-width: 820px) {
            .stApp {
                background-color: #ffffff;
            }

            .block-container {
                width: 100%;
                padding-left: 1rem;
                padding-right: 1rem;
                box-shadow: none;
            }

            .section-title {
                width: 100%;
            }

            .main-title {
                font-size: 24px;
            }
        }

        /* Print settings */
        @media print {
            .stApp {
                background-color: #ffffff;
            }

            .block-container {
                width: 210mm;
                min-height: 297mm;
                max-width: 210mm;
                padding: 10mm 14mm 12mm 14mm;
                box-shadow: none;
            }

            button {
                display: none !important;
            }

            header {
                display: none !important;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CONSTANTS
# ============================================================

BNM_SECTORS = [
    "Please select",
    "Real Estate (Commercial and Residential)",
    "Electricity, Gas, Steam and Air Conditioning Supply",
    "Transportation and Storage",
    "Manufacturing",
    "Water Supply; Sewerage, Waste Management and Remediation Activities",
    "Agriculture, Forestry and Fishing",
    "Others (Please specify)",
]

FINANCING_TYPES = [
    "Please select",
    "Islamic",
    "Conventional",
]

ASSESSMENT_TYPES = [
    "New Application",
    "Annual Review",
    "Additional",
]

GREEN_COMPANY_OPTIONS = [
    "Please select",
    "Yes",
    "No",
]

CORPORATE_STATUSES = [
    "Please select",
    "Commercial",
    "Corporate",
    "SME-Micro",
    "SME-Small",
    "SME-Medium",
    "SME-Large",
]

CSV_FILE = "ccpt_applications.csv"

TODAY = date.today().strftime("%d/%m/%Y")


# ============================================================
# SESSION STATE DEFAULT VALUES
# ============================================================

DEFAULT_VALUES = {
    "customer_name": "",
    "cif_number": "",
    "account_number": "",
    "bnm_sector": "Others (Please specify)",
    "other_sector": "",
    "principal_activities": (
        "Engaged in the supply of healthcare and related products and "
        "services to hospitals, healthcare centres, and pharmacies in "
        "Malaysia and internationally."
    ),
    "business_location": (
        "3 Church Street, #18-01, Samsung Hub, Singapore 049483"
    ),
    "financing_type": "Islamic",
    "purpose": (
        "a) To part finance investment of Adventa in Indonesia.\n"
        "b) To redeem financial of HSBC Indonesia."
    ),
    "assessment_type": "New Application",
    "esg_result": "",
    "green_company": "Please select",
    "green_industry": "",
    "ccpt_classification": "",
    "corporate_status": "Please select",
    "prepared_by": "",
    "reviewed_by": "",
    "endorsed_by": "",
}


def initialise_session_state():
    """Create default session-state values on initial page load."""

    for key, value in DEFAULT_VALUES.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_form():
    """Reset all application fields to their original values."""

    for key, value in DEFAULT_VALUES.items():
        st.session_state[key] = value

    st.session_state["save_successful"] = False
    st.session_state["validation_message"] = ""


initialise_session_state()

if "save_successful" not in st.session_state:
    st.session_state["save_successful"] = False

if "validation_message" not in st.session_state:
    st.session_state["validation_message"] = ""


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def form_row(label_text, widget_function):
    """
    Display a label and Streamlit widget in a two-column layout.
    """

    label_column, input_column = st.columns([1.25, 3.75])

    with label_column:
        st.markdown(
            f'<div class="field-label">{label_text}</div>',
            unsafe_allow_html=True,
        )

    with input_column:
        return widget_function()


def calculate_esg_result(green_company):
    """
    Example ESG calculation.

    Replace this function with the bank's approved ESG assessment
    methodology when the actual assessment rules are available.
    """

    if green_company == "Yes":
        return "Green Pure-Play"

    if green_company == "No":
        return "Further ESG Assessment Required"

    return ""


def calculate_ccpt_classification(green_company):
    """
    Example CCPT classification.

    Replace this function with the approved CCPT classification rules.
    """

    if green_company == "Yes":
        return "Climate Supporting"

    if green_company == "No":
        return "Pending Detailed CCPT Assessment"

    return ""


def validate_application(application_data):
    """
    Validate mandatory application fields.
    """

    missing_fields = []

    if not application_data["Customer Name"].strip():
        missing_fields.append("Customer Name")

    if not application_data["CIF Number"].strip():
        missing_fields.append("CIF Number")

    if application_data["BNM Sector"] == "Please select":
        missing_fields.append("Customer BNM Sector")

    if (
        application_data["BNM Sector"] == "Others (Please specify)"
        and not application_data["Other Sector"].strip()
    ):
        missing_fields.append("Specify Sector")

    if application_data["Financing Type"] == "Please select":
        missing_fields.append("Type of Financing")

    if application_data["Green Pure-Play Company"] == "Please select":
        missing_fields.append("Green Pure-Play Company")

    if application_data["Corporate Status"] == "Please select":
        missing_fields.append("Corporate Status")

    if (
        application_data["Green Pure-Play Company"] == "No"
        and not application_data["Green Pure-Play Industry"].strip()
    ):
        missing_fields.append("Green Pure-Play Industry")

    return missing_fields


def save_to_csv(application_data):
    """
    Append application information to a CSV file.
    """

    file_exists = os.path.exists(CSV_FILE)

    with open(
        CSV_FILE,
        mode="a",
        newline="",
        encoding="utf-8-sig",
    ) as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=application_data.keys(),
        )

        if not file_exists:
            writer.writeheader()

        writer.writerow(application_data)


def create_download_csv(application_data):
    """
    Create a one-record CSV file in memory for downloading.
    """

    output = io.StringIO()

    writer = csv.DictWriter(
        output,
        fieldnames=application_data.keys(),
    )

    writer.writeheader()
    writer.writerow(application_data)

    return output.getvalue().encode("utf-8-sig")


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">Group CCPT Assessment</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="section-title">Summary of Application</div>',
    unsafe_allow_html=True,
)


# ============================================================
# APPLICATION FORM
# ============================================================

customer_name = form_row(
    "Customer Name:",
    lambda: st.text_input(
        "Customer Name",
        key="customer_name",
        placeholder="Fill in Customer Name",
        label_visibility="collapsed",
    ),
)

cif_number = form_row(
    "CIF Number:",
    lambda: st.text_input(
        "CIF Number",
        key="cif_number",
        placeholder="Fill in CIF Number",
        label_visibility="collapsed",
    ),
)

account_number = form_row(
    "Customer Account No:",
    lambda: st.text_input(
        "Customer Account Number",
        key="account_number",
        placeholder="Fill in Customer Account Number",
        label_visibility="collapsed",
    ),
)

bnm_sector = form_row(
    "Customer BNM Sector:",
    lambda: st.selectbox(
        "Customer BNM Sector",
        options=BNM_SECTORS,
        key="bnm_sector",
        label_visibility="collapsed",
    ),
)

if bnm_sector == "Others (Please specify)":
    other_sector = form_row(
        "Specify Sector:",
        lambda: st.text_input(
            "Specify Sector",
            key="other_sector",
            placeholder="Please specify the BNM sector",
            label_visibility="collapsed",
        ),
    )
else:
    other_sector = ""
    st.session_state["other_sector"] = ""

principal_activities = form_row(
    "Principal Activities:",
    lambda: st.text_area(
        "Principal Activities",
        key="principal_activities",
        height=100,
        label_visibility="collapsed",
    ),
)

business_location = form_row(
    "Business Location:",
    lambda: st.text_input(
        "Business Location",
        key="business_location",
        label_visibility="collapsed",
    ),
)

financing_type = form_row(
    "Type of Financing:",
    lambda: st.selectbox(
        "Type of Financing",
        options=FINANCING_TYPES,
        key="financing_type",
        label_visibility="collapsed",
    ),
)

purpose = form_row(
    "Purpose of Financing:",
    lambda: st.text_area(
        "Purpose of Financing",
        key="purpose",
        height=110,
        label_visibility="collapsed",
    ),
)

assessment_type = form_row(
    "Type of CCPT Assessment:",
    lambda: st.selectbox(
        "Type of CCPT Assessment",
        options=ASSESSMENT_TYPES,
        key="assessment_type",
        label_visibility="collapsed",
    ),
)

green_company = form_row(
    "Green Pure-Play Company:",
    lambda: st.selectbox(
        "Green Pure-Play Company",
        options=GREEN_COMPANY_OPTIONS,
        key="green_company",
        label_visibility="collapsed",
    ),
)


# ============================================================
# AUTOMATIC ESG AND CCPT RESULTS
# ============================================================

st.session_state["esg_result"] = calculate_esg_result(green_company)
st.session_state["ccpt_classification"] = calculate_ccpt_classification(
    green_company
)

esg_result = form_row(
    "ESG:",
    lambda: st.text_input(
        "ESG Result",
        value=st.session_state["esg_result"],
        disabled=True,
        placeholder="Assessment result",
        label_visibility="collapsed",
    ),
)


# ============================================================
# GREEN PURE-PLAY INDUSTRY LOGIC
# ============================================================

if green_company == "Yes":
    st.session_state["green_industry"] = ""

    green_industry = form_row(
        "Green Pure-Play Industry:",
        lambda: st.text_input(
            "Green Pure-Play Industry",
            value="Not required for Green Pure-Play Company",
            disabled=True,
            label_visibility="collapsed",
        ),
    )

elif green_company == "No":
    green_industry = form_row(
        "Green Pure-Play Industry:",
        lambda: st.text_input(
            "Green Pure-Play Industry",
            key="green_industry",
            placeholder="Specify industry",
            label_visibility="collapsed",
        ),
    )

else:
    green_industry = form_row(
        "Green Pure-Play Industry:",
        lambda: st.text_input(
            "Green Pure-Play Industry",
            key="green_industry",
            placeholder="Select Green Pure-Play Company first",
            disabled=True,
            label_visibility="collapsed",
        ),
    )


ccpt_classification = form_row(
    "CCPT:",
    lambda: st.text_input(
        "CCPT Classification",
        value=st.session_state["ccpt_classification"],
        disabled=True,
        placeholder="CCPT classification",
        label_visibility="collapsed",
    ),
)

corporate_status = form_row(
    "Corporate Status:",
    lambda: st.selectbox(
        "Corporate Status",
        options=CORPORATE_STATUSES,
        key="corporate_status",
        label_visibility="collapsed",
    ),
)


# ============================================================
# APPROVAL SECTION
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

with st.expander(
    "Approval and Endorsement",
    expanded=True,
):
    prepared_column, reviewed_column = st.columns([1, 2])

    with prepared_column:
        st.markdown(
            '<div class="approval-title">Prepared by:</div>',
            unsafe_allow_html=True,
        )

        prepared_by = st.text_input(
            "Prepared by",
            key="prepared_by",
            placeholder="Enter name",
            label_visibility="collapsed",
        )

        st.markdown(
            '<div class="approval-role">Relationship Manager</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="approval-date">Date: {TODAY}</div>',
            unsafe_allow_html=True,
        )

    with reviewed_column:
        st.markdown(
            '<div class="approval-title">Reviewed by:</div>',
            unsafe_allow_html=True,
        )

        reviewed_by = st.text_input(
            "Reviewed by",
            key="reviewed_by",
            placeholder="Enter name",
            label_visibility="collapsed",
        )

        st.markdown(
            """
            <div class="approval-role">
                Team Leader / Head of EC / Regional Director
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown(
            f'<div class="approval-date">Date: {TODAY}</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    st.markdown(
        '<div class="approval-title">Endorsed by:</div>',
        unsafe_allow_html=True,
    )

    endorsed_by = st.text_input(
        "Endorsed by",
        key="endorsed_by",
        placeholder="Enter name",
        label_visibility="collapsed",
    )

    st.markdown(
        """
        <div class="approval-role">
            Climate Risk &amp; Stress Testing Department
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f'<div class="approval-date">Date: {TODAY}</div>',
        unsafe_allow_html=True,
    )


# ============================================================
# PREPARE APPLICATION RECORD
# ============================================================

application_data = {
    "Submission Timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
    "Customer Name": customer_name,
    "CIF Number": cif_number,
    "Customer Account Number": account_number,
    "BNM Sector": bnm_sector,
    "Other Sector": (
        st.session_state.get("other_sector", "")
        if bnm_sector == "Others (Please specify)"
        else ""
    ),
    "Principal Activities": principal_activities,
    "Business Location": business_location,
    "Financing Type": financing_type,
    "Purpose of Financing": purpose,
    "CCPT Assessment Type": assessment_type,
    "ESG Result": st.session_state["esg_result"],
    "Green Pure-Play Company": green_company,
    "Green Pure-Play Industry": (
        st.session_state.get("green_industry", "")
        if green_company == "No"
        else ""
    ),
    "CCPT Classification": st.session_state["ccpt_classification"],
    "Corporate Status": corporate_status,
    "Prepared By": prepared_by,
    "Prepared Date": TODAY,
    "Reviewed By": reviewed_by,
    "Reviewed Date": TODAY,
    "Endorsed By": endorsed_by,
    "Endorsed Date": TODAY,
}


# ============================================================
# BUTTONS
# ============================================================

st.markdown("<br>", unsafe_allow_html=True)

spacer_column, reset_column, save_column = st.columns(
    [3.5, 1, 1.3]
)

with reset_column:
    st.button(
        "Reset",
        use_container_width=True,
        on_click=reset_form,
    )

with save_column:
    save_clicked = st.button(
        "Save Application",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# SAVE AND VALIDATION
# ============================================================

if save_clicked:
    missing_fields = validate_application(application_data)

    if missing_fields:
        st.session_state["save_successful"] = False

        missing_fields_text = ", ".join(missing_fields)

        st.session_state["validation_message"] = (
            f"Please complete the following required fields: "
            f"{missing_fields_text}."
        )

        st.error(st.session_state["validation_message"])

    else:
        try:
            save_to_csv(application_data)

            st.session_state["save_successful"] = True
            st.session_state["validation_message"] = ""

            st.success(
                "Application information saved successfully."
            )

        except PermissionError:
            st.session_state["save_successful"] = False

            st.error(
                "The CSV file is currently open or cannot be accessed. "
                "Close the file and save the application again."
            )

        except OSError as error:
            st.session_state["save_successful"] = False

            st.error(
                f"Unable to save the application: {error}"
            )


# ============================================================
# DOWNLOAD SAVED APPLICATION
# ============================================================

if st.session_state["save_successful"]:
    customer_for_filename = (
        application_data["Customer Name"]
        .strip()
        .replace(" ", "_")
        .replace("/", "_")
    )

    if not customer_for_filename:
        customer_for_filename = "customer"

    download_file_name = (
        f"CCPT_Assessment_{customer_for_filename}_"
        f"{date.today().strftime('%Y%m%d')}.csv"
    )

    csv_download = create_download_csv(application_data)

    st.download_button(
        label="Download Application CSV",
        data=csv_download,
        file_name=download_file_name,
        mime="text/csv",
        use_container_width=True,
    )


# ============================================================
# APPLICATION PREVIEW
# ============================================================

with st.expander(
    "Preview Application Summary",
    expanded=False,
):
    preview_data = {
        key: value
        for key, value in application_data.items()
        if key != "Submission Timestamp"
    }

    st.json(preview_data)