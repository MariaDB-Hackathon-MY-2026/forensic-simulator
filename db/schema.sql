-- ============================================================
-- Digital Forensic Student Data Recovery Simulator
-- MariaDB Schema + Sample Data
-- Port: 3307
-- ============================================================

CREATE DATABASE IF NOT EXISTS forensic_sim CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE forensic_sim;

-- ============================================================
-- 1. Students table (main subjects of simulation)
-- ============================================================
CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100),
    course VARCHAR(100),
    year INT,
    gpa DECIMAL(3,2),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 2. Records table (active academic records)
-- ============================================================
CREATE TABLE IF NOT EXISTS records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_id VARCHAR(20) NOT NULL,
    subject VARCHAR(100),
    grade VARCHAR(5),
    semester VARCHAR(20),
    academic_year VARCHAR(10),
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(student_id)
);

-- ============================================================
-- 3. Backup records (shadow copy for recovery simulation)
-- ============================================================
CREATE TABLE IF NOT EXISTS backup_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    original_table VARCHAR(50),
    original_id INT,
    data_snapshot JSON,
    backed_up_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 4. Activity logs (forensic evidence trail)
-- ============================================================
CREATE TABLE IF NOT EXISTS activity_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action_type VARCHAR(50) NOT NULL,  -- DELETE, UPDATE, INSERT, ACCESS
    target_table VARCHAR(50),
    target_id INT,
    old_value JSON,
    new_value JSON,
    performed_by VARCHAR(100) DEFAULT 'system',
    ip_address VARCHAR(45) DEFAULT '127.0.0.1',
    description TEXT,
    logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- 5. Recovery logs
-- ============================================================
CREATE TABLE IF NOT EXISTS recovery_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recovered_table VARCHAR(50),
    recovered_id INT,
    recovered_data JSON,
    recovered_by VARCHAR(100) DEFAULT 'investigator',
    recovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- Sample Data: Students
-- ============================================================
INSERT INTO students (student_id, name, email, course, year, gpa, status) VALUES
('STU001', 'Ahmad Faris', 'ahmad.faris@university.edu', 'Computer Science', 3, 3.75, 'active'),
('STU002', 'Nur Aisyah', 'nur.aisyah@university.edu', 'Cybersecurity', 2, 3.90, 'active'),
('STU003', 'Rajan Kumar', 'rajan.kumar@university.edu', 'Information Technology', 4, 3.20, 'active'),
('STU004', 'Siti Hajar', 'siti.hajar@university.edu', 'Computer Science', 1, 3.50, 'active'),
('STU005', 'Lee Wei Hao', 'lee.weihao@university.edu', 'Cybersecurity', 3, 3.65, 'active'),
('STU006', 'Priya Devi', 'priya.devi@university.edu', 'Information Technology', 2, 3.80, 'active'),
('STU007', 'Hafiz Zulkifli', 'hafiz.zul@university.edu', 'Computer Science', 4, 2.95, 'active'),
('STU008', 'Mei Ling', 'mei.ling@university.edu', 'Cybersecurity', 1, 3.40, 'active');

-- ============================================================
-- Sample Data: Academic Records
-- ============================================================
INSERT INTO records (student_id, subject, grade, semester, academic_year, remarks) VALUES
('STU001', 'Database Systems', 'A', 'Semester 1', '2024/2025', 'Excellent performance'),
('STU001', 'Network Security', 'A-', 'Semester 1', '2024/2025', 'Good understanding'),
('STU002', 'Ethical Hacking', 'A+', 'Semester 1', '2024/2025', 'Outstanding'),
('STU002', 'Digital Forensics', 'A', 'Semester 1', '2024/2025', 'Strong analytical skills'),
('STU003', 'Web Development', 'B+', 'Semester 1', '2024/2025', 'Consistent effort'),
('STU003', 'Operating Systems', 'B', 'Semester 1', '2024/2025', 'Needs improvement'),
('STU004', 'Programming Fundamentals', 'A', 'Semester 1', '2024/2025', 'Promising student'),
('STU005', 'Malware Analysis', 'A-', 'Semester 1', '2024/2025', 'Good research skills'),
('STU006', 'Cloud Computing', 'A', 'Semester 1', '2024/2025', 'Excellent project'),
('STU007', 'Software Engineering', 'C+', 'Semester 1', '2024/2025', 'Requires support'),
('STU008', 'Introduction to Security', 'B+', 'Semester 1', '2024/2025', 'Good foundation');

-- ============================================================
-- Initial backup snapshot of all students
-- ============================================================
INSERT INTO backup_records (original_table, original_id, data_snapshot) VALUES
('students', 1, '{"student_id":"STU001","name":"Ahmad Faris","email":"ahmad.faris@university.edu","course":"Computer Science","year":3,"gpa":3.75,"status":"active"}'),
('students', 2, '{"student_id":"STU002","name":"Nur Aisyah","email":"nur.aisyah@university.edu","course":"Cybersecurity","year":2,"gpa":3.90,"status":"active"}'),
('students', 3, '{"student_id":"STU003","name":"Rajan Kumar","email":"rajan.kumar@university.edu","course":"Information Technology","year":4,"gpa":3.20,"status":"active"}'),
('students', 4, '{"student_id":"STU004","name":"Siti Hajar","email":"siti.hajar@university.edu","course":"Computer Science","year":1,"gpa":3.50,"status":"active"}'),
('students', 5, '{"student_id":"STU005","name":"Lee Wei Hao","email":"lee.weihao@university.edu","course":"Cybersecurity","year":3,"gpa":3.65,"status":"active"}'),
('students', 6, '{"student_id":"STU006","name":"Priya Devi","email":"priya.devi@university.edu","course":"Information Technology","year":2,"gpa":3.80,"status":"active"}'),
('students', 7, '{"student_id":"STU007","name":"Hafiz Zulkifli","email":"hafiz.zul@university.edu","course":"Computer Science","year":4,"gpa":2.95,"status":"active"}'),
('students', 8, '{"student_id":"STU008","name":"Mei Ling","email":"mei.ling@university.edu","course":"Cybersecurity","year":1,"gpa":3.40,"status":"active"}'),
('records', 1, '{"student_id":"STU001","subject":"Database Systems","grade":"A","semester":"Semester 1","academic_year":"2024/2025"}'),
('records', 2, '{"student_id":"STU001","subject":"Network Security","grade":"A-","semester":"Semester 1","academic_year":"2024/2025"}'),
('records', 3, '{"student_id":"STU002","subject":"Ethical Hacking","grade":"A+","semester":"Semester 1","academic_year":"2024/2025"}'),
('records', 4, '{"student_id":"STU002","subject":"Digital Forensics","grade":"A","semester":"Semester 1","academic_year":"2024/2025"}'),
('records', 5, '{"student_id":"STU003","subject":"Web Development","grade":"B+","semester":"Semester 1","academic_year":"2024/2025"}'),
('records', 6, '{"student_id":"STU003","subject":"Operating Systems","grade":"B","semester":"Semester 1","academic_year":"2024/2025"}'),
('records', 7, '{"student_id":"STU004","subject":"Programming Fundamentals","grade":"A","semester":"Semester 1","academic_year":"2024/2025"}'),
('records', 8, '{"student_id":"STU005","subject":"Malware Analysis","grade":"A-","semester":"Semester 1","academic_year":"2024/2025"}'),
('records', 9, '{"student_id":"STU006","subject":"Cloud Computing","grade":"A","semester":"Semester 1","academic_year":"2024/2025"}'),
('records', 10, '{"student_id":"STU007","subject":"Software Engineering","grade":"C+","semester":"Semester 1","academic_year":"2024/2025"}'),
('records', 11, '{"student_id":"STU008","subject":"Introduction to Security","grade":"B+","semester":"Semester 1","academic_year":"2024/2025"}');

-- Initial log: system startup
INSERT INTO activity_logs (action_type, target_table, description, performed_by) VALUES
('ACCESS', 'system', 'Database initialized and ready for simulation', 'system');

-- ============================================================
-- 6. Evidence Logs (Tagged logs)
-- ============================================================
CREATE TABLE IF NOT EXISTS evidence_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_id INT NOT NULL,
    user_id VARCHAR(50) DEFAULT 'investigator',
    tagged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (log_id) REFERENCES activity_logs(id) ON DELETE CASCADE
);

-- ============================================================
-- 7. Case Reports (Generated forensic reports)
-- ============================================================
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
