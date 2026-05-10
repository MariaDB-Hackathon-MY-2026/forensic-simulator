# Fathsic-Digital Forensic Student Data Recovery Simulator-University Poly-Tech Malaysia

A web-based educational tool designed to simulate the digital forensic data recovery process. This platform helps students learn how to recover deleted files, analyze raw data, and generate professional forensic reports.

## Features
- **Simulated Recovery Process:** Practice recovering deleted files using various forensic algorithms and techniques.
- **Interactive Dashboard:** View investigation progress, evidence recovered, and overall case status in real-time.
- **Hex Viewer:** Examine raw file data to understand data structures at a low level.
- **Evidence Tagging:** Tag recovered files as evidence for your investigation reports.
- **Timeline Generation:** Automatically generate an investigation timeline based on your actions.
- **Case Reports:** Generate and export professional forensic reports based on your findings.

## Technologies Used
- **Backend:** Python, Flask, MariaDB
- **Frontend:** HTML, CSS, JavaScript (Vanilla)
- **Version Control:** Git, GitHub

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/MariaDB-Hackathon-MY-2026/forensic-simulator.git
   cd forensic-simulator
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Initialize the database (if needed):
   ```bash
   python migrate_db.py
   ```

4. Run the application:
   ```bash
   python app.py
   ```

## Usage
1. Open your web browser and navigate to `http://localhost:5000`
2. Create a new scenario or select an existing case from the dashboard.
3. Use the recovery tools to analyze the simulated drive and find deleted files.
4. Tag important findings as evidence.
5. Review the timeline and generate a final forensic report.

## Folder Structure
```
forensic-simulator/
├── app.py              # Main Flask application file
├── db/                 # Database schema and MariaDB configuration
├── static/             # CSS styles and JavaScript files
├── templates/          # HTML templates for the frontend
├── requirements.txt    # Python dependencies
├── PRD.md              # Product Requirements Document
├── ROFTCO.md           # Rules of the Competition
└── README.md           # Project documentation
```
