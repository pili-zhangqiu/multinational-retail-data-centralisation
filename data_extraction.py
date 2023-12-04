import boto3
import os
import pandas as pd
import requests
import sys
import yaml

from tabula.io import read_pdf

from database_utils import DatabaseConnector

class DataExtractor():
    '''
    Utility class to extract data from multiple sources, including: CSV files, APIs and S3 buckets.
    '''
    def __init__(self, aws_credentials_filepath: str):
        '''
        Initialise DataExtractor class and load class variables
        '''
        # Parameters to receive data from the AWS API - Store data
        self._api_stores_headers = {
            'x-api-key': self.retrieve_creds('db_creds_aws_api.yaml')['X_API_KEY']
            }
        self._api_stores_base_url = 'https://aqj7u5id95.execute-api.eu-west-1.amazonaws.com/prod'

        # Parameters to receive data from the AWS S3 Bucket - Product data
        self._aws_access_key = self.read_db_creds(aws_credentials_filepath)['AWS_ACCESS_KEY']
        self._aws_secret_key = self.read_db_creds(aws_credentials_filepath)['AWS_SECRET_ACCESS_KEY']

    def read_db_creds(self, credentials_filepath) -> dict:
        '''
        Read the credentials yaml file and return a dictionary of the credentials.
        '''
        with open(credentials_filepath, 'r') as file:
            credentials = yaml.safe_load(file)

        return credentials

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
        for store_id in range(num_stores):
            # Get store details and append to list
            store_data = self.retrieve_store_data(store_id)
            stores_data.append(store_data)

            # Print progress
            retrieval_progress_pct = round(((store_id + 1) / num_stores * 100))
            sys.stdout.write(f'\rRetrieving data from stores... {retrieval_progress_pct}% ({store_id}/{num_stores})')
            sys.stdout.flush()

        df_stores_data = pd.concat(stores_data)
        return df_stores_data
    
    def extract_from_s3(self, s3_url: str) -> pd.DataFrame:
        '''
        Download and extract the information from an AWS S3 bucket and return a pandas dataframe.
        This is in the format: s3://{bucket}/{key} , where the file to be parsed must be a .csv or .json.
        '''
        # Parse url
        bucket = s3_url.split('/')[2]
        if '.' in bucket:
            bucket = bucket.split('.')[0]

        key = s3_url.split('/')[3]
        download_dir = 's3_downloads'
        download_filepath = f"{download_dir}/{key}"

        # Check whether the specified path exists or not
        isExist = os.path.exists(download_dir)
        if not isExist:     
            os.makedirs(download_dir)   # Create a new directory if it does not exist
            print(f"Created a new directory to store S3 Bucket data: {download_dir}")

        # Load AWS credentials and S3 client
        s3 = boto3.client('s3',
            aws_access_key_id=self._aws_access_key,
            aws_secret_access_key= self._aws_secret_key)
        
        # Download file
        s3.download_file(bucket, key, download_filepath)

        # Convert to pandas dataframe
        if key.split('.')[1] == 'csv':
            return pd.read_csv(download_filepath)
        elif key.split('.')[1] == 'json':
            return pd.read_json(download_filepath)
        else:
            raise TypeError('Cannot parse file! The file format must be a .csv or .json')


if __name__ == '__main__':
    connector = DatabaseConnector('db_creds_aws_rds.yaml')
    
    table_name = 'legacy_users'
    extractor = DataExtractor()
    extractor.read_rds_table(connector, table_name)
    