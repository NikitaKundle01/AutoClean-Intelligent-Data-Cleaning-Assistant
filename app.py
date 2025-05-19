import streamlit as st
import pandas as pd
import os
from modules.cleaner import DataCleaner
from modules.db_handler import DBHandler
from ydata_profiling import ProfileReport
from streamlit_pandas_profiling import st_profile_report  # Add this import
import tempfile

# Page config
st.set_page_config(page_title="AutoClean", page_icon="🧹", layout="wide")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'cleaned_df' not in st.session_state:
    st.session_state.cleaned_df = None

# Sidebar for navigation
st.sidebar.title("AutoClean")
page = st.sidebar.radio("Navigation", ["Upload Data", "Clean Data", "Data Profile", "History"])

def main():
    if page == "Upload Data":
        upload_page()
    elif page == "Clean Data":
        clean_page()
    elif page == "Data Profile":
        profile_page()
    elif page == "History":
        history_page()

def upload_page():
    st.title("📤 Upload Your Dataset")
    
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=["csv", "xlsx"])
    
    if uploaded_file:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            st.session_state.df = df
            st.success("File uploaded successfully!")
            
            st.subheader("Data Preview")
            st.write(df.head())
            
            # Basic info
            st.subheader("Basic Information")
            st.write(f"Shape: {df.shape}")
            st.write("Columns:")
            st.write(df.dtypes)
            
        except Exception as e:
            st.error(f"Error reading file: {e}")

def clean_page():
    st.title("🧹 Clean Your Data")
    
    if st.session_state.df is None:
        st.warning("Please upload a file first!")
        return
    
    df = st.session_state.df
    
    st.subheader("Current Data")
    st.write(df.head())
    
    # Initialize DataCleaner
    cleaner = DataCleaner(df)
    
    # Drop columns
    cols_to_drop = st.multiselect("Select columns to drop", df.columns)
    if cols_to_drop:
        cleaner.drop_columns(cols_to_drop)
    
    # Handle missing values
    st.subheader("Handle Missing Values")
    missing_cols = df.columns[df.isnull().any()].tolist()
    
    if missing_cols:
        for col in missing_cols:
            st.write(f"Column: {col} ({df[col].dtype})")
            strategy = st.selectbox(
                f"How to handle missing values in {col}",
                ["Do nothing", "Drop rows", "Fill with mean", "Fill with median", 
                 "Fill with mode", "Fill with custom value"],
                key=f"missing_{col}"
            )
            
            if strategy.startswith("Fill with custom"):
                custom_val = st.text_input(f"Custom value for {col}", key=f"custom_{col}")
                if st.button(f"Apply to {col}"):
                    cleaner.fill_missing(col, strategy, custom_val)
            elif strategy != "Do nothing":
                if st.button(f"Apply to {col}"):
                    cleaner.fill_missing(col, strategy)
    else:
        st.info("No missing values found!")
    
    # Remove duplicates
    if st.checkbox("Remove duplicate rows"):
        cleaner.remove_duplicates()
        st.success("Duplicates removed!")
    
    # Convert data types
    st.subheader("Convert Data Types")
    for col in df.columns:
        current_type = str(df[col].dtype)
        new_type = st.selectbox(
            f"Change {col} type (current: {current_type})",
            ["Keep as is", "int", "float", "str", "datetime", "category"],
            key=f"dtype_{col}"
        )
        if new_type != "Keep as is":
            cleaner.convert_dtype(col, new_type)
    
    # Show cleaned data
    if st.button("Apply All Cleaning"):
        st.session_state.cleaned_df = cleaner.get_cleaned_data()
        st.success("Data cleaned successfully!")
        st.subheader("Cleaned Data Preview")
        st.write(st.session_state.cleaned_df.head())
        
        # Download button
        csv = st.session_state.cleaned_df.to_csv(index=False)
        st.download_button(
            label="Download cleaned data as CSV",
            data=csv,
            file_name="cleaned_data.csv",
            mime="text/csv"
        )

def profile_page():
    st.title("📊 Data Profile")
    
    df = st.session_state.cleaned_df if st.session_state.cleaned_df is not None else st.session_state.df
    
    if df is None:
        st.warning("Please upload a file first!")
        return
    
    if st.button("Generate Full Report"):
        with st.spinner("Generating report..."):
            profile = ProfileReport(df, title="Data Profiling Report")
            st_profile_report(profile)

def history_page():
    st.title("📚 Cleaning History")
    st.info("This feature will be implemented with database integration")

if __name__ == "__main__":
    main()
