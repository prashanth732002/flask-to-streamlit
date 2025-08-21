import os
import pandas as pd
import streamlit as st

st.title("Excel Role Merger 📊")

# File uploader widgets
file1 = st.file_uploader("Upload first file (Branch Data)", type=["xlsx", "csv"])
file2 = st.file_uploader("Upload second file (Employment Data)", type=["xlsx", "csv"])

if file1 and file2:
    # Read Excel/CSV files
    df1 = pd.read_excel(file1) if file1.name.endswith('.xlsx') else pd.read_csv(file1)
    df2 = pd.read_excel(file2) if file2.name.endswith('.xlsx') else pd.read_csv(file2)

    # Ensure column names are stripped of spaces
    df1.columns = df1.columns.str.strip()
    df2.columns = df2.columns.str.strip()

    # Prepare role-wise stacked data
    role_mapping = {
        'AM': ['AM', 'AM Emp ID'],
        'DM': ['DM', 'DM Emp ID'],
        'RM': ['RM', 'RM Emp ID'],
        'SH': ['SH', 'SH Emp ID']
    }

    combined = pd.DataFrame()

    for role, cols in role_mapping.items():
        if all(col in df1.columns for col in ['Branch', 'Branch ID', 'State'] + cols):
            temp = df1[['Branch', 'Branch ID', 'State', cols[0], cols[1]]].copy()
            temp.columns = ['Branch', 'Branch ID', 'State', 'Emp Name', 'Emp ID']
            temp['Role'] = role
            combined = pd.concat([combined, temp], ignore_index=True)

    # Merge with Employment_Status
    if 'Emp ID' in df2.columns:
        merged_df = combined.merge(df2[['Emp ID', 'Employment_Status']], on='Emp ID', how='left')

        st.success("✅ Files processed successfully!")
        st.dataframe(merged_df.head(20))  # Show preview in UI

        # Download button
        output_file = "merged_roles.xlsx"
        merged_df.to_excel(output_file, index=False)
        with open(output_file, "rb") as f:
            st.download_button(
                label="📥 Download merged Excel",
                data=f,
                file_name="merged_roles.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    else:
        st.error("Second file must have column 'Emp ID'")
