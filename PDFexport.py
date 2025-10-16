from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, PageTemplate, FrameBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_RIGHT
from reportlab.lib import colors
from textwrap import wrap

def export_best_style(pdf_filename, dic_fremd, dic_heim):
    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=landscape(A4),
        leftMargin=60,
        rightMargin=60,
        topMargin=20,
        bottomMargin=20
    )

    styles = getSampleStyleSheet()

    fr_style = ParagraphStyle(
        'Französisch',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        leftIndent=10,
        rightIndent=10,
        spaceAfter=0
    )

    de_style = ParagraphStyle(
        'Deutsch',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_LEFT,
        leftIndent=10,
        rightIndent=10,
        italic=True,
        textColor=colors.darkblue
    )

    def split_into_chunks(text, max_chars=2000):
        """
        Teilt Text in Abschnitte von max_chars Zeichen (nach Wortgrenzen, wenn möglich)
        """
        return wrap(text, width=max_chars, break_long_words=False, replace_whitespace=False)

    def align_and_split_texts(fr_text, de_text, max_chars=2000):
        """
        Teilt beide Texte in gleich viele Abschnitte.
        """
        fr_chunks = split_into_chunks(fr_text, max_chars)
        de_chunks = split_into_chunks(de_text, max_chars)
        n = max(len(fr_chunks), len(de_chunks))

        # auffüllen, falls unterschiedlich viele Abschnitte
        while len(fr_chunks) < n:
            fr_chunks.append("")
        while len(de_chunks) < n:
            de_chunks.append("")

        return list(zip(fr_chunks, de_chunks))

    story = []

    for fr, de in zip(dic_fremd, dic_heim):
        pairs = align_and_split_texts(fr, de, max_chars=2000)
        for fr_part, de_part in pairs:
            fr_para = Paragraph(fr_part, fr_style)
            de_para = Paragraph(de_part, de_style)

            pair_table = Table([[de_para, fr_para]], colWidths=[doc.width / 2, doc.width / 2])
            pair_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 5),
                ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ]))

            story.append(pair_table)
            story.append(Spacer(1, 6))

    doc.build(story)
    print(f"✅ PDF erstellt: {pdf_filename}")




def export_pdf_vertical(pdf_filename, dic_fremd, dic_heim):
    doc = SimpleDocTemplate(pdf_filename, pagesize=A4)
    # Styles vorbereiten
    styles = getSampleStyleSheet()

    fr_style = ParagraphStyle(
        'Französisch',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        spaceAfter=1,
        leftIndent=40,   # etwas eingerückt, damit nicht ganz links
        rightIndent=80   # nicht bis ganz rechts
    )

    de_style = ParagraphStyle(
        'Deutsch',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
        spaceAfter=1,
        leftIndent=80,   # nicht ganz links
        rightIndent=40,  # eingerückt von rechts
        italic=True
    )

    # Inhalte zusammenbauen
    story = []
    for fr, de in zip(dic_fremd, dic_heim):
        story.append(Paragraph(fr, fr_style))
        story.append(Paragraph(de, de_style))
        story.append(Spacer(1, 1))  # zusätzlicher Abstand zwischen Paaren

    # PDF schreiben
    doc.build(story)
    print(f"PDF erstellt: {pdf_filename}")


def export_pdf_horizontal(pdf_filename, dic_fremd, dic_heim):
    # PDF erstellen (A4 quer)
    doc = doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=landscape(A4),
        leftMargin=60,   # linker Rand
        rightMargin=60,  # rechter Rand
        topMargin=10,    # oberer Rand
        bottomMargin=10  # unterer Rand
    )

    # Styles vorbereiten
    styles = getSampleStyleSheet()

    fr_style = ParagraphStyle(
        'Französisch',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        leftIndent=20,
        rightIndent=20,
        spaceAfter=0
    )

    de_style = ParagraphStyle(
        'Deutsch',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
        leftIndent=20,
        rightIndent=20,
        italic=True,
        textColor=colors.darkblue
    )

    # Inhalte zusammenbauen
    story = []

    data = []
    for fr, de in zip(dic_fremd, dic_heim):
        fr_para = Paragraph(fr, fr_style)
        de_para = Paragraph(de, de_style)
        data.append([fr_para, de_para])

    # Tabelle mit zwei Spalten (links FR, rechts DE)
    table = Table(data, colWidths=[doc.width/1.9, doc.width/1.9])

    # Tabellenstil anpassen
    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),   # Texte oben ausrichten
        ('LEFTPADDING', (0,0), (-1,-1), -15),
        ('RIGHTPADDING', (0,0), (-1,-1), -15),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        # optionale Linien zur Orientierung:
        # ('GRID', (0,0), (-1,-1), 0.25, colors.grey)
    ]))

    story.append(table)

    # PDF schreiben
    doc.build(story)
    print(f"PDF erstellt: {pdf_filename}")

def export_pdf_horizontal_foreign_right(pdf_filename, dic_fremd, dic_heim):
    # PDF erstellen (A4 quer)
    doc = doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=landscape(A4),
        leftMargin=60,   # linker Rand
        rightMargin=60,  # rechter Rand
        topMargin=10,    # oberer Rand
        bottomMargin=10  # unterer Rand
    )

    # Styles vorbereiten
    styles = getSampleStyleSheet()

    fr_style = ParagraphStyle(
        'Französisch',
        parent=styles['Normal'],
        fontSize=12,
        alignment=TA_LEFT,
        leftIndent=20,
        rightIndent=20,
        spaceAfter=0
    )

    de_style = ParagraphStyle(
        'Deutsch',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_RIGHT,
        leftIndent=20,
        rightIndent=20,
        italic=True,
        textColor=colors.darkblue
    )

    # Inhalte zusammenbauen
    story = []

    data = []
    for fr, de in zip(dic_fremd, dic_heim):
        fr_para = Paragraph(fr, fr_style)
        de_para = Paragraph(de, de_style)
        data.append([de_para,fr_para])

    # Tabelle mit zwei Spalten (links FR, rechts DE)
    table = Table(data, colWidths=[doc.width/1.9, doc.width/1.9])

    # Tabellenstil anpassen
    table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),   # Texte oben ausrichten
        ('LEFTPADDING', (0,0), (-1,-1), -15),
        ('RIGHTPADDING', (0,0), (-1,-1), -15),
        ('TOPPADDING', (0,0), (-1,-1), 2),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        # optionale Linien zur Orientierung:
        # ('GRID', (0,0), (-1,-1), 0.25, colors.grey)
    ]))

    story.append(table)

    # PDF schreiben
    doc.build(story)
    print(f"PDF erstellt: {pdf_filename}")



