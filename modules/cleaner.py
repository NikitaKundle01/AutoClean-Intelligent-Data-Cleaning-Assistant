import pandas as pd
import numpy as np

class DataCleaner:
    def __init__(self, df):
        self.df = df.copy()
        self.changes_log = []
    
    def remove_duplicates(self, subset=None, keep='first'):
        """Remove duplicate rows"""
        initial_rows = len(self.df)
        self.df = self.df.drop_duplicates(subset=subset, keep=keep)
        removed = initial_rows - len(self.df)
        if removed > 0:
            self.changes_log.append(f"Removed {removed} duplicate rows")
        return self.df
    
    def drop_columns(self, columns_to_drop):
        """Drop specified columns"""
        if isinstance(columns_to_drop, str):
            columns_to_drop = [columns_to_drop]
        
        existing_cols = [col for col in columns_to_drop if col in self.df.columns]
        if existing_cols:
            self.df = self.df.drop(columns=existing_cols)
            self.changes_log.append(f"Dropped columns: {', '.join(existing_cols)}")
        return self.df
    
    def handle_missing_values(self, strategy='drop', columns=None, fill_value=None):
        """Handle missing values with various strategies"""
        if columns is None:
            columns = self.df.columns
        
        if strategy == 'drop':
            initial_rows = len(self.df)
            self.df = self.df.dropna(subset=columns)
            removed = initial_rows - len(self.df)
            if removed > 0:
                self.changes_log.append(f"Dropped {removed} rows with missing values")
        
        elif strategy == 'fill':
            if fill_value is not None:
                self.df[columns] = self.df[columns].fillna(fill_value)
                self.changes_log.append(f"Filled missing values with {fill_value}")
            else:
                for col in columns:
                    if self.df[col].dtype in ['int64', 'float64']:
                        fill_val = self.df[col].mean()
                        self.df[col] = self.df[col].fillna(fill_val)
                        self.changes_log.append(f"Filled missing values in {col} with mean: {fill_val:.2f}")
                    else:
                        fill_val = self.df[col].mode()[0]
                        self.df[col] = self.df[col].fillna(fill_val)
                        self.changes_log.append(f"Filled missing values in {col} with mode: {fill_val}")
        
        return self.df
    
    def rename_columns(self, column_mapping):
        """Rename columns based on provided mapping"""
        self.df = self.df.rename(columns=column_mapping)
        renamed_cols = [f"{old} → {new}" for old, new in column_mapping.items()]
        self.changes_log.append(f"Renamed columns: {', '.join(renamed_cols)}")
        return self.df
    
    def change_data_types(self, column_types):
        """Change data types of specified columns"""
        for col, dtype in column_types.items():
            if col in self.df.columns:
                try:
                    self.df[col] = self.df[col].astype(dtype)
                    self.changes_log.append(f"Changed {col} to {dtype}")
                except Exception as e:
                    self.changes_log.append(f"Failed to convert {col} to {dtype}: {str(e)}")
        return self.df
    
    def get_changes_log(self):
        """Return list of changes made"""
        return self.changes_log
    
    def get_cleaned_data(self):
        """Return cleaned dataframe"""
        return self.df