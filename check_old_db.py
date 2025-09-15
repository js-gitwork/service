import sqlite3

old_db_path = "service_system.db"
new_db_path = "db.sqlite3"

old_conn = sqlite3.connect(old_db_path)
new_conn = sqlite3.connect(new_db_path)

old_cursor = old_conn.cursor()
new_cursor = new_conn.cursor()

# Hent data
old_cursor.execute("SELECT VPID, Kaldenavn, Beskrivelse FROM Maskinliste;")
assets = old_cursor.fetchall()

for asset in assets:
    vpid, name, description = asset
    new_cursor.execute("""
        INSERT INTO assets_asset (
            VPID, name, description, location, is_active, in_workshop
        ) VALUES (?, ?, ?, ?, ?, ?);
    """, (vpid, name or "", description or "", "", True, False))  # Standardværdier for is_active og in_workshop

new_conn.commit()
print(f"✅ Kopieret {len(assets)} aktiver!")
old_conn.close()
new_conn.close()
