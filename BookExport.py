from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import Table, TableStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Frame, PageTemplate, FrameBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT,TA_RIGHT
from reportlab.lib import colors
from textwrap import wrap

from ebooklib import epub
from itertools import zip_longest
import html

from Datenbearbeitung import PathResults


def export_pdf_horiz_preferred(pdf_filename, dic_fremd, dic_heim):
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

def create_epub(epub_filename, liste_links,liste_rechts):
    html_content = """
    <html>
    <head>
    <style>
    p {
        margin: 1em 0;
        font-size: 1.2em;
    }
    .left {
        text-align: left;
    }
    .right {
        text-align: right;
    }
    </style>
    </head>
    <body>
    """

    for links, rechts in zip_longest(liste_links, liste_rechts):
        if links:
            html_content += f'<p class="left">{links}</p>\n'
        if rechts:
            html_content += f'<p class="right">{rechts}</p>\n'

    html_content += "</body></html>"

    book = epub.EpubBook()

    book.set_identifier("id123")
    book.set_title("Abwechselnde Texte")
    book.set_language("de")

    chapter = epub.EpubHtml(
        title="Kapitel 1",
        file_name="chap_1.xhtml",
        lang="de"
    )

    chapter.content = html_content

    book.add_item(chapter)
    book.toc = (chapter,)
    book.spine = ["nav", chapter]

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(epub_filename, book)

def create_epub_2(epub_filename, liste_links,liste_rechts):
    html_content = """
    <html>
    <head>
    <style>
    body {
        font-size: 1.2em;
    }

    .row {
        display: flex;
        width: 100%;
        margin: 0.5em 0;
    }

    .left {
        justify-content: flex-start;
    }

    .right {
        justify-content: flex-end;
    }

    .text {
        max-width: 70%;
    }
    </style>
    </head>
    <body>
    """

    for links, rechts in zip_longest(liste_links, liste_rechts):
        if links:
            html_content += f'<p class="left">{links}</p>\n'
        if rechts:
            html_content += f'<p class="right">{rechts}</p>\n'

    html_content += "</body></html>"

    book = epub.EpubBook()

    book.set_identifier("id123")
    book.set_title("Abwechselnde Texte")
    book.set_language("de")

    chapter = epub.EpubHtml(
        title="Kapitel 1",
        file_name="chap_1.xhtml",
        lang="de"
    )

    chapter.content = html_content

    book.add_item(chapter)
    book.toc = (chapter,)
    book.spine = ["nav", chapter]

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    epub.write_epub(epub_filename, book)

def create_bilingual_epub(
    original,
    translation,
    output_file="bilingual.epub",
    title="Bilinguales Buch",
    author="Autor",
    lang_src="fr",
    lang_tgt="de"
):
    # ----------------------
    # Buch
    # ----------------------
    book = epub.EpubBook()

    book.set_identifier("bilingual-book")
    book.set_title(title)
    book.set_language(lang_tgt)
    book.add_author(author)

    # ----------------------
    # PROFESSIONELLES CSS
    # ----------------------
    style = """
        body {
            line-height: 1.5;
            font-family: serif;
        }

        .pair {
            margin: 1.2em 0;
        }

        /* FREMDSPRACHE */
        .src {
            margin: 0 0 0.3em 1.8em;   /* Einrückung */
            font-family: "Georgia", serif;
            font-size: 1.08em;         /* etwas größer */
            font-style: italic;
        }

        /* ÜBERSETZUNG */
        .tgt {
            margin: 0;
            font-family: serif;
            font-size: 1em;
        }
        """

    css_item = epub.EpubItem(
        uid="style",
        file_name="style/book.css",
        media_type="text/css",
        content=style
    )

    book.add_item(css_item)

    # ----------------------
    # Kapitelinhalt
    # ----------------------
    content = f"<h1>{html.escape(title)}</h1>\n"

    for i, (src, tgt) in enumerate(zip_longest(original, translation)):
        src = html.escape(src or "")
        tgt = html.escape(tgt or "")

        content += f"""
            <div class="pair" id="p{i}">
                <p class="src" lang="{lang_src}">
                    {src}
                </p>
                <p class="tgt" lang="{lang_tgt}">
                    {tgt}
                </p>
            </div>
            """

    chapter = epub.EpubHtml(
        title="Text",
        file_name="text/chapter01.xhtml",
        lang=lang_tgt
    )

    chapter.content = content
    chapter.add_item(css_item)

    book.add_item(chapter)

    # ----------------------
    # Navigation
    # ----------------------
    book.toc = (chapter,)
    book.spine = ["nav", chapter]

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # ----------------------
    # Schreiben
    # ----------------------
    epub.write_epub(output_file, book)

    print(f"EPUB erstellt: {output_file}")

def create_bilingual_epub_2(
    original,
    translation,
    output_file="bilingual.epub",
    title="Bilinguales Buch",
    author="Autor",
    lang_src="fr",
    lang_tgt="de"
):
    ## ----------------------
    # Buch
    # ----------------------
    book = epub.EpubBook()

    book.set_identifier("bilingual-book")
    book.set_title(title)
    book.set_language(lang_tgt)
    book.add_author(author)

    # ----------------------
    # ROBUSTES EPUB CSS
    # ----------------------
    style = """
    body {
        line-height: 1.5;
        font-family: serif;
    }

    .pair {
        margin-top: 1em;
        margin-bottom: 1em;
    }

    /* Container für Fremdsprache */
    .src-block {
        padding-left: 2em;        /* Einrückung */
        font-family: Georgia, serif; /* andere Schrift für Original */
        font-size: 1.15em;        /* größere Schrift */
        font-style: italic;       /* kursiv */
    }

    /* Übersetzung */
    .tgt {
        padding-left: 1em;        /* leichte Einrückung */
        font-family: serif;
        font-size: 1em;
        font-style: normal;
    }
    """

    css = epub.EpubItem(
        uid="style",
        file_name="style/book.css",
        media_type="text/css",
        content=style
    )

    book.add_item(css)

    # ----------------------
    # Inhalt erzeugen
    # ----------------------
    content = f"<h1>{html.escape(title)}</h1>"

    for i, (src, tgt) in enumerate(zip_longest(original, translation)):

        src = html.escape(src or "")
        tgt = html.escape(tgt or "")

        # Verwendung von Block-DIVs für zuverlässige Einrückung
        content += f"""
        <div class="pair" id="p{i}">
            <div class="src-block" lang="{lang_src}">
                {src}
            </div>
            <div class="tgt" lang="{lang_tgt}">
                {tgt}
            </div>
        </div>
        """

    chapter = epub.EpubHtml(
        title="Text",
        file_name="text/chapter01.xhtml",
        lang=lang_tgt
    )

    # Inline-Referenz auf CSS
    chapter.add_item(css)
    chapter.content = content

    book.add_item(chapter)

    # ----------------------
    # Navigation
    # ----------------------
    book.toc = (chapter,)
    book.spine = ["nav", chapter]

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # ----------------------
    # EPUB schreiben
    # ----------------------
    epub.write_epub(output_file, book)

    print("EPUB erstellt:", output_file)



def save_book_versions(filename, nth_run, result: PathResults, dic_foreign, dic_home, ):
    this_name = filename + " " + str(nth_run) + " " + result.name
    export_pdf_vertical(this_name + " vertical.pdf", dic_foreign, dic_home)
    export_pdf_horizontal(this_name + " horizontal_outbound.pdf", dic_foreign, dic_home)
    export_pdf_horizontal_foreign_right(this_name + " horizontal_inbound, foreign right.pdf", dic_foreign, dic_home)
    export_pdf_horiz_preferred(this_name + " horizontal_preference.pdf", dic_foreign, dic_home)
    create_epub(this_name + " book1.epub", dic_foreign, dic_home)
    create_epub_2(this_name + " book2.epub", dic_foreign, dic_home)
    #create_bilingual_epub(dic_foreign, dic_home, this_name + " 1.epub")
    create_bilingual_epub_2(dic_foreign, dic_home, this_name + " 2.epub")
    print("pdf done")



