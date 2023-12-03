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
    connector_aws_rds = DatabaseConnector('db_creds_aws_rds.yaml')
    connector_local = DatabaseConnector('db_creds_local.yaml')

    # Prepare instances of extraction and cleaning utility classes
    extractor = DataExtractor('db_creds_aws_sso.yaml')
    cleaner = DataCleaning()
    
    # ------------------ User Data ------------------
    '''    
    print('\n----- USER DATA: -----')

    # Extract table data
    read_table_name = 'legacy_users'
    
    print('Reading user data from database...')
    df_user = extractor.read_rds_table(connector_aws_rds, read_table_name)
    print('DONE \n')

    # Clean the data
    print('Cleaning user data...')
    df_user = cleaner.clean_user_data(df_user)
    print('DONE \n')

    # Upload dataframe as table to the local PostgreSQL database
    print('Uploading dataframe to local database...')
    connector_local.upload_to_db(df_user, 'dim_users')
    '''
    
    # ------------------ Card Data ------------------
    '''
    print('\n----- CARD DATA: -----')

    # Extract table data from PDF
    pdf_url = 'https://data-handling-public.s3.eu-west-1.amazonaws.com/card_details.pdf'
    
    print('Extracting table from PDF...')
    df_card = extractor.retrieve_pdf_data(pdf_url)
    print('DONE \n')

    # Clean the data
    print('Cleaning card data...')
    df_card = cleaner.clean_card_data(df_card)
    print('DONE \n')

    # Upload dataframe as table to the local PostgreSQL database
    print('Uploading dataframe to local database...')
    connector_local.upload_to_db(df_card, 'dim_card_details')
    '''

    # ------------------ Store Data ------------------
    '''    
    print('\n----- STORE DATA: -----')

    # Retrieve data from all stores   
    df_stores = extractor.retrieve_stores_data()
    
    # Clean stores data
    print('\nCleaning store data...')
    df_stores = cleaner.called_clean_store_data(df_stores)
    
    # Upload dataframe as table to the local PostgreSQL database
    print('\nUploading dataframe to local database...')
    connector_local.upload_to_db(df_stores, 'dim_store_details')
    '''

    # ------------------ Product Data ------------------
    df_products = extractor.extract_from_s3('s3://data-handling-public/products.csv')
    
    df_products = cleaner.clean_products_data(df_products)
