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

    def clean_user_data(self, df: pd.DataFrame):
        '''
        Clean the user data from NULL values, errors with dates, incorrectly typed values 
        and rows filled with the wrong information.
        '''
        # Remove all rows containing NULL values
        df = df.dropna()

        # Remove all rows with errors in dates
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce').dt.date  # Remove wrong date formatting
        df['join_date'] = pd.to_datetime(df['join_date'], errors='coerce').dt.date

        df = df[~(df['join_date'] < df['date_of_birth'])]   # Remove rows where joint_date is after date_of_birth

        current_date = date.today()                         # Remove rows where dates are after the current date
        df = df[~(df['date_of_birth'] > current_date)]
        df = df[~(df['join_date'] > current_date)]

        # Remove rows with incorrect formatting in first_name and last_name
        df = df[(df['first_name'].apply(self.is_valid_name))]
        df = df[(df['last_name'].apply(self.is_valid_name))]

        # TODO: Doesnt seem to do anything
        # Remove rows with wrong phone_number formatting
        regex_expression = '^(?:(?:\(?(?:0(?:0|11)\)?[\s-]?\(?|\+)44\)?[\s-]?(?:\(?0\)?[\s-]?)?)|(?:\(?0))(?:(?:\d{5}\)?[\s-]?\d{4,5})|(?:\d{4}\)?[\s-]?(?:\d{5}|\d{3}[\s-]?\d{3}))|(?:\d{3}\)?[\s-]?\d{3}[\s-]?\d{3,4})|(?:\d{2}\)?[\s-]?\d{4}[\s-]?\d{4}))(?:[\s-]?(?:x|ext\.?|\#)\d{3,4})?$'
        df.loc[~df['phone_number'].str.match(regex_expression), 'phone_number'] = np.nan         # For every row  where the Phone column does not match our regular expression, replace the value with NaN

        print(df)

        return df

    @staticmethod
    def is_valid_name(name: str):
        valid_name_characters = list(string.ascii_lowercase) + list(string.ascii_uppercase) + list(['-', ' '])
        
        name_without_accents = unidecode(name)
        for char in name_without_accents:
            if char not in valid_name_characters:
                return False
        return True


if __name__ == '__main__':
    connector = DatabaseConnector('db_creds.yaml')
    
    table_name = 'legacy_users'
    extractor = DataExtractor()
    df = extractor.read_rds_table(connector, table_name)

    cleaner = DataCleaning()
    cleaner.clean_user_data(df)


