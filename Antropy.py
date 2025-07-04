import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

st.set_page_config(page_title="Shannon Entropy Calculator", layout="wide")
st.title("📊 Shannon Entropy Calculator from Excel Matrix")

uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        df.columns = df.columns.str.strip()

        # Show preview
        st.subheader("📄 Raw Data Preview")
        st.dataframe(df.head(), use_container_width=True)

        # Detect matrix columns
        st.divider()
        st.subheader("⚙️ Select Key Columns")
        category_col = st.selectbox("Select Category column", df.columns, index=0)
        total_col = st.selectbox("Select Total column", df.columns, index=1)

        entropy_cols = [col for col in df.columns if col not in [category_col, total_col]]
        selected_entropy_cols = st.multiselect("Select columns to calculate entropy from", entropy_cols, default=entropy_cols)

        if selected_entropy_cols:
            # Convert to numeric
            df[selected_entropy_cols] = df[selected_entropy_cols].apply(pd.to_numeric, errors='coerce').fillna(0)

            def row_entropy(row):
                values = row[selected_entropy_cols].astype(float).values
                total = values.sum()
                if total == 0:
                    return 0.0
                probs = values / total
                probs = probs[probs > 0]
                return -np.sum(probs * np.log2(probs))

            df["Shannon Entropy"] = df.apply(row_entropy, axis=1)

            st.subheader("✅ Matrix with Shannon Entropy")
            st.dataframe(df[[category_col, total_col] + selected_entropy_cols + ['Shannon Entropy']], use_container_width=True)

            # Download option
            def to_excel_bytes(df):
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Entropy')
                return output.getvalue()

            st.download_button("📥 Download Results as Excel", to_excel_bytes(df), file_name="entropy_results.xlsx")

    except Exception as e:
        st.error(f"❌ Error reading file: {e}")
else:
    st.info("Upload an Excel file to get started.")
