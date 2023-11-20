import yaml

from sqlalchemy import Engine, create_engine, inspect

class DatabaseConnector():
    '''
    Utility class to connect and upload data to a database.
    
    Parameters:
    ----------
    credentials_filepath: str
        Path to the credentials yaml file

    Methods:
    -------
    read_db_creds()
        Read the credentials yaml file and return a dictionary of the credentials.
    init_db_engine()
        Initialise and return a database engine using the credentials input into the class.
    list_db_tables()
        Prints the names of the different tables in each database schema. It also returns a dictionary containing each schemas' tables.
    '''
    def __init__(self, credentials_filepath: str) -> None:
        self.credentials_filepath = credentials_filepath
        self.credentials = self.read_db_creds()
        self.engine = self.init_db_engine()
        self.db_tables = {}
        
    def read_db_creds(self) -> dict:
        '''
        Read the credentials yaml file and return a dictionary of the credentials.

        Returns:
        -------
        credentials: dict
            Dictionary containing the credentials
        '''
        with open(self.credentials_filepath, 'r') as file:
            credentials = yaml.safe_load(file)

        return credentials

    def init_db_engine(self) -> Engine:
        '''
        Read the credentials from the input filepath. Then, initialise and return 
        an sqlalchemy database engine.

        Returns:
        -------
        engine: Engine
            PostgreSQL database engine
        '''
        # Define the database credentials
        host=self.credentials['RDS_HOST']
        port=self.credentials['RDS_PORT']
        database=self.credentials['RDS_DATABASE']
        user=self.credentials['RDS_USER']
        password=self.credentials['RDS_PASSWORD']

        # Try to create engine
        try: 
            engine = create_engine(
                url="postgresql://{0}:{1}@{2}:{3}/{4}".format(user, password, host, port, database)
            )
            print(f"Connection to the '{host}' for user '{user}' created successfully.")
            return engine

        except Exception as ex:
            print("Connection could not be made due to the following error: \n", ex)
    
    def list_db_tables(self) -> dict:
        '''
        Prints a list of all the tables in each schema of the database and record them.

        Returns:
        -------
        self.db_tables: dict
            Dictionary contain an array of table names for each schema
        '''
        # Create inspector item for the database
        inspector = inspect(self.engine)
        schemas = inspector.get_schema_names()

        # Loop through the differents schemas, then print and store the tables names
        print("List of tables in database:")
        for schema in schemas:
            print("Schema: %s" % schema)
            tables = inspector.get_table_names(schema=schema)

            # Print the name of the tables for the schema
            for table_id in range(len(tables)):
                print("-> Table: %s" % tables[table_id])
            
            # Store table names for the specific schema in the dictionary
            self.db_tables[schema] = tables
        
        return self.db_tables
            

if __name__ == '__main__':
    connector = DatabaseConnector('db_creds.yaml')
    connector.list_db_tables()
