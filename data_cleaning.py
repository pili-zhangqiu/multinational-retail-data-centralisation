# Library imports
from datetime import date
from typing import List
from unidecode import unidecode

import numpy as np
import pandas as pd
import re
import string
import yaml

# Project class imports
from database_utils import DatabaseConnector
from data_extraction import DataExtractor


class DataCleaning():
    '''
    Utility class to clean data from specific data sources.
    '''
    def __init__(self):
        self.validation_utils = self.load_yaml('validation_utils.yaml')

    # ------------- Init utils-------------    
    def load_yaml(self, filepath: str) -> object:
        with open(filepath, 'r') as file:
            info = yaml.safe_load(file)
        return info

    # ------------- Main data cleansers -------------    
    def clean_user_data(self, df: pd.DataFrame):
        '''
        Clean the user data from NULL values, errors with dates, incorrectly typed values 
        and rows filled with the wrong information.
        '''
        # Clean columns
        df = self.clean_nulls(df)                               # Remove rows containing NULL values
        df = self.clean_user_dates(df)                          # Remove rows with errors in dates
        df = self.clean_names(df, 'first_name', 'last_name')    # Remove rows with incorrect formatting in first_name and last_name
        df = self.clean_phones(df, 'phone_number')              # Remove rows with wrong phone_number formatting

        # Final cleaning of nulls
        df = self.clean_nulls(df) 

        return df
    
    def clean_card_data(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        Clean card data, removing any erroneous values, NULL values or errors with formatting.
        '''
        # Clean columns
        df = self.clean_nulls(df)                       # Remove rows containing NULL values
        df = self.clean_card_dates(df)                  # Remove rows with errors in dates
        df = self.clean_card_number(df, 'card_number')  # Remove invalid card numbers

        # Final cleaning of nulls
        df = self.clean_nulls(df) 

        return df
    
    def called_clean_store_data(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        Clean store data, removing any erroneous values, NULL values or errors with formatting.
        '''
        df.drop(columns=['lat'], inplace=True)        # Remove the 'lat' column, as it seems to be an empty duplicate of 'latitude'

        # Clean store-specific columns
        df = self.clean_store_code(df)                # Remove rows containing invalid store codes

        # Clean other columns
        df = df.replace('eeEurope','Europe')       # Correct continent typo
        df = self.clean_country_codes(df)                   # Remove rows containing invalid or non-UN approved country codes
        df = self.clean_continents(df, 'continent')         # Remove rows containing wrong continent names
        df = self.remove_future_dates(df, 'opening_date')   # Remove rows containing invalid opening dates

        # Convert columns to numeric
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df['staff_numbers'] = pd.to_numeric(df['staff_numbers'], errors='coerce')

        return df
    
    def clean_products_data(self, df: pd.DataFrame) -> pd.DataFrame:
        '''
        Clean products data, removing any erroneous values, NULL values or errors with formatting.
        '''
        df = self.clean_nulls(df)                               # Remove rows containing NULL values

        # Convert all weights to a common measurement unit (kg)
        df = self.convert_product_weights(df, 'weight')
        df = df.rename(columns={'weight': 'weight_in_kg'})

        # Clean other columns
        df = self.clean_uuid(df, 'uuid')                 # Remove rows containing invalid UUID
        df = self.remove_future_dates(df, 'date_added')  # Remove rows containing invalid dates added

        # Final cleaning of nulls
        df = self.clean_nulls(df)          

        return df
    
    def clean_orders_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove unnecessary columns
        df = df.drop(columns=['first_name', 'last_name', '1', 'level_0'])
        
        # Remove rows containing NULL values
        df = self.clean_nulls(df)

        return df
    
    def clean_dates_data(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove rows containing NULL values
        df = self.clean_nulls(df)

        # Clean other columns
        df = self.clean_uuid(df, 'date_uuid')                 # Remove rows containing invalid UUID

        return df

    # ------------- General data cleaning utils -------------    
    def clean_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        # Remove rows with any value being NULL or NaN
        df.dropna(inplace=True)

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
    
    def remove_future_dates(self, df: pd.DataFrame, *column_names) -> pd.DataFrame:
        '''
        Remove any dates that are later than the current time in the given columns of the dataframe and return the
        cleaned dataframe.
        '''
        for column in column_names:
            # Remove rows with wrong date formatting
            df[column] = pd.to_datetime(df[column], errors='coerce', yearfirst=True).dt.date  
            #df.dropna(inplace=True)

            # Remove rows where dates are after the current date
            current_date = date.today()
            df = df[~(df[column] > current_date)]

        return df
    
    def clean_phones(self, df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        # Remove rows with wrong phone_number formatting
        regex_expression = '^(?:(?:\(?(?:0(?:0|11)\)?[\s-]?\(?|\+)44\)?[\s-]?(?:\(?0\)?[\s-]?)?)|(?:\(?0))(?:(?:\d{5}\)?[\s-]?\d{4,5})|(?:\d{4}\)?[\s-]?(?:\d{5}|\d{3}[\s-]?\d{3}))|(?:\d{3}\)?[\s-]?\d{3}[\s-]?\d{3,4})|(?:\d{2}\)?[\s-]?\d{4}[\s-]?\d{4}))(?:[\s-]?(?:x|ext\.?|\#)\d{3,4})?$'
        df.loc[~df[column_name].str.match(regex_expression), 'phone_number'] = np.nan         # For every row  where the Phone column does not match our regular expression, replace the value with NaN
        df.dropna(inplace=True)

        return df
    
    def clean_continents(self, df: pd.DataFrame, *column_names) -> pd.DataFrame:
        # Remove rows with invalid or wrong continent names
        for column in column_names:
            df = df[(df[column].apply(self.is_valid_continent))]
        return df
    
    def is_valid_continent(self, continent: str) -> bool:
        # Import valid country codes from yaml       
        continent_lowercase = continent.lower()
        if continent_lowercase in list(self.validation_utils['continent_list']):
            return True
        else: return False

    def clean_country_codes(self, df: pd.DataFrame, *column_names) -> pd.DataFrame:
        # Remove rows with non UN-approved country codes
        for column in column_names:
            df = df[(df[column].apply(self.is_valid_country_code))]
        return df
    
    def is_valid_country_code(self, country_code: str) -> bool:
        # Import valid country codes from yaml       
        country_code_uppercase = country_code.upper()
        if country_code_uppercase in list(self.validation_utils['un_country_list'].keys()):
            return True
        else: return False
    
    def convert_boolean(self, df: pd.DataFrame, column_names_arr: List[str], true_value: str, false_value: str) -> pd.DataFrame:
        '''
        Convert values in a dataframe column into boolean
        '''
        for column in column_names_arr:
            # Convert to lowercase for easy comparison
            true_value_lowercase = true_value.lower()
            false_value_lowercase = false_value.lower()

            # Convert to boolean
            df[column] = df[column].apply(self.is_true, args=(true_value_lowercase, false_value_lowercase))

        return df
    
    @staticmethod
    def is_true(string_to_check: str, true_value: str, false_value: str) -> bool:
        '''
        Returns whether the value should be True of False, given specifc values.
        '''
        string_to_check_lowercase = string_to_check.lower()

        if string_to_check_lowercase == true_value:
            return True
        elif string_to_check_lowercase == false_value:
            return False
        else: return 'NaN'
    
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

        # Convert to float
        df['latitude'] = pd.to_numeric(df['latitude'])
        df['longitude'] = pd.to_numeric(df['longitude'])

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
            if len(code_prefix) == 2 or len(code_prefix) == 3:
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

    # ------------- Product table specific data cleaning utils -------------    
    def convert_product_weights(self, df: pd.DataFrame, *column_names) -> pd.DataFrame:
        """
        Given a pandas dataframe, return a new dataframe with cleaned weight columns, where all values are represented in kg.

        For volumes, it uses a 1:1 ratio of ml to g as a rough estimate for the rows containing ml.
        """
        # Apply weight conversion function to all values in the given column
        for column in column_names:
            df[column] = df[column].apply(self.convert_to_kg)

        return df
    
    @staticmethod
    def convert_to_kg(weight: str) -> float:
        try:
            # Separate numeric value from units name (e.g. g, kg, ml)    
            value = re.split('\s*(?:kg|g|l|ml)', weight)[0]
            units = re.findall('\s*(?:kg|g|l|ml)', weight)[0]

            # Returned converted value
            if units == 'kg' or units == 'l':
                return round(float(value), 3)               # Assume 1:1 conversion ratio from l to kg
            elif units == 'g' or units == 'ml':
                return round((float(value) * 0.001), 3)     # Assume 1:1 conversion ratio from ml to g
            else:
                return 'NaN'
            
        except:
            return 'NaN'
    
    def convert_product_prices(self, df: pd.DataFrame, *column_names) -> pd.DataFrame:
        """
        Given a pandas dataframe, return a new dataframe with prices parsed and converted to pounds sterling (GBP).
        """
        # Convert product prices to float values representing GBP
        for column in column_names:
            df[column] = df[column].apply(self.convert_to_gbp)

        return df
    
    @staticmethod
    def convert_to_gbp(price: str) -> float:
        try:
            # Separate numeric value from units name (e.g. g, kg, ml)    
            value = re.split('\s*(?:£)', price)[1]
            units = re.findall('\s*(?:£)', price)[0]

            # Return value
            if units == '£':
                return round(float(value), 2)
            else:
                return 'NaN'
            
        except:
            return 'NaN'
    
    def clean_ean(self, df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        # Check if it's a valid EAN number: positive integer with 13 digits, , if not remove
        df = df[(df[column_name].apply(self.is_valid_ean))]

        return df
    
    @staticmethod
    def is_valid_ean(ean: str) -> bool:
        # Check that it is a positive integer number
        if ean.isnumeric():
            if int(ean) > 0:
                # Note: EAN codes in Europe are composed of 13 digits.
                if len(ean) == 13:
                    return True
        return False
    
    def clean_uuid(self, df: pd.DataFrame, column_name: str) -> pd.DataFrame:
        '''
        Remove rows with invalid UUIDs in the given columns and returns the cleaned dataframe.
        '''
        df = df[(df[column_name].apply(self.is_valid_uuid))]

        return df
    
    @staticmethod
    def is_valid_uuid(uuid: str) -> bool:
        '''
        Check if it's a valid UUID: 36 character alphanumeric string
        # (e.g. acde070d-8c4c-4f0d-9d8a-162843c10333), if not remove.
        '''
        try:
            # Split UUID
            uuid_split_arr = uuid.split('-')

            time_low = uuid_split_arr[0]
            time_mid = uuid_split_arr[1]
            time_hi_and_version = uuid_split_arr[2]
            clock_seq_hi_and_reserved = uuid_split_arr[3]
            mac_address = uuid_split_arr[4]

            # Check that lengths are correct
            if len(time_low)==8 and len(time_mid)==len(time_hi_and_version)==len(clock_seq_hi_and_reserved)==4 and len(mac_address)==12:
                # Check that all values are alphanumerical or hyphen
                valid_characters = list(string.ascii_lowercase) + [str(num) for num in range(10)] + ['-']
                uuid_lowercase = uuid.lower()
                for char in uuid_lowercase:
                    if char not in valid_characters:
                        print(f'Invalid char: {char}')
                        return False
                return True
            else: 
                return False
        
        except:
            return False
        
    def clean_product_code(self, df: pd.DataFrame) -> pd.DataFrame:
        # Check if it's a valid product code (e.g. U3-5148457q), if not remove
        df = df[(df['product_code'].apply(self.is_valid_product_code))]      

        return df

    @staticmethod
    def is_valid_product_code(product_code: str) -> bool:
        # Check if it's a valid product code (e.g. U3-5148457q)
        # Split code
        try:
            code_prefix = product_code.split('-')[0]
            code_suffix = product_code.split('-')[1]

            # First 2 chars should be letters
            if len(code_prefix) == 2:
                valid_characters_prefix = list(string.ascii_lowercase) + [str(num) for num in range(10)]
            
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
