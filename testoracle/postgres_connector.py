from sqlalchemy import create_engine,text,MetaData
import pandas as pd
import psycopg2
from sqlalchemy.dialects.postgresql import insert
# from dotenv import load_dotenv
# load_dotenv()
from urllib.parse import quote

import os 
class PostgresConnector:
    def __init__(self,schema='public') -> None:
        self.username = 'sireetron'
        self.password = 'srt@2025'
        self.host = '192.169.10.41'
        self.db_name  = 'collection_oa'
        self.port = 5423
        self.engine = create_engine(f"postgresql://{self.username}:{quote(self.password)}@{self.host}:{self.port}/{self.db_name}", connect_args={'options': '-csearch_path={}'.format(schema)}) 
        self.connection = None
        self.cursor = None
        self.schema = schema

        pass
    def execute(self,query):
        with self.engine.connect() as conn:
            return conn.execute(text(query))
    def connect(self):
        print(self.password)
        self.connection = psycopg2.connect(    
            host=self.host,
            port=self.port,
            database=self.db_name,
            user=self.username,
            password=self.password,
        )
        self.connection.set_session(autocommit=True)
        self.cursor = self.connection.cursor()
        print("Connected to PostgreSQL server!")
        return self.cursor
    
    def close_connection(self):
        self.connection.close() 
        print("Disconnected from PostgreSQL server!")
    
    def upsert(self, df, table,chunk_size,constraint):
        if(not self.connection): self.connect()
        
        for chunk_start in range(0, len(df), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(df))
            chunk_df = df.iloc[chunk_start:chunk_end]
            
            query_insert = ""
            for _, row in chunk_df.iterrows():
                quoted_columns = [f'"{col}"' for col in df.columns]

                query_insert += f"INSERT INTO {table} ({', '.join(quoted_columns)}) VALUES ("
                for col in df.columns:
                    value = row[col]
                    if pd.isnull(value):
                        query_insert += "NULL, "
                    else:
                        query_insert += f"'{value}', "
                query_insert = query_insert.rstrip(', ') + f") ON CONFLICT ON CONSTRAINT {constraint} DO NOTHING; "
                # query_insert = query_insert.rstrip(', ') + f') ON CONFLICT ("{constraint}") DO NOTHING;
            self.cursor.execute(query_insert)
            
            
    def upserttt(self, df, table, chunk_size, conflict_column):
        if not self.connection:
            self.connect()

        for chunk_start in range(0, len(df), chunk_size):
            chunk_end = min(chunk_start + chunk_size, len(df))
            chunk_df = df.iloc[chunk_start:chunk_end]

            for _, row in chunk_df.iterrows():
                columns = list(df.columns)
                quoted_columns = [f'"{col}"' for col in columns]
                values = []

                for col in columns:
                    val = row[col]
                    if pd.isnull(val):
                        values.append("NULL")
                    else:
                        # Escape single quotes
                        values.append(f"'{str(val).replace("'", "''")}'")

                insert_part = f"INSERT INTO {table} ({', '.join(quoted_columns)})"
                values_part = f"VALUES ({', '.join(values)})"

                # Build update part, excluding conflict column
                update_columns = [col for col in columns if col != conflict_column]
                update_part = ', '.join([f'"{col}" = EXCLUDED."{col}"' for col in update_columns])

                query = f"""
                    {insert_part}
                    {values_part}
                    ON CONFLICT ("{conflict_column}")
                    DO UPDATE SET {update_part};
                """
                self.cursor.execute(query)




    def hello(self):
        print('hello')
    def get_engine(self):
        return self.engine
    

def upsert(engine,constraint,table, conn, keys, data_iter):
    meta = MetaData()
    meta.bind = engine
    meta.reflect(views=True)
    upsert_args = {"constraint": constraint}
    for data in data_iter:
        data = {k: data[i] for i, k in enumerate(keys)}
        upsert_args["set_"] = data
        insert_stmt = insert(meta.tables[table.name]).values(**data)
        upsert_stmt = insert_stmt.on_conflict_do_update(**upsert_args)
        conn.execute(upsert_stmt)

def incremental_insert(engine,constraint,table, conn, keys, data_iter):
    meta = MetaData()
    meta.bind = engine
    meta.reflect(views=True)
    upsert_args = {"constraint": constraint}
    for data in data_iter:
        data = {k: data[i] for i, k in enumerate(keys)}
        # upsert_args["set_"] = data
        insert_stmt = insert(meta.tables[table.name]).values(**data)
        upsert_stmt = insert_stmt.on_conflict_do_nothing(**upsert_args)
        conn.execute(upsert_stmt)