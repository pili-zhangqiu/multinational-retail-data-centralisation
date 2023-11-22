import pandas as pd
from tabula import read_pdf

from database_utils import DatabaseConnector

class DataExtractor():
    '''
    Utility class to extract data from multiple sources, including: CSV files, APIs and S3 buckets.
    '''
    def __init__(self):
        pass

    def read_rds_table(self, db_connector: DatabaseConnector, table_name: str):
        '''
        Extract the database table to a pandas DataFrame.
        '''
        table = pd.read_sql_table(table_name, db_connector.engine)

        return table
    
    def retrieve_pdf_data(self, url: str):
        '''
        Extract data from from a table in a PDF file, given a URL link. Then, return a Pandas
        DataFrame with the table information.
        '''
        # Read remote pdf into a list of DataFrame
        df = read_pdf(url)

        return df 

if __name__ == '__main__':
    connector = DatabaseConnector('db_creds_aws.yaml')
    
    table_name = 'legacy_users'
    extractor = DataExtractor()
    extractor.read_rds_table(connector, table_name)
    