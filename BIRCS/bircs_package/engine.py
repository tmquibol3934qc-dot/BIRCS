import mysql.connector
from tkinter import messagebox
from datetime import datetime, timedelta


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
            print("✅ Successfully connected to MySQL!")
        except Exception as e:
            print(f"❌ Error connecting to MySQL: {e}")
            messagebox.showerror("Database Error", f"Could not connect to MySQL.\nError: {e}")

    def get_connection(self):
        """Creates a new connection to the MySQL database"""
        return mysql.connector.connect(**self.db_config)

    # --- REGISTRATION ---
    def register_user(self, data):
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # 1. Update SQL to include 'role' column
            sql = """
                  INSERT INTO users
                  (employee_id, rfid_code, first_name, last_name, role, contact_no, password, q1, a1, q2, a2, q3, a3)
                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                  """

            parts = data['name'].split()
            fname = parts[0]
            lname = " ".join(parts[1:]) if len(parts) > 1 else ""

            # 2. Add data['position'] to the values list (matching the order above)
            values = (
                data['emp_id'],
                data['rfid'],
                fname,
                lname,
                data['position'],  # <--- This inserts the Title into the 'role' column
                "N/A",
                data['pass'],
                data['q1'], data['a1'],
                data['q2'], data['a2'],
                data['q3'], data['a3']
            )

            cursor.execute(sql, values)
            conn.commit()

            cursor.close()
            conn.close()
            return True, "Registration Successful!"

        except mysql.connector.IntegrityError as e:
            if "rfid_code" in str(e):
                return False, "This RFID Card is already registered!"
            return False, "Employee ID already exists."
        except Exception as e:
            return False, f"Database Error: {e}"

    # --- LOGIN (With RFID Support!) ---\
    def authenticate_user(self, login_val, password=""):
        """Verifies credentials (Username OR Employee ID) OR RFID, and enforces suspensions"""
        try:
            from datetime import datetime
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # --- 1. LOGIN TYPE CHECK (RFID vs Manual) ---
            if not password:
                # No password means it was an RFID scan!
                query = "SELECT * FROM users WHERE rfid_code = %s OR employee_id = %s"
                cursor.execute(query, (login_val, login_val))
            else:
                # Normal manual login!
                # THE FIX: Now it checks if the text you typed matches EITHER the username OR the employee_id!
                query = "SELECT * FROM users WHERE (username = %s OR employee_id = %s) AND password = %s"
                cursor.execute(query, (login_val, login_val, password))

            user = cursor.fetchone()

            if not user:
                conn.close()
                return {"success": False, "message": "Invalid Credentials or Unregistered RFID."}

            # --- 2. SECURITY & SUSPENSION CHECK ---
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

    # --- NEW: UPDATE RFID FOR USER ---
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

    def save_incident(self, case_no, comp_name, resp_name, contact, address, inc_date, inc_time, zone, narrative,
                      processed_by, status):
        """Saves a new incident blotter to the database"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Added 'status' to the INSERT columns and an extra %s to the VALUES
            query = """
                    INSERT INTO incidents
                    (case_no, complainant_name, respondent_name, contact_number, last_known_address,
                     date_of_incident, exact_time, zone, narrative, processed_by, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                    """
            # Added status to the end of the values tuple
            values = (case_no, comp_name, resp_name, contact, address, inc_date, inc_time, zone, narrative,
                      processed_by, status)

            cursor.execute(query, values)
            conn.commit()
            conn.close()
            return True, "Incident recorded successfully!"

        except Exception as e:
            return False, f"Database error: {e}"

    def get_all_incidents(self):
        """Fetches active incidents (Auto-Archives Resolved cases older than 30 days)"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # --- THE TIME TRAVEL SQL TRICK ---
            # It fetches everything that IS NOT Resolved.
            # If it IS Resolved, it only fetches it if the created_at date is within the last 30 days!
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

            # If the database is empty, return defaults
            if not records:
                return {"hotspot": "No Data", "hotspot_pct": 0.0, "peak_hours": "No Data"}

            from collections import Counter
            from datetime import datetime

            # --- 1. HOTSPOT MATH ---
            zones = [r['zone'] for r in records if r['zone']]
            if zones:
                zone_counts = Counter(zones)
                top_zone, top_count = zone_counts.most_common(1)[0]
                hotspot_pct = top_count / len(zones)  # Calculate percentage
            else:
                top_zone = "Unknown"
                hotspot_pct = 0.0

            # --- 2. PEAK HOUR MATH ---
            hours = []
            for r in records:
                t_str = r['exact_time']
                if t_str:
                    try:
                        # Convert "03:15 PM" into a strict hour block (e.g., 15)
                        t_obj = datetime.strptime(t_str, "%I:%M %p")
                        hours.append(t_obj.hour)
                    except:
                        pass

            if hours:
                hour_counts = Counter(hours)
                peak_hour = hour_counts.most_common(1)[0][0]

                # Format back to nice 12-hour AM/PM text (e.g., "3 PM - 4 PM")
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
        """Updates the incident with the final resolution details in the EXACT correct order"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # The order of the %s here is:
            # 1. settlement, 2. stage, 3. deadline, 4. officer, 5. case_id
            query = """
                    UPDATE incidents
                    SET settlement_details  = %s,
                        hearing_stage       = %s,
                        compliance_deadline = %s,
                        status              = 'Resolved',
                        processed_by        = %s
                    WHERE case_no = %s \
                    """

            # This tuple MUST perfectly match the order of the %s above!
            cursor.execute(query, (settlement_text, stage, deadline, officer_name, case_id))
            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"CRITICAL DB SAVE ERROR: {e}")
            return False

    def get_smart_suggestion(self, current_narrative, zone):
        """Uses TF-IDF Machine Learning to find the closest past settlement"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # 1. Fetch only RESOLVED cases from the SAME ZONE that have a settlement
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

            # If there is no history for this zone yet, return a default message
            if not past_cases:
                return ["No past data for this zone yet. Manual entry required."]

            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            # 2. Prepare the text for the ML
            past_narratives = [case['narrative'] for case in past_cases]
            past_narratives.append(current_narrative)  # Add the current unsolved case at the end

            # 3. The Math: Convert words to numbers and compare them
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform(past_narratives)

            # Compare the very last item (current case) against all previous items
            similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])

            # 4. Find the absolute best match
            best_match_index = similarities[0].argmax()
            best_score = similarities[0][best_match_index]

            # If it's a completely unique case with no similarities
            if best_score < 0.1:
                return ["No highly similar past cases found. Please manually formulate a settlement."]

            # 5. Grab the settlement from that best match!
            best_settlement = past_cases[best_match_index]['settlement_details']

            return [f"+ {best_settlement}"]

        except Exception as e:
            print(f"ML Error: {e}")
            return ["Error generating AI suggestion. Check terminal."]

    def verify_kapitan_access(self, scanned_rfid):
        """Checks the database using the correct rfid_code column and scrubs hidden keystrokes"""
        try:
            # 1. Scrub the hidden "Enter" key or spaces off the scan
            clean_rfid = scanned_rfid.strip()

            print(f"\n--- RFID SCANNER DIAGNOSTIC ---")
            print(f"Cleaned scan for database: '{clean_rfid}'")

            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # 2. THE FIX: Search using the exact 'rfid_code' column!
            query = "SELECT * FROM users WHERE rfid_code = %s"
            cursor.execute(query, (clean_rfid,))
            user = cursor.fetchone()
            conn.close()

            if user:
                print(f"-> SUCCESS: Found user in database: {user.get('first_name')} {user.get('last_name')}")

                db_role = user.get('role', '')
                db_pos = user.get('position', '')

                # 3. Check if they are actually the Kapitan
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

    def get_resolution_suggestion(self, new_narrative, zone):
        """Uses NLP to find the Top 5 best matching past settlements (40% match minimum)"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            query = """
                    SELECT narrative, settlement_details
                    FROM incidents
                    WHERE status = 'Resolved' 
                      AND zone = %s
                      AND settlement_details IS NOT NULL 
                      AND settlement_details != '' 
                    """
            cursor.execute(query, (zone,))
            past_cases = cursor.fetchall()
            conn.close()

            if not past_cases:
                return []  # Return an empty list if there's no data

            narratives = [case['narrative'] for case in past_cases]
            narratives.append(new_narrative)

            # Our custom Tagalog/English stop words!
            custom_stop_words = [
                "ang", "mga", "sa", "na", "ng", "ay", "at", "kung", "may",
                "para", "naman", "ba", "ito", "iyon", "dito", "doon",
                "pa", "ako", "ikaw", "siya", "kami", "kayo", "sila",
                "din", "rin", "po", "opo", "ni", "nila", "namin", "ninyo", "niyo",
                "the", "and", "is", "in", "to", "of", "it", "that", "this"
            ]

            vectorizer = TfidfVectorizer(stop_words=custom_stop_words)
            tfidf_matrix = vectorizer.fit_transform(narratives)

            # Get the scores
            cosine_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()
            top_indices = cosine_similarities.argsort()[::-1][:5]

            suggestions = []

            for idx in top_indices:
                score = cosine_similarities[idx]

                # --- THE 40% FIX: Only grab it if it's highly relevant! ---
                if score >= 0.40:
                    pct = int(score * 100)
                    settlement = past_cases[idx]['settlement_details'].strip()

                    # Instead of a string, we pack it into a neat little dictionary
                    suggestions.append({
                        "match": pct,
                        "text": settlement
                    })

            return suggestions

        except Exception as e:
            print(f"\n--- MACHINE LEARNING ERROR ---")
            print(f"Details: {e}")
            return []

    def get_next_case_id(self):
        """Peeks at the database to calculate what the next Case ID will be"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            # Find the highest existing case_no
            cursor.execute("SELECT MAX(case_no) as max_id FROM incidents")
            result = cursor.fetchone()
            conn.close()

            # If the database has cases, add 1. If it's completely empty, start at 1!
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
            cursor.execute("SELECT * FROM users")  # Adjust table name if yours is different!
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

            # Count Total Handled (Any status)
            cursor.execute("SELECT COUNT(*) as total FROM incidents WHERE processed_by = %s", (officer_name,))
            total_handled = cursor.fetchone()['total']

            # Count Resolved
            cursor.execute("SELECT COUNT(*) as resolved FROM incidents WHERE processed_by = %s AND status = 'Resolved'",
                           (officer_name,))
            total_resolved = cursor.fetchone()['resolved']

            conn.close()
            return {"handled": total_handled, "resolved": total_resolved}
        except Exception as e:
            print(f"Error fetching stats: {e}")
            return {"handled": 0, "resolved": 0}

        # THE FIX: Added 'rfid_code' to the arguments!

    def update_user_account(self, user_id, first_name, last_name, employee_id, password, role, status, rfid_code,
                            suspend_val=0, suspend_type="Hours"):
        """Updates user details (including RFID) and calculates future suspension dates"""
        try:
            from datetime import datetime, timedelta
            conn = self.get_connection()
            cursor = conn.cursor()

            suspend_until = None

            if status == "Suspended":
                if suspend_type == "Hours":
                    suspend_until = datetime.now() + timedelta(hours=int(suspend_val))
                else:
                    suspend_until = datetime.now() + timedelta(days=int(suspend_val))

            # THE FIX: Changed 'username' to 'employee_id' to perfectly match your database!
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
            print(f"Error updating user: {e}")
            return False

    def get_my_pending_cases(self, officer_name, role):
        """Fetches pending cases. Staff only see their own. Kapitan sees all."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor(dictionary=True)

            if role.lower() in ['kapitan', 'admin']:
                # Kapitan God Mode: Sees ALL pending cases to override if needed
                query = "SELECT * FROM incidents WHERE status != 'Resolved' ORDER BY created_at DESC"
                cursor.execute(query)
            else:
                # Normal Staff: Only sees cases they personally processed
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
            return user  # Returns the questions, or None if user doesn't exist
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
                # We use .lower() and .strip() so it doesn't fail if they accidentally capitalized a letter!
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
