from fpdf import FPDF
from pylab import title


class ExportPDF:

    def __init__(self, parent):
        self.parent = parent
        self.pdf = FPDF(orientation='P', unit='mm', format='A4')

    def generar_reporte(self):
        self.nuevo_pdf()
        self.pdf.cell(200, 10, "PDF TEST")
        return self.pdf.output("pdf_export.pdf")

    def nuevo_pdf(self):
        self.pdf.add_page()
        self.pdf.set_font("Arial", size=12)
        pass
