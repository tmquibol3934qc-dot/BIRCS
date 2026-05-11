import mysql.connector
from tkinter import messagebox
from datetime import datetime, timedelta
import re
import subprocess
import zipfile
import os
import time
from collections import Counter
import difflib


class DatabaseEngine:
    def __init__(self):
        # Database Configuration
        self.db_config = {
            'host': 'localhost',
            'user': 'root',  # Default MySQL user
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

    # --- REGISTRATION ---
    def register_user(self, employee_id, rfid_code, first_name, last_name, contact_no, password, q1, a1, q2, a2, q3, a3,
                      role, profile_pic=None):
        # 🚀 THE NULL MAGIC TRICK:
        if not rfid_code or str(rfid_code).strip() == "":
            rfid_code = None

        try:
            # 🚀 THE ULTIMATE FIX: Ginamit na natin yung get_connection() imbes na ghost variable!
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
                INSERT INTO users (
                    employee_id, rfid_code, first_name, last_name, contact_no, password, 
                    q1, a1, q2, a2, q3, a3, role, profile_pic
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            val = (
                employee_id, rfid_code, first_name, last_name, contact_no, password,
                q1, a1, q2, a2, q3, a3, role, profile_pic
            )

            cursor.execute(query, val)
            conn.commit()

            cursor.close()
            conn.close()  # Always close the connection!

            return True, "Account successfully registered!"

        except mysql.connector.IntegrityError as err:
            return False, f"Registration Failed: Employee ID or RFID might already exist.\n(Details: {err})"
        except mysql.connector.Error as err:
            return False, f"Database Error: {err}"
        except Exception as e:
            return False, f"System Error: {e}"



        # --- LOGIN (With RFID Support!) ---
    def authenticate_user(self, login_val, password=""):
            """Verifies credentials (Username OR Employee ID) OR RFID, and enforces suspensions"""
            try:
                conn = self.get_connection()
                cursor = conn.cursor(dictionary=True)

                if not password:
                    query = "SELECT * FROM users WHERE rfid_code = %s"
                    cursor.execute(query, (login_val,))
                else:
                    # 🚀 BARDAGULAN UPDATE: Tinuruan na natin ang system na basahin pati ang Temp Password!
                    query = """
                        SELECT * FROM users 
                        WHERE (username = %s OR employee_id = %s) 
                        AND (password = %s OR temp_password = %s)
                    """
                    # Doble yung password parameter kasi i-che-check niya in BOTH columns
                    cursor.execute(query, (login_val, login_val, password, password))

                user = cursor.fetchone()

                if not user:
                    conn.close()
                    return {"success": False, "message": "Invalid Credentials or Unregistered RFID."}

                # 🚀 BARDAGULAN UPDATE: ONE-TIME PASSWORD BURNER LOGIC
                # Kung ang tinype nilang password ay nag-match sa temp_password column,
                # buburahin na natin agad sa database para hindi na magamit ulit!
                if password and user.get('temp_password') == password:
                    cursor.execute("UPDATE users SET temp_password = NULL WHERE id = %s", (user['id'],))
                    conn.commit()
                # ---------------------------------------------------------

                status = user.get('status', 'Active')

                if status == 'Blocked':
                    conn.close()
                    return {"success": False,
                            "message": "ACCESS DENIED: This account has been permanently blocked by the Kapitan."}

                if status == 'Suspended':
                    suspend_until = user.get('suspension_until')

                    if suspend_until:
                        if datetime.now() < suspend_until:
                            formatted_time = suspend_until.strftime("%B %d, %Y at %I:%M %p")
                            conn.close()
                            return {"success": False,
                                    "message": f"ACCOUNT SUSPENDED.\n\nYou cannot log in until:\n{formatted_time}"}
                        else:
                            cursor.execute("UPDATE users SET status = 'Active', suspension_until = NULL WHERE id = %s",
                                           (user['id'],))
                            conn.commit()
                            user['status'] = 'Active'

                conn.close()
                return {"success": True, "user_data": user}

            except Exception as e:
                print(f"Auth Error: {e}")
                return {"success": False, "message": "Database connection error."}

    # --- CHECK USER (For Forgot Password) ---
    def check_user_exists(self, emp_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE employee_id = %s", (emp_id,))
            user = cursor.fetchone()
            conn.close()
            return user is not None
        except:
            return False

    # --- UPDATE RFID FOR USER ---
    def link_rfid_card(self, emp_id, rfid_code):
        """Links a scanned card to a specific user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            sql = "UPDATE users SET rfid_code = %s WHERE employee_id = %s"
            cursor.execute(sql, (rfid_code, emp_id))
            conn.commit()

            rows = cursor.rowcount
            conn.close()

            if rows > 0:
                return True, "RFID Linked Successfully!"
            else:
                return False, "User not found."
        except mysql.connector.IntegrityError:
            return False, "This Card is already linked to another user!"
        except Exception as e:
            return False, f"Error: {e}"

    # --- INCIDENTS MANAGEMENT ---
    def save_incident(self, comp, comp_contact, comp_address, resp, resp_contact, resp_address, date, time_str, zone,
                      category, narrative, officer, status):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            current_year = datetime.now().year
            cursor.execute("SELECT COUNT(*) as total FROM incidents WHERE YEAR(created_at) = %s", (current_year,))
            result = cursor.fetchone()

            total_cases = result['total'] if isinstance(result, dict) else result[0]
            next_number = total_cases + 1
            new_case_id = f"{current_year}-{next_number:03d}"

            query = """
                INSERT INTO incidents (
                    case_no, complainant_name, complainant_contact, complainant_address, 
                    respondent_name, respondent_contact, respondent_address, 
                    date_of_incident, exact_time, zone, category, narrative, processed_by, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                new_case_id, comp, comp_contact, comp_address,
                resp, resp_contact, resp_address,
                date, time_str, zone, category, narrative, officer, status
            )

            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True, new_case_id
        except Exception as e:
            print(f"Error saving incident: {e}")
            return False, str(e)

    def get_all_incidents(self):
        """Fetches active incidents (Auto-Archives Resolved cases older than 30 days)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT * FROM incidents 
                WHERE status != 'Resolved' 
                   OR (status = 'Resolved' AND created_at >= NOW() - INTERVAL 30 DAY)
                ORDER BY created_at DESC
            """

            cursor.execute(query)
            records = cursor.fetchall()
            conn.close()
            return records
        except Exception as e:
            print(f"Error fetching incidents: {e}")
            return []

    def get_dashboard_stats(self):
        """Calculates the numbers for the Dashboard stat cards"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT status, COUNT(*) as count FROM incidents GROUP BY status")
            rows = cursor.fetchall()
            conn.close()

            stats = {'Total Cases': 0, 'Pending': 0, 'Resolved': 0, 'Urgent': 0}
            for row in rows:
                stats['Total Cases'] += row['count']
                if row['status'] in stats:
                    stats[row['status']] = row['count']
            return stats
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return {'Total Cases': 0, 'Pending': 0, 'Resolved': 0, 'Urgent': 0}

    def get_incident_analytics(self):
        """Calculates the top hotspot and peak hours from all incidents"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT zone, exact_time FROM incidents")
            records = cursor.fetchall()
            conn.close()

            if not records:
                return {"hotspot": "No Data", "hotspot_pct": 0.0, "peak_hours": "No Data"}

            zones = [r['zone'] for r in records if r['zone']]
            if zones:
                zone_counts = Counter(zones)
                top_zone, top_count = zone_counts.most_common(1)[0]
                hotspot_pct = top_count / len(zones)
            else:
                top_zone = "Unknown"
                hotspot_pct = 0.0

            hours = []
            for r in records:
                t_str = r['exact_time']
                if t_str:
                    try:
                        t_obj = datetime.strptime(t_str, "%I:%M %p")
                        hours.append(t_obj.hour)
                    except:
                        pass

            if hours:
                hour_counts = Counter(hours)
                peak_hour = hour_counts.most_common(1)[0][0]
                start_time = datetime.strptime(str(peak_hour), "%H").strftime("%I %p").lstrip("0")
                end_time = datetime.strptime(str((peak_hour + 1) % 24), "%H").strftime("%I %p").lstrip("0")
                peak_str = f"{start_time} - {end_time}"
            else:
                peak_str = "Unknown"

            return {"hotspot": top_zone, "hotspot_pct": hotspot_pct, "peak_hours": peak_str}

        except Exception as e:
            print(f"Error getting analytics: {e}")
            return {"hotspot": "Error", "hotspot_pct": 0.0, "peak_hours": "Error"}

    def update_incident_resolution(self, case_id, settlement_text, stage, deadline, officer_name):
        """Smart save: Auto-detects if it should save to Phase 1 or Phase 2"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT settlement_details FROM incidents WHERE case_no = %s", (case_id,))
            case = cursor.fetchone()

            if case and case.get('settlement_details'):
                query = """
                    UPDATE incidents 
                    SET settlement_details_2 = %s, hearing_stage = %s, compliance_deadline = %s, 
                        processed_by = %s, status = 'Resolved' 
                    WHERE case_no = %s
                """
            else:
                query = """
                    UPDATE incidents 
                    SET settlement_details = %s, hearing_stage = %s, compliance_deadline = %s, 
                        processed_by = %s, status = 'Resolved' 
                    WHERE case_no = %s
                """

            cursor.execute(query, (settlement_text, stage, deadline, officer_name, case_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Resolution Save Error: {e}")
            return False

    def get_smart_suggestion(self, current_narrative, zone):
        """Uses TF-IDF Machine Learning to find the closest past settlement"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                    SELECT narrative, settlement_details \
                    FROM incidents
                    WHERE status = 'Resolved' \
                      AND zone = %s
                      AND settlement_details IS NOT NULL \
                      AND settlement_details != '' \
                    """
            cursor.execute(query, (zone,))
            past_cases = cursor.fetchall()
            conn.close()

            if not past_cases:
                return ["No past data for this zone yet. Manual entry required."]

            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            past_narratives = [case['narrative'] for case in past_cases]
            past_narratives.append(current_narrative)

            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(past_narratives)

            similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
            best_match_index = similarities[0].argmax()
            best_score = similarities[0][best_match_index]

            if best_score < 0.1:
                return ["No highly similar past cases found. Please manually formulate a settlement."]

            best_settlement = past_cases[best_match_index]['settlement_details']
            return [f"+ {best_settlement}"]

        except Exception as e:
            print(f"ML Error: {e}")
            return ["Error generating AI suggestion. Check terminal."]

    def verify_kapitan_access(self, scanned_rfid):
        """Checks the database using the correct rfid_code column and scrubs hidden keystrokes"""
        try:
            clean_rfid = scanned_rfid.strip()
            print(f"\n--- RFID SCANNER DIAGNOSTIC ---")
            print(f"Cleaned scan for database: '{clean_rfid}'")

            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM users WHERE rfid_code = %s"
            cursor.execute(query, (clean_rfid,))
            user = cursor.fetchone()
            conn.close()

            if user:
                print(f"-> SUCCESS: Found user in database: {user.get('first_name')} {user.get('last_name')}")
                db_role = user.get('role', '')
                db_pos = user.get('position', '')

                if db_role == 'Kapitan' or db_pos == 'Kapitan':
                    print("-> VERIFIED: Kapitan access granted.")
                    return True, user
                else:
                    print(f"-> REJECTED: User exists, but rank is Role: '{db_role}', Position: '{db_pos}'")
                    return False, None
            else:
                print("-> REJECTED: Could not find that exact rfid_code in the database.")
                return False, None

        except Exception as e:
            print(f"CRITICAL DB ERROR: {e}")
            return False

    # ==========================================
    # AI SMART SUGGESTION ENGINE
    # ==========================================
    def get_resolution_suggestion(self, narrative, zone, category):
        try:
            print(f"\n--- AI DEBUG START ---")
            print(f"Searching for: Category='{category}' in table 'incidents'")

            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT narrative, settlement_details 
                FROM incidents 
                WHERE status = 'Resolved' AND category = %s
            """
            cursor.execute(query, (category,))
            past_cases = cursor.fetchall()
            conn.close()

            print(f"Found {len(past_cases)} resolved cases.")

            if not past_cases:
                return []

            suggestions = []
            for case in past_cases:
                past_narrative = case.get('narrative', '')
                settlement = case.get('settlement_details', '')

                if not past_narrative or not settlement:
                    continue

                similarity = difflib.SequenceMatcher(None, narrative.lower(), past_narrative.lower()).ratio()
                match_percentage = int(similarity * 100)

                if match_percentage >= 40:
                    suggestions.append({
                        'text': settlement,
                        'score': match_percentage
                    })

            suggestions.sort(key=lambda x: x['score'], reverse=True)

            unique_suggestions = []
            seen_texts = set()
            for s in suggestions:
                if s['text'] not in seen_texts:
                    unique_suggestions.append(s)
                    seen_texts.add(s['text'])
                if len(unique_suggestions) >= 3:
                    break

            print(f"--- AI DEBUG END ---\n")
            return unique_suggestions

        except Exception as e:
            print(f"AI Suggestion Error: {e}")
            return []

    def get_next_case_id(self):
        """Peeks at the database to calculate what the next Case ID will be"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT MAX(case_no) as max_id FROM incidents")
            result = cursor.fetchone()
            conn.close()

            if result and result['max_id']:
                return result['max_id'] + 1
            else:
                return 1
        except Exception as e:
            print(f"Error calculating next ID: {e}")
            return "???"

    def get_all_users(self):
        """Fetches all registered users for the Admin Dashboard"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
            conn.close()
            return users
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []

    def get_user_performance_stats(self, officer_name):
        """Counts how many cases an officer has handled and resolved"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("SELECT COUNT(*) as total FROM incidents WHERE processed_by = %s", (officer_name,))
            total_handled = cursor.fetchone()['total']

            cursor.execute("SELECT COUNT(*) as resolved FROM incidents WHERE processed_by = %s AND status = 'Resolved'",
                           (officer_name,))
            total_resolved = cursor.fetchone()['resolved']

            conn.close()
            return {"handled": total_handled, "resolved": total_resolved}
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return {"handled": 0, "resolved": 0}

    def update_user_account(self, user_id, first_name, last_name, employee_id, password, role, status, rfid_code,
                            suspend_val=0, suspend_type="Hours", profile_pic=None):
        """Updates user details and automatically CLEARS any pending password resets"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            suspend_until = None

            if status == "Suspended":
                if suspend_type == "Hours":
                    suspend_until = datetime.now() + timedelta(hours=int(suspend_val))
                else:
                    suspend_until = datetime.now() + timedelta(days=int(suspend_val))

            # 🚀 BARDAGULAN UPDATE: Isinama na natin ang pag-clear sa temp_password at is_pending_reset
            query = """
                UPDATE users 
                SET first_name=%s, last_name=%s, employee_id=%s, password=%s, role=%s, status=%s, 
                    suspension_until=%s, rfid_code=%s, profile_pic=%s,
                    temp_password=NULL, is_pending_reset=0
                WHERE id=%s
            """

            # Siguraduhing tugma ang bilang ng variables sa %s
            cursor.execute(query, (first_name, last_name, employee_id, password, role, status, suspend_until, rfid_code,
                                   profile_pic, user_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user: {e}")
            return False

    def get_my_pending_cases(self, officer_name, role):
        """Fetches pending cases. Staff only see their own. Kapitan sees all."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            if role.lower() in ['kapitan', 'admin']:
                query = "SELECT * FROM incidents WHERE status != 'Resolved' ORDER BY created_at DESC"
                cursor.execute(query)
            else:
                query = "SELECT * FROM incidents WHERE status != 'Resolved' AND processed_by = %s ORDER BY created_at DESC"
                cursor.execute(query, (officer_name,))

            records = cursor.fetchall()
            conn.close()
            return records
        except Exception as e:
            print(f"Error fetching pending cases: {e}")
            return []

    # ==========================================
    # FORGOT PASSWORD SYSTEM
    # ==========================================
    def get_user_security_questions(self, emp_id):
        """Fetches the 3 security questions for a specific employee ID"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT q1, q2, q3 FROM users WHERE employee_id = %s OR username = %s", (emp_id, emp_id))
            user = cursor.fetchone()
            conn.close()
            return user
        except Exception as e:
            print(f"Error fetching questions: {e}")
            return None

    def verify_security_answers(self, emp_id, a1, a2, a3):
        """Checks if the provided answers match the database (Case-Insensitive)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT a1, a2, a3 FROM users WHERE employee_id = %s OR username = %s", (emp_id, emp_id))
            user = cursor.fetchone()
            conn.close()

            if user:
                if (user['a1'].strip().lower() == a1.strip().lower() and
                        user['a2'].strip().lower() == a2.strip().lower() and
                        user['a3'].strip().lower() == a3.strip().lower()):
                    return True
            return False
        except Exception as e:
            print(f"Error verifying answers: {e}")
            return False

    def reset_user_password(self, emp_id, new_password):
        """Saves the new password to the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET password = %s WHERE employee_id = %s OR username = %s",
                           (new_password, emp_id, emp_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error resetting password: {e}")
            return False

    def get_incident_categories(self):
        """Fetches a list of all unique categories ever typed into the system"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT category FROM incidents WHERE category IS NOT NULL AND category != ''")
            results = cursor.fetchall()
            conn.close()

            if results:
                return [row[0] for row in results]
            else:
                return ["Theft", "Physical Assault", "Noise Complaint", "Property Damage", "Trespassing"]
        except Exception as e:
            print(f"Error fetching categories: {e}")
            return ["Theft", "Physical Assault", "Noise Complaint", "Property Damage"]

    def advanced_search_incidents(self, keyword="", category="All Categories"):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # 🚀 BARDAGULAN FILTER: 'created_at >= NOW() - INTERVAL 1 MONTH'
            # Ibig sabihin, yung mga record lang na pasok sa huling 30 days ang ilalabas ng query.
            query = """
                SELECT * FROM incidents 
                WHERE (case_no LIKE %s OR complainant_name LIKE %s OR respondent_name LIKE %s)
                AND created_at >= NOW() - INTERVAL 1 MONTH
            """
            params = [f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"]

            if category != "All Categories":
                query += " AND category = %s"
                params.append(category)

            query += " ORDER BY case_no DESC"

            cursor.execute(query, tuple(params))
            result = cursor.fetchall()
            conn.close()

            return result
        except Exception as e:
            print(f"Search Error: {e}")
            return []

    def reopen_case_direct(self, case_no, second_narrative):
        """Staff directly re-opens a case. Sets to Pending and saves Narrative 2."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = "UPDATE incidents SET status = 'Pending', narrative_2 = %s WHERE case_no = %s"
            cursor.execute(query, (second_narrative, case_no))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Direct Reopen Error: {e}")
            return False

    # ==========================================
    # APPEALS & KAPITAN APPROVAL SYSTEM
    # ==========================================
    def request_case_reopen(self, case_no, new_narrative):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # 🛑 BOUNCER CHECK: I-check kung lagpas na sa 1 month ang kaso
            cursor.execute("SELECT created_at FROM incidents WHERE case_no = %s", (case_no,))
            case = cursor.fetchone()

            if case:
                # Kung lumampas na sa 30 days ang created_at, bawal na i-reopen!
                if case['created_at'] < datetime.now() - timedelta(days=30):
                    conn.close()
                    return False  # Reject the request

            # Kung pasok pa sa 30 days, tuloy ang request
            query = "UPDATE incidents SET reopen_status = 'Requested', narrative_2 = %s, reopen_requested_at = NOW() WHERE case_no = %s"
            cursor.execute(query, (new_narrative, case_no))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False

    def get_reopen_requests(self):
        """Kapitan fetches all pending appeals"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM incidents WHERE reopen_status = 'Requested'")
            results = cursor.fetchall()
            conn.close()
            return results
        except Exception as e:
            return []

    def handle_reopen_request(self, case_no, action):
        """Kapitan approves or denies the request"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if action == 'Approve':
                query = "UPDATE incidents SET status = 'Pending', reopen_status = 'Approved' WHERE case_no = %s"
            else:
                query = "UPDATE incidents SET reopen_status = 'Denied' WHERE case_no = %s"
            cursor.execute(query, (case_no,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False

    def log_user_login(self, employee_name, role):
        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            conn = self.get_connection()
            cursor = conn.cursor()

            query = "INSERT INTO login_audit (employee_name, role, login_time) VALUES (%s, %s, %s)"
            cursor.execute(query, (employee_name, role, current_time))

            conn.commit()
            audit_id = cursor.lastrowid

            conn.close()
            return audit_id
        except Exception as e:
            print(f"Failed to log login: {e}")
            return None

    def log_user_logout(self, audit_id):
        if not audit_id:
            return

        try:
            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            conn = self.get_connection()
            cursor = conn.cursor()

            query = "UPDATE login_audit SET logout_time = %s WHERE audit_id = %s"
            cursor.execute(query, (current_time, audit_id))

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Failed to log logout: {e}")

    def get_login_logs(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = "SELECT employee_name, role, login_time, logout_time FROM login_audit ORDER BY login_time DESC"
            cursor.execute(query)

            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]

            cursor.close()
            conn.close()
            return results
        except Exception as e:
            print(f"Error fetching logs: {e}")
            return []

    def log_security_event(self, user_id, action, details):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            query = "INSERT INTO security_logs (user_id, action_type, details) VALUES (%s, %s, %s)"
            cursor.execute(query, (user_id, action, details))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Security Logging Error: {e}")

    # ==========================================
    # SECURITY ALERTS LOGIC
    # ==========================================
    def get_security_logs(self):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                SELECT 
                    sl.log_id, 
                    sl.user_id, 
                    IFNULL(CONCAT_WS(' ', u.first_name, u.last_name), 'Unknown User') AS employee_name, 
                    sl.action_type AS action, 
                    sl.details, 
                    sl.created_at AS timestamp, 
                    sl.is_read 
                FROM security_logs sl
                LEFT JOIN users u ON sl.user_id = u.employee_id 
                ORDER BY sl.created_at DESC
            """

            cursor.execute(query)
            records = cursor.fetchall()
            conn.close()
            return records

        except Exception as e:
            print(f"Error fetching security logs: {e}")
            return []

    def get_security_alerts(self):
        try:
            # 🚀 THE ULTIMATE FIX: Ginamit din natin si get_connection dito!
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = "SELECT * FROM security_logs ORDER BY created_at DESC"
            cursor.execute(query)

            records = cursor.fetchall()
            conn.close()
            return records
        except Exception as e:
            print(f"Error fetching alerts: {e}")
            return []

    def mark_security_log_read(self, log_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = "UPDATE security_logs SET is_read = 1 WHERE log_id = %s"
            cursor.execute(query, (log_id,))
            conn.commit()

            conn.close()
            return True
        except Exception as e:
            print(f"Error marking log as read: {e}")
            return False

    def paraphrase_logic(self, old_settlement, comp_name, resp_name):
        new_text = old_settlement
        new_text = new_text.replace("respondent", resp_name)
        new_text = new_text.replace("complainant", comp_name)
        new_text = new_text.replace("Respondent", resp_name)
        new_text = new_text.replace("Complainant", comp_name)
        return new_text

    def mark_alert_as_read(self, log_id):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = "UPDATE security_logs SET is_read = 1 WHERE log_id = %s"
            cursor.execute(query, (log_id,))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Failed to mark alert as read: {e}")
            return False

    # ==========================================
    # 🧠 NLP & TEXT PROCESSING UTILITIES
    # ==========================================
    def extract_root_words(self, text):
        if not text:
            return ""

        clean_text = re.sub(r'[^\w\s]', '', text.lower())
        words = clean_text.split()

        root_mapping = {
            'ingay': ['maingay', 'nagiingay', 'nag iingay', 'mag iingay', 'mag-iingay', 'ma-ingay', 'ingayan',
                      'maingay'],
            'away': ['nagaaway', 'nag-aaway', 'nag aaway', 'nagaway', 'nag-away', 'mag-aaway', 'magkaaway',
                     'nag-aaway-away'],
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
                    if root not in found_roots:
                        found_roots.append(root)

        return ", ".join(found_roots)

    def get_timeframe_analytics(self, timeframe="This Month"):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM incidents WHERE 1=1"

            if timeframe == "This Week":
                query += " AND created_at >= NOW() - INTERVAL 7 DAY"
            elif timeframe == "This Month":
                query += " AND created_at >= NOW() - INTERVAL 30 DAY"
            elif timeframe == "This Year":
                query += " AND YEAR(created_at) = YEAR(NOW())"

            cursor.execute(query)
            records = cursor.fetchall()
            conn.close()

            total = len(records)
            resolved = sum(1 for r in records if r['status'] == 'Resolved')
            pending = sum(1 for r in records if r['status'] in ['Pending', 'Urgent'])

            categories = [r['category'] for r in records if r['category']]
            top_cat = Counter(categories).most_common(1)[0][0] if categories else "N/A"

            zones = [r['zone'] for r in records if r['zone']]
            top_zone = Counter(zones).most_common(1)[0][0] if zones else "N/A"

            hours = []
            for r in records:
                if r.get('exact_time'):
                    try:
                        hours.append(datetime.strptime(r['exact_time'], "%I:%M %p").hour)
                    except:
                        pass

            peak_str = "N/A"
            if hours:
                peak_hour = Counter(hours).most_common(1)[0][0]
                start_t = datetime.strptime(str(peak_hour), "%H").strftime("%I %p").lstrip("0")
                end_t = datetime.strptime(str((peak_hour + 1) % 24), "%H").strftime("%I %p").lstrip("0")
                peak_str = f"{start_t} - {end_t}"

            return {
                "timeframe": timeframe,
                "total": total,
                "resolved": resolved,
                "pending": pending,
                "top_category": top_cat,
                "top_zone": top_zone,
                "peak_hours": peak_str
            }
        except Exception as e:
            print(f"Analytics Error: {e}")
            return {"total": 0, "resolved": 0, "pending": 0, "top_category": "Error", "top_zone": "Error",
                    "peak_hours": "Error"}

    # ==========================================
    # BACKUP & DISASTER RECOVERY (TIME MACHINE)
    # ==========================================
    def create_database_backup(self, zip_filepath):
        db_user = "root"
        db_pass = ""
        db_name = "bircs_db"

        temp_sql = "temp_backup.sql"

        try:
            dump_cmd = f"C:/xampp/mysql/bin/mysqldump.exe -u {db_user} {db_name} > {temp_sql}"
            subprocess.run(dump_cmd, shell=True, check=True)

            with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(temp_sql, f"{db_name}_backup.sql")

            if os.path.exists(temp_sql):
                os.remove(temp_sql)

            return True, "Backup successfully secured and compressed."
        except Exception as e:
            return False, f"Database backup failed: {str(e)}"

    def execute_rollback(self, target_zip_filepath, emergency_backup_filepath):
        success, msg = self.create_database_backup(emergency_backup_filepath)
        if not success:
            return False, f"SAFETY NET FAILED!\nRollback aborted to prevent data loss.\nError: {msg}"

        db_user = "root"
        db_pass = ""
        db_name = "bircs_db"
        temp_sql = "temp_restore.sql"

        try:
            with zipfile.ZipFile(target_zip_filepath, 'r') as zipf:
                sql_filename = zipf.namelist()[0]
                zipf.extract(sql_filename, ".")
                os.rename(sql_filename, temp_sql)

            restore_cmd = f"C:/xampp/mysql/bin/mysql.exe -u {db_user} {db_name} < {temp_sql}"
            subprocess.run(restore_cmd, shell=True, check=True)

            if os.path.exists(temp_sql):
                os.remove(temp_sql)

            return True, "TIME MACHINE SUCCESS: Database has been restored!"
        except Exception as e:
            return False, f"Rollback execution failed: {str(e)}"

    # ==========================================
    # TIME-SCOPED LOGS OPTIMIZATION
    # ==========================================
    def get_optimized_logs(self, filter_date=None, limit=50):
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            if filter_date:
                query = "SELECT * FROM login_audit WHERE login_time LIKE %s ORDER BY login_time DESC"
                cursor.execute(query, (f"{filter_date}%",))
            else:
                query = "SELECT * FROM login_audit ORDER BY login_time DESC LIMIT %s"
                cursor.execute(query, (limit,))

            result = cursor.fetchall()
            conn.close()
            return result
        except Exception as e:
            print(f"Database Error (Logs): {e}")
            return []

        # 1. Update the Request Function
    def create_password_reset_request(self, emp_id, temp_password, requested_new_password):
            """Saves the temp pass AND securely parks the requested new password"""
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                # 🚀 POGI UPDATE: Sinesave na natin yung requested_password
                query = """
                    UPDATE users 
                    SET temp_password = %s, requested_password = %s, is_pending_reset = 1 
                    WHERE employee_id = %s OR username = %s
                """
                cursor.execute(query, (temp_password, requested_new_password, emp_id, emp_id))
                conn.commit()
                conn.close()
                return True
            except Exception as e:
                print(f"Engine Error (Temp Pass): {e}")
                return False

        # 2. Add this NEW function for Kapitan's Approval
    def approve_pending_password(self, emp_id):
            """Moves the parked password to the main password and clears flags"""
            try:
                conn = self.get_connection()
                cursor = conn.cursor()
                # 🚀 POGI UPDATE: Ang ganda ng logic nito, ita-transfer niya lang!
                query = """
                    UPDATE users 
                    SET password = requested_password, 
                        requested_password = NULL, 
                        temp_password = NULL, 
                        is_pending_reset = 0 
                    WHERE (employee_id = %s OR username = %s) AND requested_password IS NOT NULL
                """
                cursor.execute(query, (emp_id, emp_id))
                affected_rows = cursor.rowcount
                conn.commit()
                conn.close()
                return affected_rows > 0
            except Exception as e:
                print(f"Error approving password: {e}")
                return False

    def check_if_pending_reset(self, emp_id):
        """Checks if the user already has a pending password reset request"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)
            # Titingnan natin yung is_pending_reset column na ginawa natin kanina
            cursor.execute("SELECT is_pending_reset FROM users WHERE employee_id = %s OR username = %s",
                           (emp_id, emp_id))
            result = cursor.fetchone()
            conn.close()

            if result and result['is_pending_reset'] == 1:
                return True
            return False
        except Exception as e:
            print(f"Error checking pending status: {e}")
            return False

# ==========================================
    # TIME-BASED RE-OPEN LOGIC (THE AUTO-JANITOR)
    # ==========================================
    def auto_manage_reopen_cases(self):
        """Automatically drops expired requests and abandons neglected approved cases"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 🛑 RULE 1: Kung 3 days na hindi pa rin ina-approve ni Kapitan, DROP THE REQUEST.
            # I-babalik sa normal at buburahin yung narrative_2 na tinype nila para malinis.
            query_drop_pending = """
                UPDATE incidents 
                SET reopen_status = 'Dropped', narrative_2 = NULL 
                WHERE reopen_status = 'Requested' 
                AND reopen_requested_at < NOW() - INTERVAL 3 DAY
            """
            cursor.execute(query_drop_pending)

            # 🛑 RULE 2: Kung na-approve na ni Kapitan, pero 3 days na nakalipas wala pa ring settlement
            # (nakalimutan ng staff o di sumipot yung tao), ABANDON THE CASE. Back to Resolved.
            query_abandon_approved = """
                UPDATE incidents 
                SET reopen_status = 'Abandoned', status = 'Resolved' 
                WHERE reopen_status = 'Approved' 
                AND status IN ('Pending', 'In Progress') 
                AND reopen_approved_at < NOW() - INTERVAL 3 DAY 
                AND (settlement_details_2 IS NULL OR settlement_details_2 = '')
            """
            cursor.execute(query_abandon_approved)

            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Auto-Janitor Error: {e}")

    # 🚀 BARDAGULAN UPDATE: Kailangan nating i-record kung kailan pinindot yung request!
    def request_case_reopen(self, case_no, new_narrative):
        """Staff requests a re-open. Flags it for the Kapitan with a Timestamp."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            # Nilagyan natin ng NOW() yung reopen_requested_at
            query = "UPDATE incidents SET reopen_status = 'Requested', narrative_2 = %s, reopen_requested_at = NOW() WHERE case_no = %s"
            cursor.execute(query, (new_narrative, case_no))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False

    # 🚀 BARDAGULAN UPDATE: Kailangan nating i-record kung kailan in-approve ni Kapitan!
    def handle_reopen_request(self, case_no, action):
        """Kapitan approves or denies the request"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            if action == 'Approve':
                # Nilagyan natin ng NOW() yung reopen_approved_at
                query = "UPDATE incidents SET status = 'Pending', reopen_status = 'Approved', reopen_approved_at = NOW() WHERE case_no = %s"
            else:
                query = "UPDATE incidents SET reopen_status = 'Denied' WHERE case_no = %s"
            cursor.execute(query, (case_no,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            return False
