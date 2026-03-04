import nltk
import unicodedata
import re
from ebooklib import epub
from bs4 import BeautifulSoup
from langdetect import detect
from UtilDebug import write_string_list_in_txt, write_string_in_txt



LANG_MAP = {
    # Westeuropa
    'en': 'english',
    'de': 'german',
    'fr': 'french',
    'es': 'spanish',
    'pt': 'portuguese',
    'it': 'italian',
    'nl': 'dutch',
    'da': 'danish',
    'no': 'norwegian',
    'sv': 'swedish',
    'fi': 'finnish',

    # Osteuropa & Balkan
    'pl': 'polish',
    'cs': 'czech',
    'sk': 'slovene',       # NLTK hat nur 'slovene', kein 'slovak'
    'sl': 'slovene',
    'hu': 'hungarian',
    'ru': 'russian',
    'uk': 'russian',       # kein eigenes Modell
    'bg': 'russian',       # fallback
    'sr': 'slovene',       # fallback für Serbisch
    'hr': 'slovene',       # fallback für Kroatisch

    # Südeuropa
    'el': 'greek',
    'tr': 'turkish',

    # Skandinavien
    'is': 'danish',        # fallback für Isländisch

    # Mitteleuropa
    'ro': 'italian',       # fallback für Rumänisch

    # Nahost / Zentralasien
    'fa': 'english',       # kein Modell
    'ar': 'english',       # kein Modell
    'he': 'english',

    # Asien
    'zh-cn': 'english',    # kein Punkt-Modell für CJK
    'zh-tw': 'english',
    'ja': 'english',
    'ko': 'english',
    'hi': 'english',
    'th': 'english',
    'vi': 'english',

    # Afrika
    'af': 'dutch',         # Afrikaans → ähnlich
    'sw': 'english',       # Swahili → kein Modell

    # Andere / fallback
    'et': 'finnish',       # Estnisch ähnlich
    'lv': 'finnish',       # Lettisch ähnlich
    'lt': 'polish',        # Litauisch ähnlich
    'ga': 'english',       # Irisch
    'cy': 'english',       # Walisisch
    'mt': 'italian',       # Maltesisch
    'id': 'english',       # Indonesisch
    'ms': 'english',       # Malaiisch
    'tl': 'english',       # Tagalog
    'ur': 'english',
    'bn': 'english',
}


def read_and_format_text_files_to_list(settings):

    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("begin loading nltk")
        nltk.download('punkt')
        print("nltk loaded")

    fremd_heim = []
    durchlauf = 0
    for file_path in [settings.foreign_filename,settings.home_filename]:
        durchlauf += 1
        sentence_list = []
        if file_path.endswith(".epub"):
            book = epub.read_epub(file_path)
            html_item_list = []

            for item in book.get_items():
                # Prüfen, ob es sich um eine .xhtml- oder .html-Datei handelt
                if item.get_name().endswith(('.xhtml', '.html')):
                    # HTML-Inhalt des Kapitels extrahieren
                    soup = BeautifulSoup(item.get_content(), 'html.parser')
                    #text_from_html = soup.get_text(separator="\n\n")
                    text_from_html = soup.get_text()


                    separated_at_newlines = re.split(r'\n\s*\n', text_from_html.strip())

                    separated_at_newlines = [
                        re.sub(r'\s+', ' ', absatz).strip() + " "
                        for absatz in separated_at_newlines
                    ]

                    #separated_at_newlines = text_from_html.strip().split("\n\n")
                    html_item_list.extend(separated_at_newlines)

            if settings.input_use_debug_txt:
                if durchlauf == 1:
                    write_string_list_in_txt(html_item_list, "txt foreign lang 1 html read.txt")
                if durchlauf == 2:
                    write_string_list_in_txt(html_item_list, "txt home lang 1 html read.txt")

            lang_text = "".join(html_item_list)
            lang = detect(lang_text)
            nltk_lang = LANG_MAP.get(lang, 'english')
            for item in html_item_list:
                if len(item) > 0:
                    sentences = nltk.sent_tokenize(item, language=nltk_lang)
                    sentence_list.extend(sentences)


        elif file_path.endswith(".txt"):
            with open("dateiname.txt", "r", encoding="utf-8") as f:
                lang_text = f.read()

            txt_abschnitte = re.split(r'\n\s*\n', lang_text)
            lang = detect(lang_text)
            nltk_lang = LANG_MAP.get(lang, 'english')

            sentences = []
            for abschnitt in txt_abschnitte:
                sentences = nltk.sent_tokenize(abschnitt, language=nltk_lang)
            sentence_list.extend(sentences)

        if settings.input_use_debug_txt:
            if durchlauf == 1:
                write_string_in_txt(lang_text, "txt foreign lang 2 read.txt")
                write_string_list_in_txt(sentence_list, "txt foreign lang 3 separated.txt")
            if durchlauf == 2:
                write_string_in_txt(lang_text, "txt home lang 2 read.txt")
                write_string_list_in_txt(sentence_list, "txt home lang 3 separated.txt")


        sentence_list = [s + " " for s in sentence_list]
        fremd_heim.append(sentence_list)

    return fremd_heim[0], fremd_heim[1]







# take long blocks of sentences and cut them down to max_length while keeping the matching
# necessary for displaying as pdf
def crop_long_blocks(dic_foreign, dic_home, max_length):
    dic_f = []
    dic_h = []
    for block_index in range(len(dic_foreign)):
        words_foreign= dic_foreign[block_index].split()
        sep_blocks_foreign = [' '.join(words_foreign[i:i + max_length]) for i in range(0, len(words_foreign), max_length)]
        words_home = dic_home[block_index].split()
        sep_blocks_home = [' '.join(words_home[i:i + max_length]) for i in range(0, len(words_home), max_length)]

        # Adjust the number of blocks, so they are the same
        difference_in_numbers_of_blocks = len(sep_blocks_foreign) - len(sep_blocks_home)
        if difference_in_numbers_of_blocks > 0:
            # foreign longer
            sep_blocks_home.extend([" "] * difference_in_numbers_of_blocks)
        elif difference_in_numbers_of_blocks < 0:
            # home longer
            sep_blocks_foreign.extend([" "] * (-difference_in_numbers_of_blocks))
        dic_f.extend(sep_blocks_foreign)
        dic_h.extend(sep_blocks_home)

    return dic_f, dic_h


def build_dictionaries_new_path_boxes_system(input_fr, input_de, x, y, input_use_shortened_blocks):
    print("start building dics")
    result_fr = []
    result_de = []

    x_prev = 0
    y_prev = 0
    x_box_start = 0
    y_box_start = 0
    x_cur = 0
    y_cur = 0
    index_prev = 0
    for i, _ in enumerate(x):
        x_cur = x[i]
        y_cur = y[i]
        if x_cur != x_prev and y_cur != y_prev:  # Box Ende


            append_sentences(True, x_cur, y_cur, x_box_start, y_box_start, input_fr, input_de, result_fr, result_de)

            x_box_start = x_cur  # starte neue box
            y_box_start = y_cur

        x_prev = x_cur
        y_prev = y_cur
        index_prev = i

    if x_box_start < len(input_fr) - 1:
        append_sentences(input_use_shortened_blocks, len(input_fr)-1, len(input_de)-1, x_box_start, y_box_start, input_fr, input_de, result_fr,result_de)

    print("finished building dics")
    return result_fr, result_de

def append_sentences(jump_big_boxes, x_cur,y_cur,x_box_start,y_box_start,input_fr,input_de,result_fr,result_de):
    satz_foreign = []
    satz_home = []
    for j in range(x_box_start, x_cur ):
        if jump_big_boxes and x_cur - x_box_start > 15 and x_box_start + 5 < j < x_cur -2:
            if j == x_box_start + 5:
                satz_foreign.append("<br/>...<br/>...<br/>" + str(x_cur - x_box_start - 6) + " sentences<br/>...<br/>...<br/>")
            continue
        satz_foreign.append(input_fr[j])
    for j in range(y_box_start, y_cur):
        if jump_big_boxes and y_cur - y_box_start > 15 and y_box_start + 5 < j < y_cur -2:
            if j == y_box_start + 5:
                satz_home.append("<br/>...<br/>...<br/>" + str(y_cur - y_box_start - 6) + " sentences<br/>...<br/>...<br/>")
            continue
        satz_home.append(input_de[j])

    result_fr.append("".join(satz_foreign))
    result_de.append("".join(satz_home))