import re
import tempfile
from datetime import datetime

from fpdf import FPDF


class OSINTReport(FPDF):
    """Custom PDF class for OSINT reports."""

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(0, 102, 204)
        self.cell(0, 10, "CALL OSINT REPORT", ln=True, align="C")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(
            0,
            5,
            f"Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            ln=True,
            align="C",
        )
        self.line(10, self.get_y() + 2, 200, self.get_y() + 2)
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def _strip_html(text: str) -> str:
    """Remove HTML tags from text."""
    clean = re.sub(r"<[^>]+>", "", text)
    clean = clean.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    return clean


def generate_pdf(title: str, content: str) -> str:
    """Generate a PDF report and return the file path."""
    pdf = OSINTReport()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Title
    clean_title = _strip_html(title)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, clean_title, ln=True)
    pdf.ln(3)

    # Content
    clean_content = _strip_html(content)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(33, 33, 33)

    for line in clean_content.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(2)
            continue

        # Section separators
        if line.startswith("━") or line.startswith("─"):
            y = pdf.get_y()
            pdf.set_draw_color(0, 102, 204)
            pdf.line(10, y, 200, y)
            pdf.ln(3)
            continue

        # Bold headers (lines with emojis at start that look like headers)
        if ":" in line and len(line.split(":")[0]) < 40:
            parts = line.split(":", 1)
            pdf.set_font("Helvetica", "B", 10)
            pdf.set_text_color(0, 51, 102)
            key_text = parts[0] + ":"
            pdf.cell(pdf.get_string_width(key_text) + 2, 6, key_text)
            if len(parts) > 1:
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(33, 33, 33)
                pdf.cell(0, 6, parts[1].strip(), ln=True)
            else:
                pdf.ln(6)
        else:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(33, 33, 33)
            pdf.multi_cell(0, 6, line)

    # Save to temp file
    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=".pdf", prefix="osint_report_"
    )
    pdf.output(tmp.name)
    return tmp.name
