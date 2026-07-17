import pandas as pd
#function to migrate it_tickets.csv data into the database
def migrate_it_tickets(conn):
    data = pd.read_csv('DATA/it_tickets.csv')
    data.to_sql('it_tickets', conn)
#function to retrieve all it tickets from the database
def get_all_it_tickets(conn):
    sql = 'SELECT * FROM it_tickets'
    data = pd.read_sql(sql, conn)
    
    return(data)