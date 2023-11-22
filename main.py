'''
Main file to create connections to databases (i.e. AWS), extract/process data
and upload to local database (i.e. PostgreSQL)
'''
from database_utils import DatabaseConnector
from data_cleaning import DataCleaning
from data_extraction import DataExtractor

if __name__ == '__main__':
    '''
    Extract, Process and Upload Data
    '''
    # Create connection to the databases
    connector_aws = DatabaseConnector('db_creds_aws.yaml')
    connector_local = DatabaseConnector('db_creds_local.yaml')

    # Prepare instances of extraction and cleaning utility classes
    extractor = DataExtractor()
    cleaner = DataCleaning()
    
    # ------------------ User Data ------------------
    # Extract table data
    read_table_name = 'legacy_users'
    df_user = extractor.read_rds_table(connector_aws, read_table_name)

    # Clean the data
    df_user = cleaner.clean_user_data(df_user)
    
    # Upload dataframe as table to the local PostgreSQL database
    connector_local.upload_to_db(df_user, 'dim_users')
    
    # ------------------ Card Data ------------------
    # Extract table data from PDF
    pdf_url = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf'
    df_card = extractor.retrieve_pdf_data(pdf_url)

    # Clean the data
    df_card = cleaner.clean_card_data(df_card)
    
    # Upload dataframe as table to the local PostgreSQL database
    connector_local.upload_to_db(df_card, 'dim_card_details')
