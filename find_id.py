import pymysql
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'root1234',
    'database': 'forensic_sim',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}
conn = pymysql.connect(**DB_CONFIG)
try:
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM records LIMIT 1")
        row = cur.fetchone()
        if row:
            print("Valid record_id:", row['id'])
        else:
            print("No records found.")
finally:
    conn.close()
