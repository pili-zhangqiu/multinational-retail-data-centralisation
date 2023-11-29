import pandas as pd
import requests
from tabula.io import read_pdf

from database_utils import DatabaseConnector

class DataExtractor():
    '''
    Utility class to extract data from multiple sources, including: CSV files, APIs and S3 buckets.
    '''
    def __init__(self):
        pass

    def read_rds_table(self, db_connector: DatabaseConnector, table_name: str) -> pd.DataFrame:
        '''
        Extract the database table to a pandas DataFrame.
        '''
        table = pd.read_sql_table(table_name, db_connector.engine)

        return table
    
    def retrieve_pdf_data(self, url: str) -> pd.DataFrame:
        '''
        Extract data from from a table in a PDF file, given a URL link. Then, return a Pandas
        DataFrame with the table information.
        '''
        # Read remote pdf into a list of DataFrame
        extracted_data = read_pdf(url, multiple_tables=True, pages="all", output_format="dataframe")

        # Convert to Pandas dataframe
        df = extracted_data[0]
        
        return df 
    
    def list_number_of_stores(self, endpoint_url: str, headers: dict) -> int:
        '''
        Returns the number of stores to extract. It should take in the number of stores endpoint and header dictionary as an argument.
        '''
        # Send a GET request to the API
        response = requests.get(endpoint_url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Access the response data as JSON
            data = response.json()
            return data

        # If the request was not successful, print the status code and response text
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Response Text: {response.text}")   

if __name__ == '__main__':
    connector = DatabaseConnector('db_creds_aws_rds.yaml')
    
    table_name = 'legacy_users'
    extractor = DataExtractor()
    extractor.read_rds_table(connector, table_name)
    