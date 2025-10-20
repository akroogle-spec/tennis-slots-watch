import psycopg2
import os
from datetime import datetime
import json

class Database:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.init_database()
    
    def get_connection(self):
        return psycopg2.connect(self.database_url)
    
    def init_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS booking_snapshots (
                id SERIAL PRIMARY KEY,
                check_date TIMESTAMP NOT NULL,
                available_dates TEXT NOT NULL,
                dates_count INTEGER NOT NULL
            )
        ''')
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def save_snapshot(self, available_dates):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        dates_json = json.dumps(available_dates, ensure_ascii=False)
        dates_count = len(available_dates)
        
        cursor.execute('''
            INSERT INTO booking_snapshots (check_date, available_dates, dates_count)
            VALUES (%s, %s, %s)
        ''', (datetime.now(), dates_json, dates_count))
        
        conn.commit()
        cursor.close()
        conn.close()
    
    def get_last_snapshot(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT available_dates, check_date
            FROM booking_snapshots
            ORDER BY check_date DESC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return json.loads(result[0]), result[1]
        return None, None
    
    def get_all_snapshots(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, check_date, available_dates, dates_count
            FROM booking_snapshots
            ORDER BY check_date DESC
            LIMIT 100
        ''')
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return results
