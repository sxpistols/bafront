import pandas as pd
import pymysql
from sqlalchemy import create_engine

cnx = create_engine('mysql+pymysql://employee:123@localhost/employee')    
df = pd.read_sql('SELECT * FROM karyawan', cnx)

print(df)
