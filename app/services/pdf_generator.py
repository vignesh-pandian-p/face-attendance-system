from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Attendance Report', 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def generate_class_report_pdf(class_, students, attendance_logs):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Class Report: {class_.department} - {class_.year} Year {class_.section} Section', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Advisor: {class_.advisor}', 0, 1)
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Student Name', 1)
    pdf.cell(40, 10, 'Date', 1)
    pdf.cell(40, 10, 'Time', 1)
    pdf.ln()

    pdf.set_font('Arial', '', 12)
    for log in attendance_logs:
        pdf.cell(40, 10, log.user.name, 1)
        pdf.cell(40, 10, log.timestamp.strftime('%Y-%m-%d'), 1)
        pdf.cell(40, 10, log.timestamp.strftime('%H:%M:%S'), 1)
        pdf.ln()

    return pdf.output(dest='S').encode('latin-1')

def generate_monthly_student_report_pdf(student, attendance_logs, month, year):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Monthly Student Report: {student.name}', 0, 1, 'C')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'Month: {month}/{year}', 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Date', 1)
    pdf.cell(40, 10, 'Time', 1)
    pdf.ln()

    pdf.set_font('Arial', '', 12)
    for log in attendance_logs:
        pdf.cell(40, 10, log.timestamp.strftime('%Y-%m-%d'), 1)
        pdf.cell(40, 10, log.timestamp.strftime('%H:%M:%S'), 1)
        pdf.ln()

    return pdf.output(dest='S').encode('latin-1')

def generate_yearly_student_report_pdf(student, attendance_logs, year):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Yearly Student Report: {student.name}', 0, 1, 'C')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'Year: {year}', 0, 1, 'C')
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Date', 1)
    pdf.cell(40, 10, 'Time', 1)
    pdf.ln()

    pdf.set_font('Arial', '', 12)
    for log in attendance_logs:
        pdf.cell(40, 10, log.timestamp.strftime('%Y-%m-%d'), 1)
        pdf.cell(40, 10, log.timestamp.strftime('%H:%M:%S'), 1)
        pdf.ln()

    return pdf.output(dest='S').encode('latin-1')

def generate_monthly_class_report_pdf(class_, students, attendance_logs, month, year):
    pdf = PDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f'Monthly Class Report: {class_.department} - {class_.year} Year {class_.section} Section', 0, 1, 'C')
    pdf.ln(5)
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, f'Month: {month}/{year}', 0, 1, 'C')
    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Advisor: {class_.advisor}', 0, 1)
    pdf.ln(10)

    pdf.set_font('Arial', 'B', 12)
    pdf.cell(40, 10, 'Student Name', 1)
    pdf.cell(40, 10, 'Date', 1)
    pdf.cell(40, 10, 'Time', 1)
    pdf.ln()

    pdf.set_font('Arial', '', 12)
    for log in attendance_logs:
        pdf.cell(40, 10, log.user.name, 1)
        pdf.cell(40, 10, log.timestamp.strftime('%Y-%m-%d'), 1)
        pdf.cell(40, 10, log.timestamp.strftime('%H:%M:%S'), 1)
        pdf.ln()

    return pdf.output(dest='S').encode('latin-1')
