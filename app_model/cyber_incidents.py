import pandas as pd
#function to migrate cyber_incidents.csv data into the database
def migrate_cyber_incidents(conn):
    data = pd.read_csv('DATA/cyber_incidents.csv')
    data.to_sql('cyber_incidents', conn)
#function to retrieve all it cyber incidents from the database
def get_all_cyber_incidents(conn):
    sql = 'SELECT * FROM cyber_incidents'
    data = pd.read_sql(sql, conn)
    
    return(data)