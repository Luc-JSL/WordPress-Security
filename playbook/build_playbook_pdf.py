"""Render PLAYBOOK.md (simple markdown subset) to a styled PDF."""
import re
import sys
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                                HRFlowable, Flowable)


class CheckBox(Flowable):
    """An empty square to tick by hand."""
    def __init__(self, size=8.5):
        super().__init__()
        self.size = size
        self.width = self.height = size

    def draw(self):
        self.canv.setStrokeColor(colors.HexColor("#1F3A5F"))
        self.canv.setLineWidth(0.9)
        self.canv.rect(0, 0, self.size, self.size, stroke=1, fill=0)

src, out = sys.argv[1], sys.argv[2]  # usage: python3 build_playbook_pdf.py PLAYBOOK.md Secure_WP_Care_Playbook.pdf
ACCENT = colors.HexColor("#1F3A5F")
SOFT = colors.HexColor("#F2F6FC")
USABLE = 7.3 * inch - 12  # frame width minus its 6pt padding on each side
LINE = colors.HexColor("#D0D5DD")

title = ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=20, leading=24, textColor=ACCENT, spaceAfter=6)
h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=13.5, leading=17, textColor=ACCENT,
                    spaceBefore=12, spaceAfter=4, keepWithNext=1)
body = ParagraphStyle("b", fontName="Helvetica", fontSize=10, leading=14, spaceAfter=4)
item = ParagraphStyle("i", parent=body, leftIndent=18, firstLineIndent=-12, spaceAfter=3)
quote = ParagraphStyle("q", parent=body, fontSize=9.6, leading=13.5, spaceAfter=3)
cell = ParagraphStyle("c", parent=body, fontSize=9.3, leading=12.5, spaceAfter=0)
cell_h = ParagraphStyle("ch", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)

DOT = '<font size="9">•</font>&nbsp;&nbsp;'


def inline(text):
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r'<font name="Courier" size="9">\1</font>', text)
    return text


def table(rows):
    data = [[Paragraph(inline(c), cell_h if r == 0 else cell) for c in row] for r, row in enumerate(rows)]
    widths = [w * USABLE / (7.3 * inch) for w in (1.65 * inch, 1.55 * inch, 4.1 * inch)][:len(rows[0])]
    t = Table(data, colWidths=widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, SOFT]),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6), ("RIGHTPADDING", (0, 0), (-1, -1), 6)]))
    return t


def quote_box(paragraphs):
    flow = [Paragraph(inline(p), quote) for p in paragraphs]
    t = Table([[flow]], colWidths=[USABLE])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT),
        ("LINEBEFORE", (0, 0), (0, -1), 3, ACCENT),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 10)]))
    return t


lines = open(src, encoding="utf-8").read().splitlines()
story, i = [], 0
while i < len(lines):
    line = lines[i]
    if line.startswith("# "):
        story.append(Paragraph(inline(line[2:]), title))
    elif line.startswith("## "):
        story.append(Paragraph(inline(line[3:]), h2))
    elif line.strip() == "---":
        story.append(HRFlowable(width="100%", thickness=0.6, color=LINE, spaceBefore=6, spaceAfter=6))
    elif line.startswith("|"):
        rows = []
        while i < len(lines) and lines[i].startswith("|"):
            cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
            if not all(re.fullmatch(r":?-{3,}:?", c) for c in cells):
                rows.append(cells)
            i += 1
        story += [table(rows), Spacer(1, 6)]
        continue
    elif line.startswith(">"):
        paras, cur = [], []
        while i < len(lines) and lines[i].startswith(">"):
            text = lines[i][1:].strip()
            if text:
                cur.append(text)
            elif cur:
                paras.append(" ".join(cur)); cur = []
            i += 1
        if cur:
            paras.append(" ".join(cur))
        story += [quote_box(paras), Spacer(1, 6)]
        continue
    elif re.match(r"\s*- ", line) or re.match(r"\d+\. ", line):
        text = line.strip()
        while i + 1 < len(lines) and lines[i + 1].startswith("      "):
            i += 1
            text += " " + lines[i].strip()
        if text.startswith("- [ ] "):
            row = Table([[CheckBox(), Paragraph(inline(text[6:]), body)]], colWidths=[0.26 * inch, USABLE - 0.26 * inch])
            row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                     ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                     ("TOPPADDING", (0, 0), (0, 0), 3), ("TOPPADDING", (1, 0), (1, 0), 0),
                                     ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
            story.append(row)
            i += 1
            continue
        elif text.startswith("- "):
            marker, text = DOT, text[2:]
        else:
            num, text = text.split(". ", 1)
            marker = f"<b>{num}.</b>&nbsp;&nbsp;"
        story.append(Paragraph(marker + inline(text), item))
    elif line.strip():
        text = line.strip()
        while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"(#|\||>|-|\d+\. |---)", lines[i + 1].strip()):
            i += 1
            text += " " + lines[i].strip()
        story.append(Paragraph(inline(text), body))
    i += 1


def footer(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(0.6 * inch, 0.45 * inch, "Secure WP Care • 30-Day Launch Playbook")
    canvas.drawRightString(letter[0] - 0.6 * inch, 0.45 * inch, f"Page {doc.page}")
    canvas.restoreState()


doc = SimpleDocTemplate(out, pagesize=letter, leftMargin=0.6 * inch, rightMargin=0.6 * inch,
                        topMargin=0.6 * inch, bottomMargin=0.7 * inch,
                        title="Secure WP Care - 30-Day Launch Playbook", author="Jordan Sledge")
doc.build(story, onFirstPage=footer, onLaterPages=footer)
