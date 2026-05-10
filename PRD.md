# 📄 Product Requirement Document (PRD)
## Digital Forensic Student Data Recovery Simulator

---

## 🧩 Overview
The Digital Forensic Student Data Recovery Simulator is a web-based forensic training platform designed to simulate real-world database incidents such as data deletion and suspicious activities. It enables students to perform forensic investigation and data recovery in a safe and controlled environment using MariaDB.

---

## 🎯 Objectives
- Provide hands-on learning for digital forensics and database recovery  
- Simulate real-world database incidents safely  
- Enable users to analyze, investigate, and recover data  
- Demonstrate practical use of MariaDB in forensic scenarios  

---

## 👤 Target Users
- IT students  
- Cybersecurity students  
- Lecturers / trainers  
- Beginner forensic learners  

---

## 🚀 Core Functionalities

### 1. Scenario Simulation
- Simulate:
  - Record deletion (intentional / accidental)  
  - Suspicious database activities (unauthorized updates, abnormal queries)  
- Provide predefined datasets for training  

---

### 2. Data Management
- Main database (active data)  
- Backup / shadow tables (for recovery simulation)  
- Activity logs table  

---

### 3. Forensic Investigation Module
- View logs of:
  - deletions  
  - updates  
  - access attempts  
- Identify suspicious activities  

---

### 4. Data Recovery Module
- Restore deleted records from backup  
- Reconstruct modified data  
- Execute recovery via SQL or guided UI  

---

### 5. Data Comparison
- Compare:
  - original data  
  - compromised data  
  - recovered data  
- Highlight differences  

---

### 6. User Interface
- Dashboard:
  - scenario selection  
  - logs view  
  - recovery actions  
- Simple and educational UI  

---

## 🗄️ Database Design (High-Level)

### Tables:
- `students`  
- `records`  
- `backup_records`  
- `activity_logs`  
- `recovery_logs`  

---

## 🔐 Security Considerations
- Simulated environment only (no real attack execution)  
- Controlled input (avoid real SQL injection risk)  
- Logging for all actions  

---

## ⚙️ System Flow
1. User selects scenario  
2. System simulates incident (delete/update)  
3. Logs are generated  
4. User investigates logs  
5. User performs recovery  
6. System shows before vs after comparison  

---

## 📊 Success Criteria
- Users can:
  - detect incidents  
  - analyze logs  
  - recover data  
- System clearly demonstrates MariaDB usage  

---