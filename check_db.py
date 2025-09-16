import os
import django

# Sæt Django op
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vprepair.settings')
django.setup()

from django.db import connection

def check_tables():
    with connection.cursor() as cursor:
        # Hent alle tabeller
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        for table in tables:
            table_name = table[0]
            print(f"\n=== TABEL: {table_name} ===")
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            for col in columns:
                print(f"- {col[1]} ({col[2]})")

if __name__ == "__main__":
    check_tables()
