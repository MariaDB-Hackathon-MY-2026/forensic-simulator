from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
import pymysql
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'forensic_sim_secret_key'

@app.before_request
def ensure_score():
    if 'score' not in session:
        session['score'] = 100

@app.context_processor
def inject_globals():
    score = session.get('score', 100)
    if score >= 96: rank = 'Expert'
    elif score >= 81: rank = 'Investigator'
    elif score >= 51: rank = 'Analyst'
    else: rank = 'Trainee'
    return dict(user_rank=rank)

@app.route('/toggle_mode', methods=['POST'])
def toggle_mode():
    current_mode = session.get('mode', 'guided')
    session['mode'] = 'challenge' if current_mode == 'guided' else 'guided'
    return redirect(url_for('landing'))


# ─────────────────────────────────────────────
# Database Configuration
# ─────────────────────────────────────────────
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3307,
    'user': 'root',
    'password': 'root1234',   # Change to your MariaDB root password
    'database': 'forensic_sim',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db():
    return pymysql.connect(**DB_CONFIG)

def log_action(action_type, target_table, description, target_id=None, old_value=None, new_value=None, performed_by='investigator'):
    """Write an entry to activity_logs."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO activity_logs 
                    (action_type, target_table, target_id, old_value, new_value, performed_by, description)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                action_type, target_table, target_id,
                json.dumps(old_value, default=str) if old_value else None,
                json.dumps(new_value, default=str) if new_value else None,
                performed_by, description
            ))
        conn.commit()
    finally:
        conn.close()

# ─────────────────────────────────────────────
# Landing Page
# ─────────────────────────────────────────────
@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/select_mode', methods=['POST'])
def select_mode():
    mode = request.form.get('mode', 'guided')
    session['mode'] = mode
    session['score'] = 100
    session.pop('active_target', None)
    return redirect(url_for('dashboard'))

# ─────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS total FROM students")
            total_students = cur.fetchone()['total']

            cur.execute("SELECT COUNT(*) AS total FROM records")
            total_records = cur.fetchone()['total']

            cur.execute("SELECT COUNT(*) AS total FROM activity_logs")
            total_logs = cur.fetchone()['total']

            cur.execute("SELECT COUNT(*) AS total FROM recovery_logs")
            total_recoveries = cur.fetchone()['total']

            cur.execute("""
                SELECT * FROM activity_logs 
                ORDER BY logged_at DESC LIMIT 5
            """)
            recent_logs = cur.fetchall()

        return render_template('dashboard.html',
            total_students=total_students,
            total_records=total_records,
            total_logs=total_logs,
            total_recoveries=total_recoveries,
            recent_logs=recent_logs
        )
    finally:
        conn.close()

# ─────────────────────────────────────────────
# Scenario Simulation
# ─────────────────────────────────────────────
@app.route('/scenario')
def scenario():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM students ORDER BY student_id")
            students = cur.fetchall()
            cur.execute("SELECT * FROM records ORDER BY student_id")
            records = cur.fetchall()
    finally:
        conn.close()
    return render_template('scenario.html', students=students, records=records)

@app.route('/scenario/delete_student', methods=['POST'])
def delete_student():
    student_id = request.form.get('student_id')
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Snapshot before delete
            cur.execute("SELECT * FROM students WHERE student_id = %s", (student_id,))
            student = cur.fetchone()
            if not student:
                flash('Student not found.', 'error')
                return redirect(url_for('scenario'))

            # Set as active investigation target
            session['active_target'] = {'table': 'students', 'id': student['id'], 'student_id': student_id}

            # Backup to backup_records
            cur.execute("""
                INSERT INTO backup_records (original_table, original_id, data_snapshot)
                VALUES ('students', %s, %s)
            """, (student['id'], json.dumps(student, default=str)))

            # Delete associated records first
            cur.execute("SELECT * FROM records WHERE student_id = %s", (student_id,))
            recs = cur.fetchall()
            for r in recs:
                cur.execute("""
                    INSERT INTO backup_records (original_table, original_id, data_snapshot)
                    VALUES ('records', %s, %s)
                """, (r['id'], json.dumps(r, default=str)))
            cur.execute("DELETE FROM records WHERE student_id = %s", (student_id,))
            cur.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()

        log_action('DELETE', 'students', f"Student {student_id} ({student['name']}) deleted in simulation",
                   target_id=student['id'], old_value=student)
        flash(f"✅ Simulation: Student {student_id} and their records have been deleted.", 'success')
    finally:
        conn.close()
    return redirect(url_for('scenario'))

@app.route('/scenario/modify_record', methods=['POST'])
def modify_record():
    record_id = request.form.get('record_id')
    new_grade = request.form.get('new_grade')
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM records WHERE id = %s", (record_id,))
            old_record = cur.fetchone()
            if not old_record:
                flash('Record not found.', 'error')
                return redirect(url_for('scenario'))

            # Set as active investigation target
            session['active_target'] = {'table': 'records', 'id': int(record_id)}

            cur.execute("""
                INSERT INTO backup_records (original_table, original_id, data_snapshot)
                VALUES ('records', %s, %s)
            """, (record_id, json.dumps(old_record, default=str)))

            cur.execute("UPDATE records SET grade = %s WHERE id = %s", (new_grade, record_id))
        conn.commit()

        new_record = old_record.copy()
        new_record['grade'] = new_grade
        log_action('UPDATE', 'records',
                   f"Grade tampered: {old_record['subject']} changed from {old_record['grade']} to {new_grade}",
                   target_id=int(record_id), old_value=old_record, new_value=new_record)
        flash(f"⚠️ Simulation: Grade for record #{record_id} changed to {new_grade}.", 'warning')
    finally:
        conn.close()
    return redirect(url_for('scenario'))

@app.route('/scenario/reset', methods=['POST'])
def reset_scenario():
    """Reset DB to original state using backups."""
    session['score'] = 100
    session.pop('active_target', None)
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM evidence_logs")
            cur.execute("DELETE FROM records")
            cur.execute("DELETE FROM students")
            cur.execute("""
                SELECT * FROM backup_records 
                WHERE original_table IN ('students', 'records')
                ORDER BY original_table DESC, backed_up_at ASC
            """)
            backups = cur.fetchall()

            inserted_students = set()
            inserted_records = set()

            for b in backups:
                data = json.loads(b['data_snapshot'])
                if b['original_table'] == 'students' and data['student_id'] not in inserted_students:
                    cur.execute("""
                        INSERT IGNORE INTO students 
                            (student_id, name, email, course, year, gpa, status)
                        VALUES (%(student_id)s, %(name)s, %(email)s, %(course)s, %(year)s, %(gpa)s, %(status)s)
                    """, data)
                    inserted_students.add(data['student_id'])

            for b in backups:
                data = json.loads(b['data_snapshot'])
                if b['original_table'] == 'records':
                    data.setdefault('academic_year', None)
                    data.setdefault('remarks', None)
                    key = (data['student_id'], data['subject'], data['semester'])
                    if key not in inserted_records:
                        cur.execute("""
                            INSERT IGNORE INTO records 
                                (student_id, subject, grade, semester, academic_year, remarks)
                            VALUES (%(student_id)s, %(subject)s, %(grade)s, %(semester)s, %(academic_year)s, %(remarks)s)
                        """, data)
                        inserted_records.add(key)
        conn.commit()
        log_action('ACCESS', 'system', 'Database reset to initial state by investigator')
        flash('🔄 Database has been reset to its original state.', 'info')
    finally:
        conn.close()
    return redirect(url_for('scenario'))

# ─────────────────────────────────────────────
# Forensic Logs Viewer
# ─────────────────────────────────────────────
@app.route('/logs')
def logs():
    action_filter = request.args.get('action', '')
    conn = get_db()
    try:
        with conn.cursor() as cur:
            if action_filter:
                cur.execute("""
                    SELECT * FROM activity_logs WHERE action_type = %s 
                    ORDER BY logged_at DESC
                """, (action_filter,))
            else:
                cur.execute("SELECT * FROM activity_logs ORDER BY logged_at DESC")
            all_logs = cur.fetchall()
            
            cur.execute("SELECT log_id FROM evidence_logs")
            tagged_ids = [row['log_id'] for row in cur.fetchall()]
    finally:
        conn.close()
    return render_template('logs.html', logs=all_logs, action_filter=action_filter, tagged_ids=tagged_ids)

@app.route('/api/evidence/toggle', methods=['POST'])
def toggle_evidence():
    log_id = request.json.get('log_id')
    if not log_id: return jsonify({'error': 'Missing log_id'}), 400
    
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM evidence_logs WHERE log_id = %s", (log_id,))
            if cur.fetchone():
                cur.execute("DELETE FROM evidence_logs WHERE log_id = %s", (log_id,))
                status = 'untagged'
            else:
                cur.execute("INSERT INTO evidence_logs (log_id) VALUES (%s)", (log_id,))
                status = 'tagged'
        conn.commit()
        return jsonify({'status': status})
    finally:
        conn.close()


# ─────────────────────────────────────────────
# Data Recovery
# ─────────────────────────────────────────────
@app.route('/recovery')
def recovery():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT br.*, 
                    CASE 
                        WHEN br.original_table = 'students' THEN
                            JSON_UNQUOTE(JSON_EXTRACT(br.data_snapshot, '$.name'))
                        ELSE 
                            JSON_UNQUOTE(JSON_EXTRACT(br.data_snapshot, '$.subject'))
                    END AS label
                FROM backup_records br
                ORDER BY br.backed_up_at DESC
            """)
            backups = cur.fetchall()

            cur.execute("SELECT * FROM recovery_logs ORDER BY recovered_at DESC")
            recovery_history = cur.fetchall()
    finally:
        conn.close()
    return render_template('recovery.html', backups=backups, recovery_history=recovery_history)

@app.route('/recovery/restore', methods=['POST'])
def restore_record():
    backup_id = request.form.get('backup_id')
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM backup_records WHERE id = %s", (backup_id,))
            backup = cur.fetchone()
            if not backup:
                flash('Backup record not found.', 'error')
                return redirect(url_for('recovery'))

            data = json.loads(backup['data_snapshot'])

            if backup['original_table'] == 'students':
                cur.execute("""
                    INSERT INTO students (student_id, name, email, course, year, gpa, status)
                    VALUES (%(student_id)s, %(name)s, %(email)s, %(course)s, %(year)s, %(gpa)s, %(status)s)
                    ON DUPLICATE KEY UPDATE
                        name=VALUES(name), email=VALUES(email), 
                        course=VALUES(course), year=VALUES(year), 
                        gpa=VALUES(gpa), status=VALUES(status)
                """, data)
                label = data.get('name', 'Unknown')

            elif backup['original_table'] == 'records':
                data.setdefault('academic_year', None)
                data.setdefault('remarks', None)
                try:
                    cur.execute("""
                        INSERT INTO records (student_id, subject, grade, semester, academic_year, remarks)
                        VALUES (%(student_id)s, %(subject)s, %(grade)s, %(semester)s, %(academic_year)s, %(remarks)s)
                        ON DUPLICATE KEY UPDATE grade=VALUES(grade), remarks=VALUES(remarks)
                    """, data)
                except pymysql.err.IntegrityError:
                    flash(f"❌ Error: Cannot restore academic record. The associated student profile ({data.get('student_id')}) must be restored first!", 'error')
                    return redirect(url_for('recovery'))
                label = f"{data.get('subject')} ({data.get('student_id')})"

            cur.execute("""
                INSERT INTO recovery_logs (recovered_table, recovered_id, recovered_data)
                VALUES (%s, %s, %s)
            """, (backup['original_table'], backup['original_id'], backup['data_snapshot']))
        conn.commit()

        # Evaluate Investigation
        active_target = session.get('active_target')
        if active_target:
            is_correct = False
            
            # Case 001: Disgruntled Admin (Student Deletion)
            if active_target['table'] == 'students':
                if backup['original_table'] == 'students' and str(backup['original_id']) == str(active_target['id']):
                    is_correct = True
                elif backup['original_table'] == 'records' and data.get('student_id') == active_target.get('student_id'):
                    is_correct = True
            
            # Case 002: Midnight Hacker (Grade Tampering)
            elif active_target['table'] == 'records':
                if backup['original_table'] == 'records' and str(backup['original_id']) == str(active_target['id']):
                    is_correct = True

            if is_correct:
                flash(f"✅ Case Solved! Successfully recovered target evidence: {label}", 'success')
                session.pop('active_target', None)
            else:
                session['score'] -= 10
                session.modified = True
                flash(f"❌ Incorrect evidence recovered. Integrity penalty: -10 points.", 'error')
        else:
            flash(f"✅ Successfully recovered: {label}", 'success')

        log_action('ACCESS', backup['original_table'],
                   f"Data recovered: {backup['original_table']} ID {backup['original_id']}",
                   target_id=backup['original_id'], new_value=data)
    finally:
        conn.close()
    return redirect(url_for('recovery'))

# ─────────────────────────────────────────────
# Data Comparison
# ─────────────────────────────────────────────
@app.route('/compare')
def compare():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM students ORDER BY student_id")
            current_students = cur.fetchall()

            cur.execute("""
                SELECT data_snapshot FROM backup_records 
                WHERE original_table = 'students'
                GROUP BY original_id
                ORDER BY backed_up_at ASC
            """)
            backup_rows = cur.fetchall()
            original_students = [json.loads(r['data_snapshot']) for r in backup_rows]

            cur.execute("SELECT * FROM records ORDER BY student_id")
            current_records = cur.fetchall()

            cur.execute("""
                SELECT data_snapshot FROM backup_records 
                WHERE original_table = 'records'
                GROUP BY original_id
                ORDER BY backed_up_at ASC
            """)
            backup_rec_rows = cur.fetchall()
            original_records = [json.loads(r['data_snapshot']) for r in backup_rec_rows]

    finally:
        conn.close()

    return render_template('compare.html',
        current_students=current_students,
        original_students=original_students,
        current_records=current_records,
        original_records=original_records
    )

# ─────────────────────────────────────────────
# API: Live stats for dashboard charts
# ─────────────────────────────────────────────
@app.route('/api/stats')
def api_stats():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT action_type, COUNT(*) AS count 
                FROM activity_logs GROUP BY action_type
            """)
            action_counts = cur.fetchall()
        return jsonify({'action_counts': action_counts})
    finally:
        conn.close()

# ─────────────────────────────────────────────
# Advanced Features: Timeline & Reports
# ─────────────────────────────────────────────
@app.route('/timeline')
def timeline():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM activity_logs ORDER BY logged_at ASC")
            events = cur.fetchall()
    finally:
        conn.close()
    return render_template('timeline.html', events=events)

@app.route('/report/generate', methods=['POST'])
def generate_report():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            # Gather evidence
            cur.execute("""
                SELECT a.* FROM activity_logs a
                JOIN evidence_logs e ON a.id = e.log_id
                ORDER BY a.logged_at ASC
            """)
            evidence = cur.fetchall()
            
            if evidence:
                summary = f"Investigation completed. {len(evidence)} evidence logs were tagged."
            else:
                summary = "Investigation completed with no evidence tagged."
                
            score = session.get('score', 100)
            result = "Success" if score >= 80 else "Needs Improvement"
            
            cur.execute("""
                INSERT INTO case_reports (scenario_name, summary, evidence_found, score, result)
                VALUES (%s, %s, %s, %s, %s)
            """, ("Forensic Case", summary, json.dumps(evidence, default=str), score, result))
            
            report_id = cur.lastrowid
            
            # Clear evidence for next case
            cur.execute("DELETE FROM evidence_logs")
            session['score'] = 100
            session.pop('active_target', None)
        conn.commit()
        flash("Case Report Generated successfully!", "success")
        return redirect(url_for('view_report', report_id=report_id))
    finally:
        conn.close()

@app.route('/reports')
def list_reports():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM case_reports ORDER BY created_at DESC")
            reports = cur.fetchall()
    finally:
        conn.close()
    return render_template('reports.html', reports=reports)

@app.route('/reports/<int:report_id>')
def view_report(report_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM case_reports WHERE id = %s", (report_id,))
            report = cur.fetchone()
            if not report:
                flash("Report not found.", "error")
                return redirect(url_for('list_reports'))
            
            evidence = json.loads(report['evidence_found']) if report['evidence_found'] else []
    finally:
        conn.close()
    return render_template('report_detail.html', report=report, evidence=evidence)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
