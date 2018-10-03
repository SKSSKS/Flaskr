from fpdf import FPDF

body = "Hello suraj\nHow are yoouaksdjaosli asodlilkawdjalwkd aosid oiasdc kadshdcn"
pdf = FPDF()
pdf.add_page()
pdf.set_xy(0, 0)
pdf.set_font('arial', 'B', 20.0)
pdf.cell(0, 10, txt='Helloboy', ln=1, align="C")
pdf.set_font('arial', 'B', 13.0)
line = ''
for text in body:
    if text == '\n':
        pdf.cell(0, 10, txt=line, ln=1, align="L")
        line = ''
    else:
        line += text
if len(line) != 0:
    pdf.cell(0, 10, txt=line, ln=1, align="L")
pdf.output('hellboy.pdf', 'F')
