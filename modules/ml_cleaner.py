import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.impute import KNNImputer
from sklearn.preprocessing import LabelEncoder

class MLCleaner:
    def __init__(self, df):
        self.df = df.copy()
        self.changes_log = []
    
    def detect_outliers(self, columns=None, contamination=0.05):
        """Detect outliers using Isolation Forest"""
        if columns is None:
            numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
            columns = numeric_cols
        
        # Only process numeric columns
        numeric_cols = [col for col in columns if self.df[col].dtype in ['int64', 'float64']]
        if not numeric_cols:
            return self.df, []
        
        # Initialize and fit the model
        clf = IsolationForest(contamination=contamination, random_state=42)
        clf.fit(self.df[numeric_cols])
        
        # Predict outliers
        outliers = clf.predict(self.df[numeric_cols]) == -1
        self.changes_log.append(f"Detected {outliers.sum()} potential outliers using Isolation Forest")
        
        return outliers
    
    def remove_outliers(self, columns=None, contamination=0.05):
        """Remove detected outliers"""
        outliers = self.detect_outliers(columns, contamination)
        initial_rows = len(self.df)
        self.df = self.df[~outliers]
        removed = initial_rows - len(self.df)
        if removed > 0:
            self.changes_log.append(f"Removed {removed} outliers")
        return self.df
    
    def smart_impute(self, columns=None):
        """Use KNN imputation for missing values"""
        if columns is None:
            columns = self.df.columns
        
        # Only process numeric columns
        numeric_cols = [col for col in columns if self.df[col].dtype in ['int64', 'float64']]
        if not numeric_cols:
            return self.df
        
        # Encode categorical columns if needed
        categorical_cols = [col for col in columns if self.df[col].dtype == 'object']
        encoders = {}
        df_encoded = self.df.copy()
        
        for col in categorical_cols:
            if df_encoded[col].nunique() < 50:  # Only encode if reasonable number of categories
                encoders[col] = LabelEncoder()
                df_encoded[col] = encoders[col].fit_transform(df_encoded[col].astype(str))
        
        # Apply KNN imputation
        imputer = KNNImputer(n_neighbors=5)
        df_imputed = df_encoded.copy()
        df_imputed[numeric_cols + categorical_cols] = imputer.fit_transform(
            df_imputed[numeric_cols + categorical_cols]
        )
        
        # Decode categorical columns
        for col in categorical_cols:
            if col in encoders:
                df_imputed[col] = encoders[col].inverse_transform(df_imputed[col].astype(int))
        
        self.df = df_imputed
        self.changes_log.append("Applied KNN imputation for missing values")
        return self.df
    
    def suggest_cleaning(self):
        """Suggest cleaning operations based on data analysis"""
        suggestions = []
        
        # Check for missing values
        missing_values = self.df.isnull().sum()
        if missing_values.sum() > 0:
            cols_with_missing = missing_values[missing_values > 0].index.tolist()
            suggestions.append({
                'action': 'handle_missing',
                'columns': cols_with_missing,
                'message': f"{len(cols_with_missing)} columns have missing values"
            })
        
        # Check for duplicates
        if self.df.duplicated().sum() > 0:
            suggestions.append({
                'action': 'remove_duplicates',
                'message': f"{self.df.duplicated().sum()} duplicate rows found"
            })
        
        # Check for outliers in numeric columns
        numeric_cols = self.df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            suggestions.append({
                'action': 'check_outliers',
                'columns': numeric_cols.tolist(),
                'message': f"Potential outliers in {len(numeric_cols)} numeric columns"
            })
        
        return suggestions
    
    def get_changes_log(self):
        """Return list of changes made"""
        return self.changes_log
    
    def get_cleaned_data(self):
        """Return cleaned dataframe"""
        return self.df