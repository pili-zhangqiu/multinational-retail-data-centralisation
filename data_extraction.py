import pandas as pd
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

if __name__ == '__main__':
    connector = DatabaseConnector('db_creds_aws_rds.yaml')
    
    table_name = 'legacy_users'
    extractor = DataExtractor()
    extractor.read_rds_table(connector, table_name)
    