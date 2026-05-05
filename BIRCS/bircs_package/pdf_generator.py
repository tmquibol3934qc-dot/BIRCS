import os
from datetime import datetime
from tkinter import messagebox


class PDFGenerator:
    @staticmethod
    def export_blotter(row_data):
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("Library Missing", "Kailangan mong i-install ang FPDF. (pip install fpdf)")
            return

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 8, txt="REPUBLIKA NG PILIPINAS", ln=True, align='C')
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 6, txt="Lungsod ng Caloocan", ln=True, align='C')
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 8, txt="BARANGAY 176-B BAGONG SILANG", ln=True, align='C')

        pdf.ln(5)
        pdf.set_font("Arial", 'B', 16)
        pdf.set_fill_color(220, 220, 220)
        pdf.cell(0, 10, txt="OFFICIAL BLOTTER REPORT", ln=True, align='C', fill=True)
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 11)
        pdf.cell(40, 8, txt="Case Number:", border=0)
        pdf.set_font("Arial", '', 11)
        pdf.cell(60, 8, txt=str(row_data.get('case_no', 'N/A')), border=0)

        pdf.set_font("Arial", 'B', 11)
        pdf.cell(40, 8, txt="Status:", border=0)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, txt=str(row_data.get('status', 'Pending')), border=0, ln=True)

        pdf.set_font("Arial", 'B', 11)
        pdf.cell(40, 8, txt="Category & Zone:", border=0)
        pdf.set_font("Arial", '', 11)
        pdf.cell(60, 8, txt=f"{row_data.get('category', 'Uncategorized')} (Zone {row_data.get('zone', 'N/A')})",
                 border=0)

        pdf.set_font("Arial", 'B', 11)
        pdf.cell(40, 8, txt="Date Recorded:", border=0)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 8, txt=str(row_data.get('exact_time', 'N/A')), border=0, ln=True)

        pdf.ln(2)
        pdf.cell(0, 0, "", "T")
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt="I. NARRATIVE OF INCIDENT", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.multi_cell(0, 6, txt=row_data.get('narrative') or "No narrative provided.")
        pdf.ln(5)

        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, txt="II. RESOLUTION & SETTLEMENT TERMS", ln=True)
        pdf.set_font("Arial", '', 11)

        settlement_text = row_data.get(
            'settlement_details') or "Case is currently ongoing or no settlement has been reached yet."
        if row_data.get('settlement_details_2'):
            settlement_text += f"\n\n[PHASE 2 UPDATE / RE-OPENED]:\n{row_data.get('settlement_details_2')}"
        pdf.multi_cell(0, 6, txt=settlement_text)
        pdf.ln(20)

        pdf.set_font("Arial", '', 11)
        pdf.cell(95, 8, txt="_____________________________", ln=0, align='C')
        pdf.cell(95, 8, txt="_____________________________", ln=1, align='C')
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(95, 6, txt=str(row_data.get('complainant_name', 'Complainant')).upper(), ln=0, align='C')
        pdf.cell(95, 6, txt=str(row_data.get('respondent_name', 'Respondent')).upper(), ln=1, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(95, 6, txt="Complainant (Plaintiff)", ln=0, align='C')
        pdf.cell(95, 6, txt="Respondent (Opposing Party)", ln=1, align='C')

        pdf.ln(15)
        pdf.set_font("Arial", '', 11)
        pdf.cell(95, 8, txt="_____________________________", ln=0, align='C')
        pdf.cell(95, 8, txt="_____________________________", ln=1, align='C')
        pdf.set_font("Arial", 'B', 11)
        pdf.cell(95, 6, txt=str(row_data.get('processed_by', 'Investigating Officer')).upper(), ln=0, align='C')
        pdf.cell(95, 6, txt="", ln=1, align='C')
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(95, 6, txt="Barangay Investigating Staff", ln=0, align='C')
        pdf.cell(95, 6, txt="Witness (Signature over Printed Name)", ln=1, align='C')

        safe_case_no = str(row_data.get('case_no', 'UNKNOWN')).replace("-", "_")
        filename = f"Blotter_Record_{safe_case_no}.pdf"
        try:
            pdf.output(filename)
            os.startfile(filename)
            messagebox.showinfo("Success", f"Official Blotter Report Generated!\nSaved as: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Hindi ma-save ang PDF. {e}")

    @staticmethod
    def export_analytics(data, timeframe):
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror("Library Missing", "Please install fpdf.")
            return

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", 'B', 18)
        pdf.cell(0, 10, txt="BARANGAY 176-B BAGONG SILANG", ln=True, align='C')
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, txt="Incident Analytics & Trends Report", ln=True, align='C')

        pdf.ln(5)
        pdf.set_font("Arial", 'I', 10)
        pdf.cell(0, 8, txt=f"Generated On: {datetime.now().strftime('%B %d, %Y - %I:%M %p')}", ln=True, align='C')
        pdf.cell(0, 8, txt=f"Data Filter Applied: {timeframe}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(220, 230, 241)
        pdf.cell(0, 10, txt="  EXECUTIVE SUMMARY", ln=True, fill=True)
        pdf.set_font("Arial", '', 12)
        pdf.ln(5)
        pdf.cell(100, 10, txt=f"Total Incidents Filed: {data['total']}", ln=False)
        pdf.cell(0, 10, txt=f"Resolved Cases: {data['resolved']}", ln=True)
        pdf.cell(100, 10, txt=f"Pending/Ongoing Cases: {data['pending']}", ln=True)
        pdf.ln(10)

        pdf.set_font("Arial", 'B', 12)
        pdf.set_fill_color(242, 220, 219)
        pdf.cell(0, 10, txt="  KEY TRENDS & PATTERNS", ln=True, fill=True)
        pdf.set_font("Arial", '', 12)
        pdf.ln(5)
        pdf.cell(0, 10, txt=f"Most Frequent Incident: {data['top_category']}", ln=True)
        pdf.cell(0, 10, txt=f"Incident Hotspot: {data['top_zone']}", ln=True)
        pdf.cell(0, 10, txt=f"Peak Hours: {data['peak_hours']}", ln=True)

        pdf.ln(30)
        pdf.set_font("Arial", 'I', 10)
        pdf.set_text_color(150, 150, 150)
        pdf.cell(0, 10, txt="System-generated analytics report from BICRS. No physical signature required.", ln=True,
                 align='C')

        filename = f"BICRS_Analytics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        try:
            pdf.output(filename)
            os.startfile(filename)
            messagebox.showinfo("Success", f"PDF Report Generated successfully!\nSaved as: {filename}")
        except Exception as e:
            messagebox.showerror("File Error", f"Hindi mai-save ang PDF.\nError: {e}")
