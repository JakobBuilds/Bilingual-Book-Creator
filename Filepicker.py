import tkinter as tk
from dataclasses import dataclass, asdict, field
from tkinter import filedialog
from pathlib import Path
import json
from tkinter import messagebox

import threading
from tkinter import ttk


APP_NAME = "Filepicker"
CONFIG_PATH = Path.home() / f".{APP_NAME}_last_session.json"

def parse_float_list(text):
    if not text.strip():
        return []
    return [float(x.strip()) for x in text.split(",")]


def format_float_list(values):
    return ", ".join(str(v) for v in values)


def user_input_settings():
    return_settings = Settings()

    running = True
    cancelled = False


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
            return_settings.home_filename = path
            lbl_my_lang.config(text=f"My Language EPUB:\n{path}")
        else:
            return_settings.foreign_filename = path
            lbl_other_lang.config(text=f"Other Language EPUB:\n{path}")
        check_ready()

    def choose_output_folder():
        folder = filedialog.askdirectory(title="Ausgabeordner wählen")
        if not folder:
            return
        return_settings.output_folder = folder
        lbl_output_folder.config(text=f"Output Folder:\n{folder}")
        check_ready()

    def check_ready():
        if return_settings.check_is_ready():
            btn_continue.config(state="normal")
        else:
            btn_continue.config(state="disabled")

    def continue_action():
        nonlocal running

        try:
            # Debug Flag
            return_settings.input_use_graphix = debug_mode_graphix.get()
            return_settings.input_use_debug_txt = debug_mode_txt_log.get()

            # Integer
            return_settings.input_max_hovertext_length = int(entry_hover_len.get())

            # Float-Listen
            return_settings.input_demo_cutoffs = parse_float_list(entry_demo_cutoffs.get())
            return_settings.input_demo_box_cutoffs = parse_float_list(entry_demo_box.get())

            return_settings.input_use_path_algorithm = path_algo_var.get()
            return_settings.input_path_opt_from  = float(entry_path_from.get())
            return_settings.input_path_opt_to  = float(entry_path_to.get())
            return_settings.input_path_opt_stepsize  = float(entry_path_stepsize.get())

            return_settings.input_path_box_cutoffs = parse_float_list(entry_path_box.get())
            return_settings.input_path_diag_incentives = parse_float_list(entry_path_diag.get())

            return_settings.input_book_use_shortened_blocks = book_short_var.get()
            return_settings.input_book_block_max_length = int(entry_block_len.get())


        except ValueError:
            tk.messagebox.showerror("Fehler", "Bitte gültige Zahlenwerte eingeben.")
            return

        running = False
        return_settings.save_to_file(CONFIG_PATH)
        root.quit()

    def cancel_action():
        nonlocal running, cancelled
        cancelled = True
        running = False
        root.quit()

    def on_close():
        cancel_action()

    def show_explanation():
        explanation_window = tk.Toplevel(root)
        explanation_window.title("Anwendung – Erklärung")
        explanation_window.geometry("600x600")
        explanation_window.transient(root)
        explanation_window.grab_set()

        # Hauptframe
        frame = tk.Frame(explanation_window)
        frame.pack(fill="both", expand=True, padx=15, pady=15)

        # Scrollbar
        scrollbar = tk.Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")

        text_widget = tk.Text(
            frame,
            wrap="word",
            yscrollcommand=scrollbar.set,
            font=("TkDefaultFont", 10)
        )
        text_widget.pack(fill="both", expand=True)

        scrollbar.config(command=text_widget.yview)

        # >>> HIER DEIN ERKLÄRUNGSTEXT <<<
        explanation_text = """
    Bilingual Book Creator – Anleitung
    ==================================

    1. My Language Epub:
    Choose the book of your language
        
    2. Other Language Epub:
    Choose the book of the foreign language
    
    3. Output Folder:
    Choose output folder
    
    4. Abbrechen:
    Cancel
    
    5. Weiter:
    Continue
    
    6. Cutoff Optimization
    Choose candidate values for the optimal Cutoff. 
    The algorithm will cut off correlations weaker than that value. 
    Then it will optimize for how many translation boxes are being created by 
    - Multiclean: Delete all Values in Columns and Rows with more than 1 Value
    - Gradient Clean: Delete all Values where Gradient to neighbours is out of range
    Variables:
    Here we generate the recommended values from 0.5 to 0.8 with 0.3 apart:
    From - recommended 0.5
    To - recommended 0.8
    Stepsize - recommended 0.3
    Optimal Value is mostly around 0.63
    
    7. Path Algorithm
    Choose whether you want to use the computationally expensive path algorithm. 
    Between every two neighbouring points, this algorithm will inject a box of points 
    from the original data that has been cleaned away too rigorously before.
    
    You can choose the cutoff for these boxes and in these boxes the path algorithm
    will look for the path that finds the most points with highest correlation values.
    If you use a low cutoff (below 0.4) this might take a long time, depending on the book.
    You can use multiple box cutoffs. Then put a comma in between (0.4,0.5,0.7)
    Use values between 0 and 1. Ideally not much higher than 0.7
    Recommended: 0.4
    
    Path diag incentives is an incentive for the algorithm to find diagonal paths,
    which will lead to more translation boxes.
    It will only skip one nondiagonal value smaller than the incentive
    You can use multiple incentives. Then put a comma in between (0.4,0.5,0.7)
    Recommended: 0.5
    
    8. Debug Mode
    You can choose to get a graphical analysis. 
    This will give you visual feedback on the correlations and how they are processed.
    You can choose the hovertext length for the interactive graphics.
    
    The demo cutoff determines the first demo plots, where you can see how the cutoff
    applied to the data looks and where you can explore the correlation data. 
    If you choose it too low (below 0.3 depending on the book), 
    the plotting might take long or might fail.
    You can use multiple demo cutoffs. Then put a comma in between (0.4,0.5,0.7)
    
    The demo box cutoff determines the boxes that will be shown in the graph before the 
    path algorithm is applied.
    You can use multiple demo box cutoffs. Then put a comma in between (0.4,0.5,0.7)
    
    9. Book settings
    You can choose to use shortened blocks. This means that if somehow a text block on 
    one side or the other gets longer than 20 sentences, only the first few will be shown.
    The missing ones will be represented by ... #number of missing sentences ...
    
    This might happen, when the variables are chosen badly, the algorithm somehow performs 
    poorly or when one book is not a literal translation of the other, but perhaps a 
    shortened version or part 1 whereas the other book is the full volume.
    
    Book block length is also meant for cases where very long blocks exist. Especially if you 
    choose not to shorten blocks like mentioned above. Then in order for the pdf output not to 
    overflow and fail you can choose at what number of words to cut the block into smaller blocks.
    
    """

        text_widget.insert("1.0", explanation_text)
        text_widget.config(state="disabled")

        # Schließen-Button
        btn_close = tk.Button(explanation_window, text="Schließen", command=explanation_window.destroy)
        btn_close.pack(pady=10)

    def toggle_debug_inputs():
        if debug_mode_graphix.get():
            debug_outer_frame.pack(pady=5, fill="x")  # fill="x" wichtig
            debug_inner_frame.pack(anchor="w", fill="x", padx=10, pady=5)  # linksbündig erzwingen
        else:
            debug_inner_frame.pack_forget()

    def toggle_path_settings():
        if path_algo_var.get():
            path_settings_frame.pack(anchor="w", padx=20, pady=5)
        else:
            path_settings_frame.pack_forget()


    return_settings = return_settings.load_from_file()



    root = tk.Tk()

    main_frame = tk.Frame(root)
    main_frame.pack(fill="both", expand=True)

    left_frame = tk.Frame(main_frame)
    left_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

    right_frame = tk.Frame(main_frame, width=450)
    right_frame.pack(side="right", fill="y", padx=10, pady=10)
    right_frame.pack_propagate(False)  # verhindert automatisches Schrumpfen



    root.title("Create Bilingual Books")
    root.geometry("800x600")
    root.protocol("WM_DELETE_WINDOW", on_close)

    debug_mode_graphix = tk.BooleanVar(value=return_settings.input_use_graphix)
    debug_mode_txt_log = tk.BooleanVar(value=return_settings.input_use_debug_txt)

    # --- Buttons ---
    btn_my_lang = tk.Button(left_frame, text="My Language EPUB wählen", width=30,
                            command=lambda: choose_file("My Language"))
    btn_other_lang = tk.Button(left_frame, text="Other Language EPUB wählen", width=30,
                               command=lambda: choose_file("Other Language"))
    btn_output_folder = tk.Button(left_frame, text="Output Folder wählen", width=30,
                                  command=choose_output_folder)

    # --- Labels ---
    lbl_my_lang = tk.Label(left_frame, text="My Language EPUB: – noch nicht gewählt –", wraplength=250, justify="left")
    lbl_other_lang = tk.Label(left_frame, text="Other Language EPUB: – noch nicht gewählt –", wraplength=250, justify="left")
    lbl_output_folder = tk.Label(left_frame, text="Output Folder: – noch nicht gewählt –", wraplength=250, justify="left")

    # =====================================
    # Drei einzelne Float-Felder nebeneinander
    # =====================================

    opt_frame = tk.LabelFrame(right_frame, text="Cutoff Optimization")
    opt_frame.pack(pady=10, fill="x", padx=10)

    path_variables_label = tk.Label(opt_frame, text="Path Optimization: From, To, Stepsize")
    path_variables_label.pack(anchor="w")

    single_cutoff_frame = tk.Frame(opt_frame)
    single_cutoff_frame.pack(anchor="w", pady=5)

    # tk.Label(single_cutoff_frame, text="Path Optimization: From, To, Stepsize").grid(row=0, column=0, sticky="w", padx=(0, 10))

    entry_path_from = tk.Entry(single_cutoff_frame, width=8)
    entry_path_from.insert(0, str(return_settings.input_path_opt_from))
    entry_path_from.grid(row=0, column=0, padx=5)

    entry_path_to = tk.Entry(single_cutoff_frame, width=8)
    entry_path_to.insert(0, str(return_settings.input_path_opt_to))
    entry_path_to.grid(row=0, column=1, padx=5)

    entry_path_stepsize = tk.Entry(single_cutoff_frame, width=8)
    entry_path_stepsize.insert(0, str(return_settings.input_path_opt_stepsize))
    entry_path_stepsize.grid(row=0, column=2, padx=5)
    # =====================================


    # ===============================
    # Path Algorithm (immer sichtbar)
    # ===============================

    path_frame = tk.LabelFrame(right_frame, text="Path Algorithm")
    path_frame.pack(pady=10, fill="x", padx=10)

    path_algo_var = tk.BooleanVar(value=return_settings.input_use_path_algorithm)

    tk.Checkbutton(
        path_frame,
        text="Use Path Algorithm",
        variable=path_algo_var,
        command=lambda: toggle_path_settings()
    ).pack(anchor="w", pady=5)

    # Untergeordneter Frame für Cutoffs
    path_settings_frame = tk.Frame(path_frame)



    tk.Label(path_settings_frame, text="Path Box Cutoffs (comma separated):").pack(anchor="w")
    entry_path_box = tk.Entry(path_settings_frame, width=40)
    entry_path_box.insert(0, format_float_list(return_settings.input_path_box_cutoffs))
    entry_path_box.pack(anchor="w", pady=2)

    tk.Label(path_settings_frame, text="Path Diag Incentives (comma separated):").pack(anchor="w")
    entry_path_diag = tk.Entry(path_settings_frame, width=40)
    entry_path_diag.insert(0, format_float_list(return_settings.input_path_diag_incentives))
    entry_path_diag.pack(anchor="w", pady=2)

    if path_algo_var.get():
        path_settings_frame.pack(anchor="w", padx=20, pady=5)

    # ===============================
    # Debug Modus Optionen
    # ===============================

    debug_outer_frame = tk.LabelFrame(right_frame, text="Debug Mode")
    debug_outer_frame.pack(pady=10, fill="x", padx=10)



    debug_header_frame = tk.Frame(debug_outer_frame)
    debug_header_frame.pack(anchor="w", pady=5, padx=5, fill="x")

    # Checkbox links
    chk_debug_graphix = tk.Checkbutton(
        debug_header_frame,
        text="Grafik Analyse erstellen",
        variable=debug_mode_graphix,
        command=toggle_debug_inputs
    )
    chk_debug_graphix.pack(side="left")

    # Button rechts daneben
    chk_debug_log = tk.Checkbutton(
        debug_header_frame,
        text="Text Files erstellen",
        variable=debug_mode_txt_log
    )
    chk_debug_log.pack(side="left", padx=10)  # Abstand zur Checkbox





    # --- Inner Frame für Debug Parameter ---
    debug_inner_frame = tk.Frame(debug_outer_frame)

    # --- Hovertext Länge (int) ---
    tk.Label(debug_inner_frame, text="Max Hovertext Length:").pack(anchor="w")
    entry_hover_len = tk.Entry(debug_inner_frame, width=20)
    entry_hover_len.insert(0, str(return_settings.input_max_hovertext_length))
    entry_hover_len.pack(anchor="w", pady=2)

    # --- Demo Cutoffs ---
    tk.Label(debug_inner_frame, text="Demo Cutoffs (comma separated):").pack(anchor="w")
    entry_demo_cutoffs = tk.Entry(debug_inner_frame, width=40)
    entry_demo_cutoffs.insert(0, format_float_list(return_settings.input_demo_cutoffs))
    entry_demo_cutoffs.pack(anchor="w", pady=2)

    # --- Demo Box Cutoffs ---
    tk.Label(debug_inner_frame, text="Demo Box Cutoffs (comma separated):").pack(anchor="w")
    entry_demo_box = tk.Entry(debug_inner_frame, width=40)
    entry_demo_box.insert(0, format_float_list(return_settings.input_demo_box_cutoffs))
    entry_demo_box.pack(anchor="w", pady=2)

    # Initialzustand des Debug-Blocks
    toggle_debug_inputs()

    # ===============================
    # Book Settings (immer sichtbar)
    # ===============================

    book_frame = tk.LabelFrame(right_frame, text="Book Settings")
    book_frame.pack(pady=10, fill="x", padx=10)

    # Innerer Frame für die horizontale Ausrichtung
    book_inner_frame = tk.Frame(book_frame)
    book_inner_frame.pack(anchor="w", padx=5, pady=5, fill="x")

    # Checkbox Use Shortened Blocks links
    book_short_var = tk.BooleanVar(value=return_settings.input_book_use_shortened_blocks)
    chk_short = tk.Checkbutton(book_inner_frame, text="Use Shortened Blocks", variable=book_short_var)
    chk_short.grid(row=0, column=0, sticky="w", padx=(0, 20))

    # Label + Entry für Book Block Max Length rechts davon
    tk.Label(book_inner_frame, text="Book Block Max Length (Words):").grid(row=0, column=1, sticky="w")
    entry_block_len = tk.Entry(book_inner_frame, width=10)
    entry_block_len.insert(0, str(return_settings.input_book_block_max_length))
    entry_block_len.grid(row=0, column=2, sticky="w", padx=(5, 0))






    # --- Untere Button-Leiste ---
    frame_bottom = tk.Frame(left_frame)
    btn_explain = tk.Button(frame_bottom, text="?", width=5, command=show_explanation)
    btn_cancel = tk.Button(frame_bottom, text="Abbrechen", width=10, command=cancel_action)
    btn_continue = tk.Button(frame_bottom, text="Weiter", width=10, state="disabled", command=continue_action)









    if return_settings.home_filename is not None:
        lbl_my_lang.config(text=f"My Language EPUB:\n{return_settings.home_filename}")

    if return_settings.foreign_filename is not None:
        lbl_other_lang.config(text=f"Other Language EPUB:\n{return_settings.foreign_filename}")

    if return_settings.output_folder is not None:
        lbl_output_folder.config(text=f"Output Folder:\n{return_settings.output_folder}")

    check_ready()  # aktiviert den Weiter-Button sofort

    # --- Layout Aufbau ---
    btn_my_lang.pack(pady=5)
    lbl_my_lang.pack(pady=5)
    btn_other_lang.pack(pady=5)
    lbl_other_lang.pack(pady=5)
    btn_output_folder.pack(pady=5)
    lbl_output_folder.pack(pady=5)


    frame_bottom.pack(pady=20)
    btn_explain.pack(side="left", padx=3)
    btn_cancel.pack(side="left", padx=3)
    btn_continue.pack(side="right", padx=3)





    while running:
        root.mainloop()

    root.destroy()

    if cancelled or not return_settings.check_is_ready():
        return None
    else:
        return return_settings











@dataclass
class Settings:
    home_filename: str = None
    foreign_filename: str = None
    book_filename:str = None
    output_folder: str = None
    input_use_graphix: bool = False
    input_use_debug_txt: bool = False

    input_max_hovertext_length: int = 150
    input_demo_cutoffs: list = field(default_factory=lambda: [0.4, 0.6, 0.8])
    input_demo_box_cutoffs: list = field(default_factory=lambda: [0.4, 0.5])

    input_use_path_algorithm: bool = True
    input_path_opt_from: float = 0.5
    input_path_opt_to: float = 0.9
    input_path_opt_stepsize: float = 0.03
    input_path_box_cutoffs: list = field(default_factory=lambda: [0.4, 0.5])
    input_path_diag_incentives: list = field(default_factory=lambda: [0.45])

    input_book_use_shortened_blocks: bool = True
    input_book_block_max_length: int = 300

    def check_is_ready(self):
        return self.home_filename is not None and self.foreign_filename is not None and self.output_folder is not None

    def save_to_file(self, filename):
        """Speichert die Settings als JSON-Datei."""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(asdict(self), f, ensure_ascii=False, indent=4)


    @classmethod
    def load_from_file(cls):

        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return cls(**data)
            except Exception:
                pass
        return Settings()

