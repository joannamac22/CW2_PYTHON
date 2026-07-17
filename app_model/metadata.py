import pandas as pd
#function to migrate datasets_metadata.csv data into the database
def migrate_datasets_metadata(conn):
    data = pd.read_csv('DATA/datasets_metadata.csv')
    data.to_sql('datasets_metadata', conn)
#function to retrieve all datasets metadata from the database
def get_all_datasets_metadata(conn):
    sql = 'SELECT * FROM datasets_metadata'
    data = pd.read_sql(sql, conn)
    
    return(data)