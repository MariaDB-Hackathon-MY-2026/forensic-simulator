import pymysql
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'root1234',
    'database': 'forensic_sim',
    'charset': 'utf8mb4'
}
conn = pymysql.connect(**DB_CONFIG)
try:
    with conn.cursor() as cur:
        cur.execute('''
        CREATE TABLE IF NOT EXISTS evidence_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            log_id INT NOT NULL,
            user_id VARCHAR(50) DEFAULT 'investigator',
            tagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (log_id) REFERENCES activity_logs(id) ON DELETE CASCADE
        );
        ''')
        cur.execute('''
        CREATE TABLE IF NOT EXISTS case_reports (
            id INT AUTO_INCREMENT PRIMARY KEY,
            scenario_name VARCHAR(100),
            summary TEXT,
            actions_taken TEXT,
            evidence_found TEXT,
            score INT,
            result VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
    conn.commit()
    print('Tables created successfully.')
finally:
    conn.close()
