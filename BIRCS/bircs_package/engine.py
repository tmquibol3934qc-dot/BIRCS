import mysql.connector
from tkinter import messagebox
from datetime import datetime, timedelta
import re
import difflib


class DatabaseEngine:
    def __init__(self):
        # Database Configuration
        self.db_config = {
            'host': 'localhost',
            'user': 'root',
            'password': '',  # <--- CHANGE THIS TO YOUR MYSQL PASSWORD
            'database': 'bircs_db'
        }

        # Test connection on startup
        try:
            conn = self.get_connection()
            conn.close()
            print("[SUCCESS] Successfully connected to MySQL!")
        except Exception as e:
            print(f"[ERROR] Error connecting to MySQL: {e}")
            messagebox.showerror("Database Error", f"Could not connect to MySQL.\nError: {e}")

    def get_connection(self):
        """Creates a new connection to the MySQL database"""
        return mysql.connector.connect(**self.db_config)

    # ==========================================
    # 🧑‍🤝‍🧑 USER MANAGEMENT & AUTHENTICATION
    # ==========================================
    def register_user(self, data):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            sql = """
                  INSERT INTO users
                  (employee_id, rfid_code, first_name, last_name, role, contact_no, password, q1, a1, q2, a2, q3, a3)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                  """

            parts = data['name'].split()
            fname = parts[0]
            lname = " ".join(parts[1:]) if len(parts) > 1 else ""

            values = (
                data['emp_id'], data['rfid'], fname, lname, data['position'],
                "N/A", data['pass'], data['q1'], data['a1'], data['q2'], data['a2'], data['q3'], data['a3']
            )

            cursor.execute(sql, values)
            conn.commit()
            conn.close()
            return True, "Registration Successful!"

        except mysql.connector.IntegrityError as e:
            if "rfid_code" in str(e): return False, "This RFID Card is already registered!"
            return False, "Employee ID already exists."
        except Exception as e:
            return False, f"Database Error: {e}"

    def authenticate_user(self, login_val, password=""):
        """Verifies credentials OR RFID, enforces suspensions"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            if not password:  # RFID Login
                query = "SELECT * FROM users WHERE rfid_code = %s OR employee_id = %s"
                cursor.execute(query, (login_val, login_val))
            else:  # Manual Login
                query = "SELECT * FROM users WHERE (username = %s OR employee_id = %s) AND password = %s"
                cursor.execute(query, (login_val, login_val, password))

            user = cursor.fetchone()

            if not user:
                conn.close()
                return {"success": False, "message": "Invalid Credentials or Unregistered RFID."}

            status = user.get('status', 'Active')

            if status == 'Blocked':
                conn.close()
                return {"success": False, "message": "ACCESS DENIED: Account permanently blocked."}

            if status == 'Suspended':
                suspend_until = user.get('suspension_until')
                if suspend_until and datetime.now() < suspend_until:
                    formatted_time = suspend_until.strftime("%B %d, %Y at %I:%M %p")
                    conn.close()
                    return {"success": False, "message": f"ACCOUNT SUSPENDED until:\n{formatted_time}"}
                elif suspend_until:
                    # Lift suspension if time has passed
                    cursor.execute("UPDATE users SET status = 'Active', suspension_until = NULL WHERE id = %s",
                                   (user['id'],))
                    conn.commit()
                    user['status'] = 'Active'

            conn.close()
            return {"success": True, "user_data": user}

        except Exception as e:
            print(f"Auth Error: {e}")
            return {"success": False, "message": "Database connection error."}

    def verify_kapitan_access(self, scanned_rfid):
        """Checks if RFID belongs to a Kapitan"""
        try:
            clean_rfid = scanned_rfid.strip()
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT * FROM users WHERE rfid_code = %s", (clean_rfid,))
            user = cursor.fetchone()
            conn.close()

            if user and (user.get('role') == 'Kapitan' or user.get('position') == 'Kapitan'):
                return True, user
            return False, None

        except Exception as e:
            print(f"Kapitan Access Error: {e}")
            return False, None

    def get_all_users(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            conn.close()
            return users
        except:
            return []

    def update_user_account(self, user_id, first_name, last_name, employee_id, password, role, status, rfid_code,
                            suspend_val=0, suspend_type="Hours"):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            suspend_until = None
            if status == "Suspended":
                if suspend_type == "Hours":
                    suspend_until = datetime.now() + timedelta(hours=int(suspend_val))
                else:
                    suspend_until = datetime.now() + timedelta(days=int(suspend_val))

            query = """
                UPDATE users 
                SET first_name=%s, last_name=%s, employee_id=%s, password=%s, role=%s, status=%s, suspension_until=%s, rfid_code=%s
                WHERE id=%s
            """
            cursor.execute(query, (first_name, last_name, employee_id, password, role, status, suspend_until, rfid_code,
                                   user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Update User Error: {e}")
            return False

    def get_user_performance_stats(self, officer_name):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT COUNT(*) as total FROM incidents WHERE processed_by = %s", (officer_name,))
            total = cursor.fetchone()['total']
            cursor.execute("SELECT COUNT(*) as resolved FROM incidents WHERE processed_by = %s AND status = 'Resolved'",
                           (officer_name,))
            resolved = cursor.fetchone()['resolved']
            conn.close()
            return {"handled": total, "resolved": resolved}
        except:
            return {"handled": 0, "resolved": 0}

    # ==========================================
    # 🔐 FORGOT PASSWORD SYSTEM
    # ==========================================
    def check_user_exists(self, emp_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE employee_id = %s", (emp_id,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except:
            return False

    def get_user_security_questions(self, emp_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT q1, q2, q3 FROM users WHERE employee_id = %s OR username = %s", (emp_id, emp_id))
            user = cursor.fetchone()
            conn.close()
            return user
        except:
            return None

    def verify_security_answers(self, emp_id, a1, a2, a3):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT a1, a2, a3 FROM users WHERE employee_id = %s OR username = %s", (emp_id, emp_id))
            user = cursor.fetchone()
            conn.close()

            if user and (user['a1'].strip().lower() == a1.strip().lower() and
                         user['a2'].strip().lower() == a2.strip().lower() and
                         user['a3'].strip().lower() == a3.strip().lower()):
                return True
            return False
        except:
            return False

    def reset_user_password(self, emp_id, new_password):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE employee_id = %s OR username = %s",
                           (new_password, emp_id, emp_id))
            conn.commit()
            conn.close()
            return True
        except:
            return False

    def link_rfid_card(self, emp_id, rfid_code):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET rfid_code = %s WHERE employee_id = %s", (rfid_code, emp_id))
            conn.commit()
            rows = cursor.rowcount
            conn.close()
            return (True, "RFID Linked Successfully!") if rows > 0 else (False, "User not found.")
        except mysql.connector.IntegrityError:
            return False, "Card already linked!"
        except Exception as e:
            return False, str(e)

    # ==========================================
    # 📋 INCIDENTS & BLOTTER MANAGEMENT
    # ==========================================
    def save_incident(self, comp, comp_contact, comp_address, resp, resp_contact, resp_address, date, time_str, zone,
                      category, narrative, officer, status):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # Generate Case ID
            current_year = datetime.now().year
            cursor.execute("SELECT COUNT(*) as total FROM incidents WHERE YEAR(created_at) = %s", (current_year,))
            total = cursor.fetchone()['total']
            new_case_id = f"{current_year}-{(total + 1):03d}"

            # NLP Root Words (Optional: Add 'nlp_keywords' to the SQL if your database supports it)
            # root_words = self.extract_root_words(narrative)

            query = """
                INSERT INTO incidents (
                    case_no, complainant_name, complainant_contact, complainant_address, 
                    respondent_name, respondent_contact, respondent_address, 
                    date_of_incident, exact_time, zone, category, narrative, processed_by, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (new_case_id, comp, comp_contact, comp_address, resp, resp_contact, resp_address,
                      date, time_str, zone, category, narrative, officer, status)

            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True, new_case_id
        except Exception as e:
            print(f"Error saving incident: {e}")
            return False, str(e)

    def get_all_incidents(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT * FROM incidents 
                WHERE status != 'Resolved' OR (status = 'Resolved' AND created_at >= NOW() - INTERVAL 30 DAY)
                ORDER BY created_at DESC
            """
            cursor.execute(query)
            records = cursor.fetchall()
            conn.close()
            return records
        except:
            return []

    def get_my_pending_cases(self, officer_name, role):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            if role.lower() in ['kapitan', 'admin']:
                cursor.execute("SELECT * FROM incidents WHERE status != 'Resolved' ORDER BY created_at DESC")
            else:
                cursor.execute(
                    "SELECT * FROM incidents WHERE status != 'Resolved' AND processed_by = %s ORDER BY created_at DESC",
                    (officer_name,))
            records = cursor.fetchall()
            conn.close()
            return records
        except:
            return []

    def get_incident_categories(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM incidents WHERE category IS NOT NULL AND category != ''")
            results = cursor.fetchall()
            conn.close()
            return [row[0] for row in results] if results else ["Theft", "Physical Assault", "Noise Complaint",
                                                                "Property Damage", "Trespassing"]
        except:
            return ["Theft", "Physical Assault", "Noise Complaint", "Property Damage"]

    def advanced_search_incidents(self, keyword="", category="All Categories", year="All Years", status="All Status"):
        """Omni-Search Pro: Scans Case IDs/Names + Category + Year + Status Filters"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM incidents WHERE 1=1"
            params = []

            if keyword and keyword.strip() != "":
                kw = f"%{keyword.strip()}%"
                query += " AND (case_no LIKE %s OR complainant_name LIKE %s OR respondent_name LIKE %s)"
                params.extend([kw, kw, kw])
            if category and category != "All Categories":
                query += " AND category = %s"
                params.append(category)
            if year and year != "All Years":
                query += " AND YEAR(created_at) = %s"
                params.append(year)
            if status and status != "All Status":
                db_status = "Pending" if status == "Normal" else status
                query += " AND status = %s"
                params.append(db_status)

            query += " ORDER BY created_at DESC"
            cursor.execute(query, tuple(params))
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            print(f"Omni-Search Error: {e}")
            return []

    # ==========================================
    # 🤝 RESOLUTIONS & APPEALS
    # ==========================================
    def update_incident_resolution(self, case_id, settlement_text, stage, deadline, officer_name):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT settlement_details FROM incidents WHERE case_no = %s", (case_id,))
            case = cursor.fetchone()

            if case and case.get('settlement_details'):
                query = "UPDATE incidents SET settlement_details_2=%s, hearing_stage=%s, compliance_deadline=%s, processed_by=%s, status='Resolved' WHERE case_no=%s"
            else:
                query = "UPDATE incidents SET settlement_details=%s, hearing_stage=%s, compliance_deadline=%s, processed_by=%s, status='Resolved' WHERE case_no=%s"

            cursor.execute(query, (settlement_text, stage, deadline, officer_name, case_id))
            conn.commit()
            conn.close()
            return True
        except:
            return False

    def request_case_reopen(self, case_no, new_narrative):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE incidents SET reopen_status = 'Requested', narrative_2 = %s WHERE case_no = %s",
                           (new_narrative, case_no))
            conn.commit()
            conn.close()
            return True
        except:
            return False

    def get_reopen_requests(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM incidents WHERE reopen_status = 'Requested'")
            results = cursor.fetchall()
            conn.close()
            return results
        except:
            return []

    def handle_reopen_request(self, case_no, action):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if action == 'Approve':
                cursor.execute("UPDATE incidents SET status = 'Pending', reopen_status = 'Approved' WHERE case_no = %s",
                               (case_no,))
            else:
                cursor.execute("UPDATE incidents SET reopen_status = 'Denied' WHERE case_no = %s", (case_no,))
            conn.commit()
            conn.close()
            return True
        except:
            return False

    # ==========================================
    # 📊 ANALYTICS & DASHBOARD
    # ==========================================
    def get_dashboard_stats(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT status, COUNT(*) as count FROM incidents GROUP BY status")
            rows = cursor.fetchall()
            conn.close()

            stats = {'Total Cases': 0, 'Pending': 0, 'Resolved': 0, 'Urgent': 0}
            for row in rows:
                stats['Total Cases'] += row['count']
                if row['status'] in stats: stats[row['status']] = row['count']
            return stats
        except:
            return {'Total Cases': 0, 'Pending': 0, 'Resolved': 0, 'Urgent': 0}

    def get_incident_analytics(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT zone, exact_time FROM incidents")
            records = cursor.fetchall()
            conn.close()

            if not records: return {"hotspot": "No Data", "hotspot_pct": 0.0, "peak_hours": "No Data"}

            from collections import Counter
            zones = [r['zone'] for r in records if r['zone']]
            top_zone = "Unknown"
            hotspot_pct = 0.0
            if zones:
                top_zone, top_count = Counter(zones).most_common(1)[0]
                hotspot_pct = top_count / len(zones)

            hours = []
            for r in records:
                if r['exact_time']:
                    try:
                        hours.append(datetime.strptime(r['exact_time'], "%I:%M %p").hour)
                    except:
                        pass

            peak_str = "Unknown"
            if hours:
                peak_hour = Counter(hours).most_common(1)[0][0]
                start_t = datetime.strptime(str(peak_hour), "%H").strftime("%I %p").lstrip("0")
                end_t = datetime.strptime(str((peak_hour + 1) % 24), "%H").strftime("%I %p").lstrip("0")
                peak_str = f"{start_t} - {end_t}"

            return {"hotspot": top_zone, "hotspot_pct": hotspot_pct, "peak_hours": peak_str}
        except:
            return {"hotspot": "Error", "hotspot_pct": 0.0, "peak_hours": "Error"}

    # ==========================================
    # 🛡️ SYSTEM AUDITS & SECURITY LOGS
    # ==========================================
    def log_user_login(self, name, role):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO login_audit (employee_name, role, login_time) VALUES (%s, %s, %s)",
                           (name, role, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
            conn.commit()
            last_id = cursor.lastrowid
            conn.close()
            return last_id
        except:
            return None

    def log_user_logout(self, audit_id):
        if not audit_id: return
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE login_audit SET logout_time = %s WHERE audit_id = %s",
                           (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), audit_id))
            conn.commit()
            conn.close()
        except:
            pass

    def get_login_logs(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT employee_name, role, login_time, logout_time FROM login_audit ORDER BY login_time DESC")
            records = cursor.fetchall()
            conn.close()
            return records
        except:
            return []

    def log_security_event(self, user_id, action, details):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO security_logs (user_id, action_type, details) VALUES (%s, %s, %s)",
                           (user_id, action, details))
            conn.commit()
            conn.close()
        except:
            pass

    def get_security_logs(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = """
                SELECT sl.log_id, sl.user_id, IFNULL(CONCAT_WS(' ', u.first_name, u.last_name), 'Unknown User') AS employee_name, 
                       sl.action_type AS action, sl.details, sl.created_at AS timestamp, sl.is_read 
                FROM security_logs sl
                LEFT JOIN users u ON sl.user_id = u.employee_id 
                ORDER BY sl.created_at DESC
            """
            cursor.execute(query)
            records = cursor.fetchall()
            conn.close()
            return records
        except:
            return []

    def mark_alert_as_read(self, log_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE security_logs SET is_read = 1 WHERE log_id = %s", (log_id,))
            conn.commit()
            conn.close()
            return True
        except:
            return False

    # ==========================================
    # 🧠 MACHINE LEARNING & NLP UTILITIES
    # ==========================================
    def extract_root_words(self, text):
        if not text: return ""
        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()

        root_mapping = {
            'ingay': ['maingay', 'nagiingay', 'nag iingay', 'mag iingay', 'mag-iingay', 'ma-ingay', 'ingayan'],
            'away': ['nagaaway', 'nag-aaway', 'nag aaway', 'nagaway', 'nag-away', 'mag-aaway', 'magkaaway'],
            'utang': ['nangutang', 'umutang', 'mangungutang', 'pautang', 'inutang', 'uutang', 'utangan'],
            'nakaw': ['ninakaw', 'magnanakaw', 'ninakawan', 'nanakaw', 'ninanakaw', 'nagnakaw'],
            'kagat': ['kinagat', 'nangagat', 'nakagat', 'nangangagat', 'kinakagat'],
            'banta': ['nagbanta', 'binantaan', 'nagbabanta', 'pagbabanta', 'pananakot', 'nanakot', 'tinakot'],
            'chismis': ['chinismis', 'nagchichismisan', 'chismisan', 'tsismis', 'nagtsitsismisan', 'tsismosa',
                        'chismosa'],
            'kalat': ['nagkalat', 'makalat', 'kinakalat', 'nagkakalat', 'tapon', 'nagtapon']
        }

        found_roots = []
        for word in words:
            for root, variations in root_mapping.items():
                if word in variations or word == root:
                    if root not in found_roots: found_roots.append(root)
        return ", ".join(found_roots)

    def get_resolution_suggestion(self, narrative, zone, category):
        """Unified Smart Suggestion leveraging NLP and SequenceMatcher"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            # Use zone AND category for tighter filtering
            cursor.execute(
                "SELECT narrative, settlement_details FROM incidents WHERE status = 'Resolved' AND category = %s AND zone = %s",
                (category, zone))
            past_cases = cursor.fetchall()
            conn.close()

            if not past_cases: return []

            # 1. Get root words of current complaint
            current_roots = self.extract_root_words(narrative)

            suggestions = []
            for case in past_cases:
                past_narrative = case.get('narrative', '')
                settlement = case.get('settlement_details', '')
                if not past_narrative or not settlement: continue

                # 2. Get root words of past complaint
                past_roots = self.extract_root_words(past_narrative)

                # 3. Calculate similarity (Boosted if root words match!)
                similarity = difflib.SequenceMatcher(None, narrative.lower(), past_narrative.lower()).ratio()

                if current_roots and past_roots and any(r in past_roots for r in current_roots.split(', ')):
                    similarity += 0.3  # 30% Boost if root words match!

                match_percentage = int(min(similarity * 100, 100))  # Cap at 100%

                if match_percentage >= 40:
                    suggestions.append({'text': settlement, 'score': match_percentage})

            # Sort and return unique top 3
            suggestions.sort(key=lambda x: x['score'], reverse=True)
            unique_suggestions = []
            seen_texts = set()
            for s in suggestions:
                if s['text'] not in seen_texts:
                    unique_suggestions.append(s)
                    seen_texts.add(s['text'])
                if len(unique_suggestions) >= 3: break

            return unique_suggestions

        except Exception as e:
            print(f"AI Suggestion Error: {e}")
            return []

    def paraphrase_logic(self, old_settlement, comp_name, resp_name):
        new_text = old_settlement
        new_text = new_text.replace("respondent", resp_name).replace("complainant", comp_name)
        new_text = new_text.replace("Respondent", resp_name).replace("Complainant", comp_name)
        return new_text
