import pandas as pd
import requests
import yaml
from tabula.io import read_pdf

from database_utils import DatabaseConnector

class DataExtractor():
    '''
    Utility class to extract data from multiple sources, including: CSV files, APIs and S3 buckets.
    '''
    def __init__(self):
        '''
        Initialise DataExtractor class and load class variables
        '''
        self._api_stores_headers = {
            'x-api-key': self.retrieve_creds('db_creds_aws_api.yaml')['X_API_KEY']
            }
        self._api_stores_base_url = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod'

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
    
    def retrieve_creds(self, filepath: str) -> dict:
        '''
        Returns credential data from a YAML file given its path and key name.

        Parameters:
        ----------
        filepath: str
            Filepath to the credentials YAML

        Returns:
        -------
        creds: dict
            Authentication credentials from YAML file
        '''
        # Parse YAML
        with open(filepath, 'r') as file:
            creds = yaml.safe_load(file)
        return creds
    
    def list_number_of_stores(self) -> int:
        '''
        Returns the number of stores to extract. It should take in the number of stores endpoint and header dictionary as an argument.
        '''
        # Send a GET request to the API
        endpoint_url = f'{self._api_stores_base_url}/number_stores'
        headers = self._api_stores_headers

        response = requests.get(endpoint_url, headers=headers)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Access the response data as JSON
            data = response.json()
            num_stores = int(data['number_stores'])
            print(f'Total number of stores is {num_stores}')
            return num_stores

        # If the request was not successful, print the status code and response text
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Response Text: {response.text}")
            raise requests.exceptions.RequestException("Request failed")
    
    def retrieve_store_data(self, store_id: int) -> pd.DataFrame:
        # Send a GET request to the API
        endpoint_url = f'{self._api_stores_base_url}/store_details/{store_id}'
        headers = self._api_stores_headers

        response = requests.get(endpoint_url, headers=headers)

        # Check if the request was successful (status code 200). If so, return data.
        if response.status_code == 200:
            return pd.json_normalize(response.json())

        # If the request was not successful, print the status code and response text
        else:
            print(f"Request failed with status code: {response.status_code}")
            print(f"Response Text: {response.text}")
            raise requests.exceptions.RequestException("Request failed")
        
    def retrieve_stores_data(self) -> pd.DataFrame:
        '''
        Extracts and returns all the stores from the API in a pandas Dataframe format.
        '''
        # Get number of stores from API
        num_stores = self.list_number_of_stores()

        # Loop through all stores and save the data
        stores_data = []
        for store_id in range(1,num_stores):
            store_data = self.retrieve_store_data(store_id)
            print(store_data)
            stores_data.append(store_data)

        return stores_data

if __name__ == '__main__':
    connector = DatabaseConnector('db_creds_aws_rds.yaml')
    
    table_name = 'legacy_users'
    extractor = DataExtractor()
    extractor.read_rds_table(connector, table_name)
    