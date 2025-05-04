import json
import re
import sqlite3
import pandas as pd

from fp.fp import FreeProxy

def get_fresh_proxies():
    try:
        proxy = FreeProxy(rand=True, timeout=1).get()
        return {
            'http': proxy, 
            'https': proxy
        }
    except:
        return None


def time_to_minutes(time_str:str)->int:
    hours_match = re.search(r'(\d+)h', time_str)
    minutes_match = re.search(r'(\d+)m', time_str)
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0

    return hours * 60 + minutes


def json_to_sqlite(json_data:dict, db_file:str, table_name:str)->str:
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data

    if not data or not isinstance(data, list):
        raise ValueError("JSON data should be a list of dictionaries")

    columns = list(data[0].keys())

    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    create_table_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
    cursor.execute(create_table_sql)

    for item in data:
        placeholders = ', '.join(['?'] * len(columns))
        values = [item[col] for col in columns]
        cursor.execute(
            f"INSERT INTO {table_name} VALUES ({placeholders})", values)

    conn.commit()
    conn.close()
    
    return db_file

def json_to_excel(json_data:dict, file_name:str)->None:
    df = pd.DataFrame(json_data,)
    df.to_excel(file_name, index=False)

def execute_sql_query(sql_query:str, db_path:str)->dict:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        cursor.execute(sql_query)
        results = [dict(row) for row in cursor.fetchall()]
        return results
    finally:
        conn.close()

        

