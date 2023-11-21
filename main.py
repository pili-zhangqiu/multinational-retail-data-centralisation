'''
Main file to create connections to databases (i.e. AWS), extract/process data
and upload to local database (i.e. PostgreSQL)
'''
from database_utils import DatabaseConnector
from data_cleaning import DataCleaning
from data_extraction import DataExtractor

if __name__ == '__main__':
    # Create connection to the database
    connector_aws = DatabaseConnector('db_creds_aws.yaml')
    
    # Extract table data
    read_table_name = 'legacy_users'
    extractor = DataExtractor()
    df = extractor.read_rds_table(connector_aws, read_table_name)

    # Clean the data
    cleaner = DataCleaning()
    df = cleaner.clean_user_data(df)
    
    # Upload dataframe as table to the database
    connector_local = DatabaseConnector('db_creds_local.yaml')
    upload_table_name = 'dim_users'
    connector_local.upload_to_db(df, upload_table_name)
    