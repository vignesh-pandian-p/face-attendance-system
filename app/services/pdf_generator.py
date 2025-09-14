from fpdf import FPDF

class PDF(FPDF):
    def __init__(self, college_name, class_obj):
        super().__init__()
        self.college_name = college_name
        self.class_obj = class_obj

    def header(self):
        self.set_font('Helvetica', 'B', 18)
        self.cell(0, 10, self.college_name, 0, 1, 'C')
        self.ln(5)
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 10, 'Attendance Report', 0, 1, 'C')
        self.set_font('Helvetica', '', 12)
        self.cell(0, 10, f'Department of {self.class_obj.department}', 0, 1, 'C')
        self.cell(0, 10, f'Class: {self.class_obj.year} - Section {self.class_obj.section}', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def fancy_table(self, header, data):
        self.set_font('Helvetica', 'B', 12)
        self.set_fill_color(200, 220, 255)
        self.cell(90, 7, header[0], 1, 0, 'C', 1)
        self.cell(90, 7, header[1], 1, 0, 'C', 1)
        self.ln()
        self.set_font('Helvetica', '', 12)
        self.set_fill_color(240, 240, 240)
        fill = False
        for row in data:
            self.cell(90, 6, str(row[0]), 'LR', 0, 'L', fill)
            self.cell(90, 6, str(row[1]), 'LR', 0, 'L', fill)
            self.ln()
            fill = not fill
        self.cell(180, 0, '', 'T')

def generate_attendance_pdf(college_name, class_obj, logs):
    pdf = PDF(college_name, class_obj)
    pdf.add_page()

    header = ['Student Name', 'Timestamp']
    data = []
    if logs:
        for log in logs:
            data.append([log.user.name, log.timestamp.strftime('%Y-%m-%d %H:%M:%S')])

    if not data:
        pdf.set_font('Helvetica', 'I', 12)
        pdf.cell(0, 10, 'No attendance records found for this class.', 0, 1, 'C')
    else:
        pdf.fancy_table(header, data)

    return pdf.output(dest='S')
