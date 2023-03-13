#!/usr/bin/python

import os
import aiofiles
import base64
import os
import io
import pandas as pd
from pandas.io.json import json_normalize
import numpy as np
import json
import sqlalchemy
from sqlalchemy import create_engine, text 
from sqlalchemy.types import NVARCHAR, VARCHAR, String, CHAR
from sqlalchemy.inspection import inspect
import datetime as dt
import time

parent_dir_path = os.path.dirname(os.path.realpath(__file__))

POSTGRES_DB = os.environ.get('POSTGRES_DB')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')

engine = create_engine(f'postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@bravo_database/{POSTGRES_DB}')

def keepalive():
    keepalive_df = pd.read_sql_query(text('''SELECT CURRENT_TIMESTAMP as "realtime_data";'''), con=engine)
    return keepalive_df

def load_csv(file_name):
    df = pd.read_csv(f'./shared_volume/{file_name}')
    df.to_sql(file_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

def load_excel(file_name):
    xls = pd.ExcelFile(f'./shared_volume/{file_name}')
    for table_name in xls.sheet_names:
        df = pd.read_excel(f'./shared_volume/{file_name}', sheet_name=table_name)
        df.to_sql(table_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

def load_json(file_name):
    with open(f'./shared_volume/{file_name}') as f:
        data = json.load(f)
        df = json_normalize(data)
        df.to_sql(file_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

def load_sql(file_name):
    with open(f'./shared_volume/{file_name}') as f:
        sql = f.read()
        df = pd.read_sql_query(text(sql), con=engine)
        df.to_sql(file_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

def load_sql_query(file_name):
    with open(f'./shared_volume/{file_name}') as f:
        sql = f.read()
        df = pd.read_sql_query(text(sql), con=engine)
        df.to_sql(file_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

def load_sql_query_with_params(file_name, params):
    with open(f'./shared_volume/{file_name}') as f:
        sql = f.read()
        df = pd.read_sql_query(text(sql), con=engine, params=params)
        df.to_sql(file_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

def load_parquet(file_name):
    df = pd.read_parquet(f'./shared_volume/{file_name}')
    df.to_sql(file_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

def load_pickle(file_name):
    df = pd.read_pickle(f'./shared_volume/{file_name}')
    df.to_sql(file_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

def load_tsv(file_name):
    df = pd.read_csv(f'./shared_volume/{file_name}', sep='\t')
    df.to_sql(file_name, con=engine, if_exists='replace', index=False)
    return f"Loaded {file_name}"

# Set the directory path and CSV file name
dir_path = '/path/to/directory'
csv_file = 'file_info.csv'

# Check if the CSV file exists, and create it if it doesn't
if not os.path.exists(csv_file):
    df = pd.DataFrame(columns=['filename', 'created_time', 'modified_time'])
    df.to_csv(csv_file, index=False)

# Continuously check for new files
while True:
    # Loop through the files in the directory
    for file_name in os.listdir(dir_path):
        file_path = os.path.join(dir_path, file_name)

        # Check if the file is a CSV
        if not file_name.endswith('.csv'):
            continue

        # Get the file creation and modification times
        created_time = os.path.getctime(file_path)
        modified_time = os.path.getmtime(file_path)

        # Check if the file is new or has been modified
        df = pd.read_csv(csv_file)
        is_new_file = not any(df['filename'] == file_name)
        is_modified_file = (df.loc[df['filename'] == file_name, 'modified_time'].values[0] != modified_time) if not is_new_file else False

        # If the file is new or has been modified, add/update the file info in the DataFrame and CSV
        if is_new_file or is_modified_file:
            df.loc[df['filename'] == file_name, ['created_time', 'modified_time']] = [created_time, modified_time] if not is_new_file else [created_time, modified_time, '']
            if is_new_file:
                df = df.append({'filename': file_name, 'created_time': created_time, 'modified_time': modified_time}, ignore_index=True)
            df.to_csv(csv_file, index=False)

            # Optional: Print a message indicating the file was processed
            print(f'Processed file: {file_name}')

    # Wait for 60 seconds before checking again
    time.sleep(60)
    