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

    # ------------- Table-specific data cleaning utils -------------    
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
        
    # ------------- General data cleaning utils -------------    
    def clean_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove rows with any value being NULL or NaN
        df = df.dropna()

        # Remove rows with any value being a string 'NULL'
        df = df[~df.isin(['NULL', 'null', 'Null']).any(axis=1)]

        return df
    
    def clean_names(self, df:pd.DataFrame, *column_names) -> pd.DataFrame:
        # Remove rows with incorrect formatting
        for column in column_names:
            df = df[(df[column].apply(self.is_valid_name))]

        return df

    @staticmethod
    def is_valid_name(name: str):
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

    def clean_card_number(self, df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        # Check if it's a valid card number: positive integer with 8 to 19 digits
        df = df[(df[column_name].apply(self.is_valid_card_number))]

        return df
    
    @staticmethod
    def is_valid_card_number(card_number: str):
        # Check that it is a positive integer number
        if card_number.isnumeric():
            if int(card_number) > 0:
                # Note: Payment card numbers are composed of 8 to 19 digits.
                if len(card_number) >= 8 and len(card_number) <= 19:
                    return True
        return False

if __name__ == '__main__':
    connector = DatabaseConnector('db_creds_aws.yaml')
    
    table_name = 'legacy_users'
    extractor = DataExtractor()
    df = extractor.read_rds_table(connector, table_name)

    cleaner = DataCleaning()
    df = cleaner.clean_user_data(df)
    print(df)
