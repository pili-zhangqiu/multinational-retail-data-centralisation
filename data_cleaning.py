import numpy as np
import pandas as pd
import string

from datetime import date
from typing import List
from unidecode import unidecode

from database_utils import DatabaseConnector
from data_extraction import DataExtractor

class DataCleaning():
    '''
    Utility class to clean data from specific data sources.
    '''
    def __init__(self):
            pass

    # ------------- Main data cleansers -------------    
    def clean_user_data(self, df: pd.DataFrame):
        '''
        Clean the user data from NULL values, errors with dates, incorrectly typed values 
        and rows filled with the wrong information.
        '''
        # Remove all rows containing NULL values
        df = self.clean_nulls(df)

        # Remove all rows with errors in dates
        df = self.clean_user_dates(df)

        # Remove rows with incorrect formatting in first_name and last_name
        df = self.clean_names(df, 'first_name', 'last_name')

        # Remove rows with wrong phone_number formatting
        df = self.clean_phones(df, 'phone_number')

        return df
    
    def clean_card_data(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        Clean card data, removing any erroneous values, NULL values or errors with formatting.
        '''
        # Remove all rows containing NULL values
        df = self.clean_nulls(df)

        # Remove all rows with errors in dates
        df = self.clean_card_dates(df)

        # Remove invalid card numbers
        df = self.clean_card_number(df, 'card_number')

        return df
    
    def called_clean_store_data (self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        Clean store data, removing any erroneous values, NULL values or errors with formatting.
        '''
        # Remove the 'lat' column, as it seems to be an empty duplicate of 'latitude'
        df.drop(columns=['lat'], inplace=True)

        # Remove all rows containing NULL values
        df = self.clean_nulls(df)
        
        # Remove all rows containing invalid latitude or longitude
        df = self.clean_lat_lon(df)

        # Remove all rows containing invalid localities
        df = self.clean_names(df, 'locality')
        print(df)
        print(' ')

        # Remove all rows containing invalid store codes
        df = self.clean_store_code(df)
        print(df)

        return df

    # ------------- General data cleaning utils -------------    
    def clean_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove rows with any value being NULL or NaN
        df = df.dropna()

        # Remove rows with any value being a string 'NULL'
        for column in list(df.columns.values):
            df = df[~(df[column].apply(self.is_null_str))]
            
        return df
    
    @staticmethod
    def is_null_str(var: str) -> bool:
        var_str =  str(var)
        var_str_lowercase = var_str.lower()
        
        list_null_str = ['null', 'none', 'n/a', 'nan']
        
        if var_str_lowercase in list_null_str:
            return True
        else:
            return False   
    
    def clean_names(self, df:pd.DataFrame, *column_names) -> pd.DataFrame:
        # Remove rows with incorrect formatting
        for column in column_names:
            df = df[(df[column].apply(self.is_valid_name))]

        return df

    @staticmethod
    def is_valid_name(name: str) -> bool:
        valid_name_characters = list(string.ascii_lowercase) + list(string.ascii_uppercase) + list(['-', ' '])
        
        name_without_accents = unidecode(name)
        for char in name_without_accents:
            if char not in valid_name_characters:
                return False
        return True

    def clean_phones(self, df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        # Remove rows with wrong phone_number formatting
        regex_expression = '^(?:(?:\(?(?:0(?:0|11)\)?[\s-]?\(?|\+)44\)?[\s-]?(?:\(?0\)?[\s-]?)?)|(?:\(?0))(?:(?:\d{5}\)?[\s-]?\d{4,5})|(?:\d{4}\)?[\s-]?(?:\d{5}|\d{3}[\s-]?\d{3}))|(?:\d{3}\)?[\s-]?\d{3}[\s-]?\d{3,4})|(?:\d{2}\)?[\s-]?\d{4}[\s-]?\d{4}))(?:[\s-]?(?:x|ext\.?|\#)\d{3,4})?$'
        df.loc[~df[column_name].str.match(regex_expression), 'phone_number'] = np.nan         # For every row  where the Phone column does not match our regular expression, replace the value with NaN
        df = df.dropna()

        return df
    
    def is_alphabetical(self, var: str) -> bool:
        '''
        Check if a string only contains alphabetical characters
        '''
        valid_characters = list(string.ascii_lowercase)
        
        var_lowercase = var.lower()
        for char in var_lowercase:
            if char not in valid_characters:
                return False
        return True
    
    def is_float(self, var: str) -> bool:
        '''
        Check if a string can be coverted to a float
        '''
        try:
            float(var)
            return True
        except ValueError:
            return False
    
    def is_int(self, var: str) -> bool:
        '''
        Check if a string can be coverted to an int
        '''
        # Make sure it doesn't have decimal places
        for char in var:
            if char == '.':
                return False
        
        # Check if it's numerical
        try:
            int(var)
            return True
        except ValueError:
            return False
        
    # ------------- User table specific data cleaning utils -------------    
    def clean_user_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove rows with wrong date formatting
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce').dt.date  
        df['join_date'] = pd.to_datetime(df['join_date'], errors='coerce').dt.date

        # Remove rows where joint_date is after date_of_birth
        df = df[~(df['join_date'] < df['date_of_birth'])]

        # Remove rows where dates are after the current date
        current_date = date.today()
        df = df[~(df['date_of_birth'] > current_date)]
        df = df[~(df['join_date'] > current_date)]

        return df
    
    # ------------- Card table specific data cleaning utils -------------    
    def clean_card_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove rows with wrong date formatting
        df['expiry_date'] = pd.to_datetime(df['expiry_date'], format='%m/%y', errors='coerce').dt.date  
        df['date_payment_confirmed'] = pd.to_datetime(df['date_payment_confirmed'], errors='coerce').dt.date

        # NOTE: Do we want to check if a payment was made after expiry date? Maybe it's not part of what the
        # data cleaning function should do

        # Remove rows where dates are before or after the current date
        current_date = date.today()
        # df = df[~(df['expiry_date'] < current_date)]    # NOTE: Keeping expired card data as it might be useful
        df = df[~(df['date_payment_confirmed'] > current_date)]

        return df
    
    def clean_card_number(self, df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        # Check if it's a valid card number: positive integer with 8 to 19 digits, , if not remove
        df = df[(df[column_name].apply(self.is_valid_card_number))]

        return df
    
    @staticmethod
    def is_valid_card_number(card_number: str) -> bool:
        # Check that it is a positive integer number
        if card_number.isnumeric():
            if int(card_number) > 0:
                # Note: Payment card numbers are composed of 8 to 19 digits.
                if len(card_number) >= 8 and len(card_number) <= 19:
                    return True
        return False

    # ------------- Store table specific data cleaning utils -------------    
    def clean_lat_lon(self, df: pd.DataFrame) -> pd.DataFrame:
        # Check if it's a valid latitude and longitude, if not remove
        df = df[(df['latitude'].apply(self.is_valid_lat))]
        df = df[(df['longitude'].apply(self.is_valid_lon))]
        
        return df
      
    def is_valid_lat(self, latitude: str) -> bool:
        # Check it is a numeric value
        if self.is_float(latitude):
            # Check it is in the correct range (-90 to 90 deg)
            if -90 <= float(latitude) <= 90:
                return True
            else: 
                return False
        else:
            return False
          
    def is_valid_lon(self, longitude: str) -> bool:
        # Check it is a numeric value
        if self.is_float(longitude):
            # Check it is in the correct range (-180 to 180 deg)
            if -180 <= float(longitude) <= 180:
                return True
            else: 
                return False
        else:
            return False
    
    def clean_store_code(self, df: pd.DataFrame) -> pd.DataFrame:
        # Check if it's a valid store code (e.g. CH-99475026), if not remove
        df = df[(df['store_code'].apply(self.is_valid_store_code))]        
        return df

    @staticmethod
    def is_valid_store_code(store_code: str) -> bool:
        # Check if it's a valid store code (e.g. CH-99475026)
        # Split code
        try:
            code_prefix = store_code.split('-')[0]
            code_suffix = store_code.split('-')[1]

            # First 2 chars should be letters
            if len(code_prefix) == 2:
                valid_characters_prefix = list(string.ascii_lowercase)
            
                prefix_lowercase = code_prefix.lower()
                for char in prefix_lowercase:
                    if char not in valid_characters_prefix:
                        return False
            else: return False
        
            # Last 8 chars can be a mix of alphabetical letters and numbers
            if len(code_suffix) == 8:
                valid_characters_suffix = list(string.ascii_lowercase) +  [str(num) for num in range(10)]
            
                suffix_lowercase = code_suffix.lower()
                for char in suffix_lowercase:
                    if char not in valid_characters_suffix:
                        return False
            else: return False

            return True
        
        except IndexError:
            return False

        

if __name__ == '__main__':
    connector = DatabaseConnector('db_creds_aws_rds.yaml')
    
    table_name = 'legacy_users'
    extractor = DataExtractor()
    df = extractor.read_rds_table(connector, table_name)

    cleaner = DataCleaning()
    df = cleaner.clean_user_data(df)
    print(df)
