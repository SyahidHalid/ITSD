import streamlit as st
import pandas as pd
import os
from datetime import date


#----------------------------config--------------------------------------------------------------------
#   st.set_page_config("Main Page", "🎪", layout="wide")

# def icon(emoji: str):
#     """Shows an emoji as a Notion-style page icon."""
#     st.write(
#         f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
#         unsafe_allow_html=True,
#     )
# # icon("🎪")

st.set_page_config(page_title="Main Page", page_icon="Merger bank.png", layout="wide")

st.image("SME_Wide.jpeg",  use_container_width=True)

st.title("SME Intelligence Hub")
#   st.header("Reminder to copy data to template before start:")
st.subheader("Data and Leads Platform (MIS, CBRS, ELSA, EPC, JOMXCESS)")
st.write('Please follow instructions as per below for smooth operation in generating golden records:')

#----------------------------side bar--------------------------------------------------------------------
st.markdown(
    """
    <style>

    /* Main page background */
    .stApp {
        background-color: #FFFFFF;
    }

    /* Main content background */
    [data-testid="stMain"] {
        background-color: #FFFFFF;
    }

    [data-testid="stMainBlockContainer"] {
        background-color: #FFFFFF;
    }

    /* Main page text */
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] p,
    [data-testid="stMain"] span,
    [data-testid="stMain"] label {
        color: #000000;
    }


    /* ==========================================
       SIDEBAR
       ========================================== */

    [data-testid="stSidebar"] {
        background-color: #0B223F;
    }

    [data-testid="stSidebarContent"] {
        background-color: #0B223F;
    }

    /* Sidebar text */
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label {
        color: #FFFFFF !important;
    }

    /* Sidebar navigation links */
    [data-testid="stSidebar"] a {
        color: #FFFFFF !important;
    }

    /* Sidebar navigation link text */
    [data-testid="stSidebarNav"] span {
        color: #FFFFFF !important;
    }

    /* Navigation hover */
    [data-testid="stSidebarNav"] a:hover {
        background-color: #173A61 !important;
        border-radius: 8px;
    }

    /* Current/selected page */
    [data-testid="stSidebarNav"] a[aria-current="page"] {
        background-color: #F6C386 !important;
        border-radius: 8px;
    }

    /* Selected page text */
    [data-testid="stSidebarNav"] a[aria-current="page"] span {
        color: #0B223F !important;
        font-weight: 700;
    }

    </style>
    """,
    unsafe_allow_html=True
)


st.sidebar.write('SME Intelligence Hub')
st.sidebar.write('BPMB Group Data and Leads Platform')

# Add footer and code version
footer = """
<style>
.footer {
    position: relative;
}

@media (max-width: 600px) {
    .footer {
        position: static;
        margin-top: 20px;
    }
}
</style>

<div class="footer">
    <hr style="margin-top: 20px;">
    <p style="font-size: 12px; color: gray;">Code version: 1.0.1</p>
</div>
"""
st.sidebar.markdown(footer, unsafe_allow_html=True)
st.sidebar.image("Merger bank.png", width=150)
#   st.sidebar.image("IH.png", width=150)
#   st.sidebar.title("Main Page")


#----------------------------Upload--------------------------------------------------------------------
# BASE_FOLDER = "."

# MIS4_FILE = os.path.join(BASE_FOLDER+'//input//', "MIS4_EXPANDED.xlsx")
# CBRS_FILE = os.path.join(BASE_FOLDER+'//input//', "CBRS_GOLDEN_RECORD_TEST_100.xlsx")
# ELSA_FILE = os.path.join(BASE_FOLDER+'//input//', "ELSA_EXPANDED.xlsx")
# EPC_FILE = os.path.join(BASE_FOLDER+'//input//', "EPC_EXPANDED.xlsx")
# JOMXCESS_FILE = os.path.join(BASE_FOLDER+'//input//', "JOMXCESS_EXPANDED.xlsx")

# def load_excel(path):
#     df = pd.read_excel(path, engine="openpyxl", dtype=object)
#     df.columns = [str(c).strip() for c in df.columns]
#     print(f"Loaded {os.path.basename(path)}: {len(df):,} rows")
#     return df

# def validate_files(paths):
#     missing = [p for p in paths if not os.path.exists(p)]
#     if missing:
#         raise FileNotFoundError("Missing files:\n- " + "\n- ".join(missing))
    
# validate_files([MIS4_FILE, CBRS_FILE, ELSA_FILE, EPC_FILE, JOMXCESS_FILE])

# mis4 = load_excel(MIS4_FILE)
# cbrs = load_excel(CBRS_FILE)
# elsa = load_excel(ELSA_FILE)
# epc = load_excel(EPC_FILE)
# jom = load_excel(JOMXCESS_FILE)


#----------------------------LEFT FORM--------------------------------------------------------------------
left_col, right_col = st.columns(2)

with left_col:
    st.subheader("DMS Dataset")

    with st.expander("Instructions"):
        st.write("Please upload the latest DMS in xlsx format.")
    
    form = st.form("Basic form")
    df1 = form.file_uploader(label= "Upload feature is ready to insert .xlsx file as per below:")

    if df1:
      df1 = pd.read_excel(df1, header=0)
    
    submitted = form.form_submit_button("Submit")
    if submitted:
      st.write("Submitted")
      st.write(df1.head(5))

      df1_1 = df1[['CUSTOMER NAME']]

      st.write(df1_1['CUSTOMER NAME'].value_counts())


    #   st.write(f"File submitted for : "+str(year)+"-"+str(month))


    # with st.form("loan_database_form"):
    #     df1 = st.file_uploader(
    #         "Upload Latest DMS Dataset:",
    #         type=["xlsx"],
    #         key="loan_file"
    #     )

    #     submitted_loan = st.form_submit_button(
    #         "Submit MIS Dataset",
    #         use_container_width=True
    #     )

    #     if submitted_loan:
    #         st.write("Column checking: ")
    #         st.write(mis4.shape)

  
    # st.write("")
    # st.write("Download file: ")
    # st.download_button("Download CSV",
    #                 mis4.to_csv(index=False),
    #                 file_name='MIS Dataset as at '+str(year)+"-"+str(month)+' - CCRIS RAW.csv',
    #                 mime='text/csv')

    # st.write("Total Rows: ", len(mis4))

    # st.subheader("MIS First 10 Rows")
    # st.dataframe(mis4.head(10), use_container_width=True)
    # st.write(mis4.head())

    # year = st.slider(
    #     "Year",
    #     min_value=2020,
    #     max_value=2030,
    #     step=1,
    #     key="loan_year"
    # )

    # month = st.slider(
    #     "Month",
    #     min_value=1,
    #     max_value=12,
    #     step=1,
    #     key="loan_month"
    # )




#----------------------------LEFT FORM--------------------------------------------------------------------
with right_col:

    st.subheader("Second File")

    with st.form("second_form"):

        year2 = st.slider(
            "Year",
            min_value=2020,
            max_value=2030,
            step=1,
            key="second_year"
        )

        month2 = st.slider(
            "Month",
            min_value=1,
            max_value=12,
            step=1,
            key="second_month"
        )

        df2 = st.file_uploader(
            "Upload Second File:",
            type=["xlsx"],
            key="second_file"
        )

        submitted_second = st.form_submit_button(
            "Submit Second File",
            use_container_width=True
        )


#----------------------------Title--------------------------------------------------------------------

#st.write('# Income Statement')
#st.write(mis4.columns)


# st.subheader("CBRS First 10 Rows")
# st.dataframe(cbrs.head())

# st.subheader("ELSA First 10 Rows")
# st.dataframe(elsa.head())

# st.subheader("EPC First 10 Rows")
# st.dataframe(epc.head())

# st.subheader("JOMXCESS First 10 Rows")
# st.dataframe(jom.head())



# # Add a date input component
# min_date = date(2019,12,31)
# max_date = date(2023,4,30)

# Date_Range = st.sidebar.date_input(
#     "Select Date Range:",
#     (min_date, max_date),
#     min_value=min_date,
#     max_value=max_date
# )

# selected_date = pd.to_datetime(Date_Range[0])
# selected_date2 = pd.to_datetime(Date_Range[1])
# st.sidebar.error("Date Range Selected: " + selected_date.strftime('%Y/%m/%d') + " to " +selected_date2.strftime('%Y/%m/%d') )



#left, center, right = st.columns([1, 2, 1])

# with center:

#     # Center image inside the center column
#     img_left, img_center, img_right = st.columns([1, 2, 1])

#     with img_center:
#         st.image("Merger bank.png", width=250)

#     # Center title and subtitle
#     st.markdown(
#         """
#         <div style="text-align: center;">
#             <h1>SME Intelligence Hub</h1>
#             <h3>Summary of Datasets</h3>
#         </div>
#         """,
#         unsafe_allow_html=True
#     )




# st.write("Total Rows: ", len(mis4))
# st.write("Total Columns: ", len(mis4.columns))
# st.write("Column Names: ", list(mis4.columns))
# st.write("Column Data Types: ", mis4.dtypes.to_dict())
# st.write("Missing Values per Column: ", mis4.isnull().sum().to_dict())
# st.write("Unique Values per Column: ", mis4.nunique().to_dict())
# st.write("Summary Statistics: ", mis4.describe(include='all').to_dict())
# st.write("First 10 Rows: ", mis4.head().to_dict(orient='records'))
# st.write("Last 10 Rows: ", mis4.tail().to_dict(orient='records'))
# st.write("Sample Rows: ", mis4.sample(10).to_dict(orient='records'))
# st.write("DataFrame Info: ")
# st.write(mis4.info())
# st.write("DataFrame Memory Usage: ", mis4.memory_usage(deep=True).to_dict())

# value = 1250

# st.metric(
#     label="Total Customers",
#     value=f"{value:,}"
# )

# import streamlit as st

# value = 85

# if value >= 80:
#     bg_color = "#ffe6e6"
#     border_color = "#dc3545"
#     text_color = "#dc3545"
# elif value >= 50:
#     bg_color = "#fff3cd"
#     border_color = "#ffc107"
#     text_color = "#856404"
# else:
#     bg_color = "#d4edda"
#     border_color = "#28a745"
#     text_color = "#155724"

# st.markdown(
#     f"""
#     <div style="
#         background-color: {bg_color};
#         border: 2px solid {border_color};
#         padding: 20px;
#         border-radius: 10px;
#         text-align: center;
#     ">
#         <p style="margin: 0;">Risk Score</p>
#         <h2 style="margin: 5px; color: {text_color};">
#             {value}
#         </h2>
#     </div>
#     """,
#     unsafe_allow_html=True
# )