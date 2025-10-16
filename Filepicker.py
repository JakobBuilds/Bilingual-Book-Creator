import tkinter as tk
from tkinter import filedialog
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


def pick_epubs_and_output():
    result = {"my_lang": None, "other_lang": None, "output_folder": None}
    running = True
    cancelled = False

    debug_values = {
        "enabled": False,
        "thresholds": [0,0,0]
    }

    def choose_file(language):
        path = filedialog.askopenfilename(
            title=f"{language} – EPUB-Datei wählen",
            filetypes=[
                ("EPUB & TXT files", "*.epub *.txt"),
                ("EPUB files", "*.epub"),
                ("TXT files", "*.txt"),
                ("Alle Dateien", "*.*")
            ]
        )
        if not path:
            return
        if language == "My Language":
            result["my_lang"] = path
            lbl_my_lang.config(text=f"My Language EPUB:\n{path}")
        else:
            result["other_lang"] = path
            lbl_other_lang.config(text=f"Other Language EPUB:\n{path}")
        check_ready()

    def choose_output_folder():
        folder = filedialog.askdirectory(title="Ausgabeordner wählen")
        if not folder:
            return
        result["output_folder"] = folder
        lbl_output_folder.config(text=f"Output Folder:\n{folder}")
        check_ready()

    def check_ready():
        if all(result.values()):
            btn_continue.config(state="normal")
        else:
            btn_continue.config(state="disabled")

    def continue_action():
        """Schließt das Fenster mit Erfolg und speichert die Threshold-Werte."""
        nonlocal running, debug_values
        if debug_mode.get():
            debug_values["enabled"] = True
            debug_values["thresholds"] = [
                int(entry_thresh1.get()),
                int(entry_thresh2.get()),
                int(entry_thresh3.get())
            ]
        running = False
        root.quit()

    def cancel_action():
        nonlocal running, cancelled
        cancelled = True
        running = False
        root.quit()

    def on_close():
        cancel_action()

    def toggle_debug_inputs():
        if debug_mode.get():
            debug_frame.pack(pady=5)
        else:
            debug_frame.pack_forget()

    root = tk.Tk()
    root.title("EPUB-Auswahl")
    root.geometry("500x450")
    root.protocol("WM_DELETE_WINDOW", on_close)

    debug_mode = tk.BooleanVar(value=False)

    # --- Buttons ---
    btn_my_lang = tk.Button(root, text="My Language EPUB wählen", width=40,
                            command=lambda: choose_file("My Language"))
    btn_other_lang = tk.Button(root, text="Other Language EPUB wählen", width=40,
                               command=lambda: choose_file("Other Language"))
    btn_output_folder = tk.Button(root, text="Output Folder wählen", width=40,
                                  command=choose_output_folder)

    # --- Labels ---
    lbl_my_lang = tk.Label(root, text="My Language EPUB: – noch nicht gewählt –", wraplength=450, justify="left")
    lbl_other_lang = tk.Label(root, text="Other Language EPUB: – noch nicht gewählt –", wraplength=450, justify="left")
    lbl_output_folder = tk.Label(root, text="Output Folder: – noch nicht gewählt –", wraplength=450, justify="left")

    # --- Untere Button-Leiste ---
    frame_bottom = tk.Frame(root)
    btn_cancel = tk.Button(frame_bottom, text="Abbrechen", width=15, command=cancel_action)
    btn_continue = tk.Button(frame_bottom, text="Weiter", width=15, state="disabled", command=continue_action)

    # --- Debug-Modus Checkbox ---
    chk_debug = tk.Checkbutton(root, text="Debug-Modus aktivieren", variable=debug_mode, command=toggle_debug_inputs)

    # --- Eingabefelder für Debug-Parameter ---
    debug_frame = tk.Frame(root)

    lbl_thresh1 = tk.Label(debug_frame, text="csv min foreign row")
    entry_thresh1 = tk.Entry(debug_frame, width=6)
    entry_thresh1.insert(0, "0")

    lbl_thresh2 = tk.Label(debug_frame, text="csv min home col")
    entry_thresh2 = tk.Entry(debug_frame, width=6)
    entry_thresh2.insert(0, "0")

    lbl_thresh3 = tk.Label(debug_frame, text="csv max size")
    entry_thresh3 = tk.Entry(debug_frame, width=6)
    entry_thresh3.insert(0, "2000")

    # Layout für Debug-Parameter
    lbl_thresh1.grid(row=0, column=0, padx=5)
    entry_thresh1.grid(row=1, column=0, padx=5)

    lbl_thresh2.grid(row=0, column=1, padx=5)
    entry_thresh2.grid(row=1, column=1, padx=5)

    lbl_thresh3.grid(row=0, column=2, padx=5)
    entry_thresh3.grid(row=1, column=2, padx=5)

    # --- Layout Aufbau ---
    btn_my_lang.pack(pady=5)
    lbl_my_lang.pack(pady=5)
    btn_other_lang.pack(pady=5)
    lbl_other_lang.pack(pady=5)
    btn_output_folder.pack(pady=5)
    lbl_output_folder.pack(pady=5)

    chk_debug.pack(pady=10)  # Debug-Checkbox

    frame_bottom.pack(pady=20)
    btn_cancel.pack(side="left", padx=10)
    btn_continue.pack(side="right", padx=10)

    while running:
        root.mainloop()

    root.destroy()

    if cancelled or not all(result.values()):
        return None
    else:
        return result["my_lang"], result["other_lang"], result["output_folder"], debug_values




def format_text(text):
    text = text.replace("\u00A0", " ").replace("\u202F", " ")
    text = text.replace(" !", "!").replace("\n", " ")
    text = text.replace("  ", " ").replace("  ", " ")
    text = text.replace(" \u00BB", "\u00BB")
    # Unicode normalisieren (NFKC = Kompatibilitäts-Normalisierung)
    text = unicodedata.normalize("NFKC", text)
    # Alle Arten von Non-Break-Spaces in normales Leerzeichen umwandeln
    text = text.replace("\u00A0", " ").replace("\u202F", " ")
    # Tabs in Leerzeichen umwandeln
    text = text.replace("\t", " ")
    # Zeilenumbrüche behandeln:
    # 1. Zeilenumbruch + Kleinbuchstabe = " " (im Satz)
    text = re.sub(r"\n(?=[a-zäöüßàâéèùç])", " ", text)
    # 2. Mehrere Umbrüche = 1 Absatzumbruch
    text = re.sub(r"\n{2,}", "\n", text)
    # 3. Übrige einzelne Umbrüche auch in Leerzeichen umwandeln
    text = text.replace("\n", " ")
    # Mehrfache Leerzeichen reduzieren
    text = re.sub(r" {2,}", " ", text)
    # Kein Leerzeichen vor Satzzeichen (.,;:!?»)
    text = re.sub(r"\s+([.,;:!?»])", r"\1", text)
    # Leerzeichen nach öffnenden Guillemets («) entfernen
    text = re.sub(r"(«)\s+", r"\1", text)
    # Leerzeichen am Anfang/Ende entfernen
    text = text.strip()
    # Option: mehrere Satzendzeichen vereinheitlichen (z.B. "!!" → "!")
    text = re.sub(r"([!?]){2,}", r"\1", text)
    return text




def read_text_files_to_list(path_fremd_epub, path_heim_epub, debug = False):

    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        print("begin loading nltk")
        nltk.download('punkt')
        print("nltk loaded")

    fremd_heim = []
    durchlauf = 0
    for file_path in [path_fremd_epub,path_heim_epub]:
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
                    text_from_html = soup.get_text(separator="\n\n")
                    separated_at_newlines = re.split(r'\n\s*\n', text_from_html.strip())
                    separated_at_newlines = [absatz + " " for absatz in separated_at_newlines]
                    #separated_at_newlines = text_from_html.strip().split("\n\n")
                    html_item_list.extend(separated_at_newlines)

            if debug:
                write_string_list_in_txt(html_item_list, "# html" + str(durchlauf) + " eingelesen.txt")

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

        if debug:
            write_string_in_txt(lang_text, "# input " + str(durchlauf) +"_gelesen.txt")
            write_string_list_in_txt(sentence_list, "# input " + str(durchlauf) +"_getrennt.txt")

        sentence_list = [s + " " for s in sentence_list]
        fremd_heim.append(sentence_list)

    return fremd_heim[0], fremd_heim[1]

