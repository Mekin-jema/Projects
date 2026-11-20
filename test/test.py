import streamlit as st
import pandas as pd
import re
from io import BytesIO


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="MSISDN Reconciliation",
    page_icon="📱",
    layout="wide"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }

    .title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #666;
        font-size: 16px;
        margin-bottom: 25px;
    }

    .metric-card {
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #ddd;
        background-color: #fafafa;
    }

    .found {
        color: #16803c;
        font-weight: bold;
    }

    .not-found {
        color: #c62828;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="title">📱 MSISDN Reconciliation System</div>',
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="subtitle">
    Compare hotel-reported service users against internal company records
    and identify MSISDNs that require investigation or business decisions.
    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_msisdn(value):
    """
    Normalize Ethiopian MSISDN values.

    Examples:
        251911234567
        +251911234567
        0911234567
        911234567

    Result:
        251911234567
    """

    if pd.isna(value):
        return None

    value = str(value).strip()

    # Remove Excel's trailing .0
    if value.endswith(".0"):
        value = value[:-2]

    # Remove spaces, -, (, ), etc.
    value = re.sub(r"[^\d+]", "", value)

    # Remove leading +
    value = value.replace("+", "")

    # Ethiopian local format
    if value.startswith("0") and len(value) == 10:
        value = "251" + value[1:]

    # Ethiopian format without country code
    elif len(value) == 9 and value.startswith("9"):
        value = "251" + value

    return value


def find_msisdn_column(df):
    """
    Try to automatically find the MSISDN column.
    """

    possible_names = [
        "msisdn",
        "mobile",
        "mobile_number",
        "mobile number",
        "phone",
        "phone_number",
        "phone number",
        "customer_msisdn",
        "customer msisdn",
        "subscriber",
        "subscriber_number"
    ]

    normalized_columns = {
        str(col).strip().lower(): col
        for col in df.columns
    }

    for name in possible_names:
        if name in normalized_columns:
            return normalized_columns[name]

    return None


def create_excel(result_df, summary_df):
    """
    Create downloadable Excel workbook.
    """

    output = BytesIO()

    with pd.ExcelWriter(
        output,
        engine="openpyxl"
    ) as writer:

        result_df.to_excel(
            writer,
            sheet_name="Reconciliation",
            index=False
        )

        summary_df.to_excel(
            writer,
            sheet_name="Summary",
            index=False
        )

    output.seek(0)

    return output


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.header("⚙️ Configuration")

st.sidebar.markdown(
    """
    **Workflow**

    1. Upload hotel Excel
    2. Upload company Excel
    3. Select MSISDN columns
    4. Run reconciliation
    5. Review unmatched users
    6. Download report
    """
)

st.sidebar.divider()

decision_not_found = st.sidebar.selectbox(
    "Decision for NOT FOUND users",
    [
        "INVESTIGATE",
        "NOT ELIGIBLE",
        "REJECT",
        "MANUAL REVIEW"
    ]
)


# ============================================================
# FILE UPLOAD
# ============================================================

col1, col2 = st.columns(2)

with col1:

    st.subheader("🏨 Hotel Data")

    hotel_file = st.file_uploader(
        "Upload hotel Excel file",
        type=["xlsx", "xls"],
        key="hotel"
    )

with col2:

    st.subheader("🏢 Company Data")

    company_file = st.file_uploader(
        "Upload company Excel file",
        type=["xlsx", "xls"],
        key="company"
    )


# ============================================================
# PROCESS FILES
# ============================================================

if hotel_file and company_file:

    try:

        hotel_df = pd.read_excel(hotel_file)

        company_df = pd.read_excel(company_file)

    except Exception as e:

        st.error(f"Error reading Excel files: {e}")

        st.stop()


    # ========================================================
    # COLUMN SELECTION
    # ========================================================

    st.divider()

    st.subheader("🔍 Select MSISDN Columns")

    col1, col2 = st.columns(2)

    auto_hotel = find_msisdn_column(hotel_df)
    auto_company = find_msisdn_column(company_df)

    with col1:

        hotel_default = (
            list(hotel_df.columns).index(auto_hotel)
            if auto_hotel is not None
            else 0
        )

        hotel_msisdn_col = st.selectbox(
            "Hotel MSISDN column",
            hotel_df.columns,
            index=hotel_default
        )

    with col2:

        company_default = (
            list(company_df.columns).index(auto_company)
            if auto_company is not None
            else 0
        )

        company_msisdn_col = st.selectbox(
            "Company MSISDN column",
            company_df.columns,
            index=company_default
        )


    # ========================================================
    # FILE PREVIEW
    # ========================================================

    with st.expander("👀 Preview uploaded files"):

        col1, col2 = st.columns(2)

        with col1:

            st.write("Hotel Data")

            st.dataframe(
                hotel_df.head(10),
                use_container_width=True
            )

        with col2:

            st.write("Company Data")

            st.dataframe(
                company_df.head(10),
                use_container_width=True
            )


    # ========================================================
    # RUN BUTTON
    # ========================================================

    st.divider()

    run_comparison = st.button(
        "🚀 Run MSISDN Reconciliation",
        type="primary",
        use_container_width=True
    )


    # ========================================================
    # RECONCILIATION
    # ========================================================

    if run_comparison:

        with st.spinner("Comparing MSISDNs..."):

            # ----------------------------------------------
            # Copy data
            # ----------------------------------------------

            hotel = hotel_df.copy()
            company = company_df.copy()

            # ----------------------------------------------
            # Normalize MSISDN
            # ----------------------------------------------

            hotel["NORMALIZED_MSISDN"] = (
                hotel[hotel_msisdn_col]
                .apply(normalize_msisdn)
            )

            company["NORMALIZED_MSISDN"] = (
                company[company_msisdn_col]
                .apply(normalize_msisdn)
            )

            # ----------------------------------------------
            # Remove empty values
            # ----------------------------------------------

            hotel = hotel[
                hotel["NORMALIZED_MSISDN"].notna()
            ].copy()

            company = company[
                company["NORMALIZED_MSISDN"].notna()
            ].copy()

            # ----------------------------------------------
            # Remove duplicates from company lookup
            # ----------------------------------------------

            company_lookup = (
                company[
                    ["NORMALIZED_MSISDN"]
                ]
                .drop_duplicates()
                .copy()
            )

            company_lookup["IN_COMPANY_DATA"] = "FOUND"

            # ----------------------------------------------
            # LEFT JOIN
            #
            # Hotel list is the master list.
            # ----------------------------------------------

            result = hotel.merge(
                company_lookup,
                on="NORMALIZED_MSISDN",
                how="left"
            )

            # ----------------------------------------------
            # Determine status
            # ----------------------------------------------

            result["IN_COMPANY_DATA"] = (
                result["IN_COMPANY_DATA"]
                .fillna("NOT FOUND")
            )

            result["STATUS"] = result[
                "IN_COMPANY_DATA"
            ]

            # ----------------------------------------------
            # Business decision
            # ----------------------------------------------

            result["DECISION"] = result[
                "STATUS"
            ].apply(
                lambda x:
                    "VERIFIED"
                    if x == "FOUND"
                    else decision_not_found
            )

            # ----------------------------------------------
            # Duplicate flag
            # ----------------------------------------------

            result["DUPLICATE_HOTEL_MSISDN"] = (
                result[
                    "NORMALIZED_MSISDN"
                ]
                .duplicated(keep=False)
                .map({
                    True: "DUPLICATE",
                    False: "UNIQUE"
                })
            )

            # =================================================
            # SUMMARY
            # =================================================

            total_hotel = len(result)

            found = (
                result["STATUS"] == "FOUND"
            ).sum()

            not_found = (
                result["STATUS"] == "NOT FOUND"
            ).sum()

            duplicates = (
                result["DUPLICATE_HOTEL_MSISDN"]
                == "DUPLICATE"
            ).sum()

            unique_hotel_msisdn = (
                result["NORMALIZED_MSISDN"]
                .nunique()
            )

            match_rate = (
                found / total_hotel * 100
                if total_hotel > 0
                else 0
            )

            summary_df = pd.DataFrame({

                "METRIC": [
                    "Total Hotel Records",
                    "Unique Hotel MSISDNs",
                    "Found in Company Data",
                    "Not Found in Company Data",
                    "Duplicate Hotel Records",
                    "Match Rate (%)"
                ],

                "VALUE": [
                    total_hotel,
                    unique_hotel_msisdn,
                    found,
                    not_found,
                    duplicates,
                    round(match_rate, 2)
                ]
            })


            # =================================================
            # SAVE TO SESSION
            # =================================================

            st.session_state["result"] = result
            st.session_state["summary"] = summary_df


# ============================================================
# DISPLAY RESULTS
# ============================================================

if "result" in st.session_state:

    result = st.session_state["result"]
    summary_df = st.session_state["summary"]

    st.divider()

    st.subheader("📊 Reconciliation Summary")

    total_hotel = int(
        summary_df.loc[
            summary_df["METRIC"] == "Total Hotel Records",
            "VALUE"
        ].iloc[0]
    )

    found = int(
        summary_df.loc[
            summary_df["METRIC"] == "Found in Company Data",
            "VALUE"
        ].iloc[0]
    )

    not_found = int(
        summary_df.loc[
            summary_df["METRIC"] == "Not Found in Company Data",
            "VALUE"
        ].iloc[0]
    )

    match_rate = float(
        summary_df.loc[
            summary_df["METRIC"] == "Match Rate (%)",
            "VALUE"
        ].iloc[0]
    )


    # ========================================================
    # METRICS
    # ========================================================

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🏨 Hotel Records",
        f"{total_hotel:,}"
    )

    col2.metric(
        "✅ Found",
        f"{found:,}"
    )

    col3.metric(
        "❌ Not Found",
        f"{not_found:,}"
    )

    col4.metric(
        "📈 Match Rate",
        f"{match_rate:.2f}%"
    )


    # ========================================================
    # STATUS CHART
    # ========================================================

    st.subheader("📈 Status Distribution")

    chart_data = pd.DataFrame({
        "Status": [
            "FOUND",
            "NOT FOUND"
        ],

        "Count": [
            found,
            not_found
        ]
    })

    st.bar_chart(
        chart_data.set_index("Status")
    )


    # ========================================================
    # TABS
    # ========================================================

    tab1, tab2, tab3 = st.tabs([
        "📋 All Results",
        "❌ Not Found",
        "📊 Summary"
    ])


    # ========================================================
    # ALL RESULTS
    # ========================================================

    with tab1:

        st.dataframe(
            result,
            use_container_width=True,
            height=500
        )


    # ========================================================
    # NOT FOUND
    # ========================================================

    with tab2:

        not_found_df = result[
            result["STATUS"] == "NOT FOUND"
        ].copy()

        st.warning(
            f"{len(not_found_df):,} MSISDNs were not found "
            "in the company data."
        )

        st.dataframe(
            not_found_df,
            use_container_width=True,
            height=500
        )


    # ========================================================
    # SUMMARY
    # ========================================================

    with tab3:

        st.dataframe(
            summary_df,
            use_container_width=True
        )


    # ========================================================
    # DOWNLOAD
    # ========================================================

    st.divider()

    output = create_excel(
        result,
        summary_df
    )

    st.download_button(
        label="📥 Download Reconciliation Report",
        data=output,
        file_name="MSISDN_Reconciliation_Report.xlsx",
        mime=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        use_container_width=True
    )

else:

    st.info(
        "👆 Upload the hotel Excel and company Excel files "
        "to start the reconciliation."
    )