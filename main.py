
from DataPainter import DataPainter
from UtilDebug import write_sentences_in_csv
from BuildDictionaries import crop_long_blocks, build_dictionaries_new_path_boxes_system, read_and_format_text_files_to_list
from BookExport import save_book_versions
from Filepicker import user_input_settings
from DataVisualization import painter_add_cutoff_examples, painter_add_boxes_with_cutoff
from Datenbearbeitung import (compute_similarity_from_cache, matrix_find_best_cutoff, matrix_to_optimal_paths,
                              find_filename)
import tkinter as tk
from tkinter import ttk
import threading

import os
import time
import numpy as np


class Main:

    def __init__(self, settings, stop_event):
        self.settings = settings
        self.stop_event = stop_event
        self.cancel_event = None

        self.total_steps = 0
        self.current_step = 0

    def run(self, progress_callback, cancel_event = None):
        self.cancel_event = cancel_event
        self.progress_callback = progress_callback
        try:
            if self.stop_event.is_set():
                return
            self._initialize()
            if self.stop_event.is_set():
                return
            self._process_books()
            if self.stop_event.is_set():
                return
            self._optimize_cutoffs()
            if not self.stop_event.is_set():
                self._update_progress(message="Verarbeitung abgeschlossen.")
        except Exception as e:
            self._update_progress(message=f"Fehler in Main.run(): {e}")

    def _update_progress(self, percent=None, message=None):
        if self.progress_callback:
            self.progress_callback(percent=percent, message=message)

    def _check_cancel(self):
        if self.cancel_event and self.cancel_event.is_set():
            raise Exception("Verarbeitung abgebrochen.")

    def _initialize(self):
        self._update_progress(percent=0, message="Initialisiere...")
        os.chdir(self.settings.output_folder)
        self.input_cutoff_candidates = np.arange(
            self.settings.input_path_opt_from,
            self.settings.input_path_opt_to,
            self.settings.input_path_opt_stepsize
        )
        self._update_progress(percent=1, message="Initialisierung abgeschlossen.")

    def _process_books(self):
        self._update_progress(percent=3, message="Lese EPUB-Dateien und erstelle Similarity Matrix...")

        self.sentence_list_foreign, self.sentence_list_home = read_and_format_text_files_to_list(settings)
        sentences_foreign = np.array(self.sentence_list_foreign)
        sentences_home = np.array(self.sentence_list_home)

        #### COMPUTE COSINE SIMILARITY MATRIX FOR BOTH LANGUAGES
        self.daten_matrix_cpu_full = compute_similarity_from_cache(settings, sentences_foreign, sentences_home)

        self._check_cancel()
        self._update_progress(percent=7, message="EPUB-Verarbeitung abgeschlossen.")

    def _optimize_cutoffs(self):
        self._update_progress(percent=10, message="Starte Cutoff-Optimierung...")
        #### FIND A GOOD CUTOFF GIVEN THE PROCESSING (delete rows, cols with multiple values)
        optimal_cutoff, evaluation = matrix_find_best_cutoff(self, self.daten_matrix_cpu_full, self.input_cutoff_candidates)
        self._update_progress(percent=21, message="Found best cutoff at " + f"{optimal_cutoff:.2f}" + " with " + str(evaluation) + " boxes.")


        max_len = settings.input_max_hovertext_length
        foreign_limited = [f"{i}: {(s[:max_len - 3] + "...") if len(s) > max_len else s}" for i, s in
                           enumerate(self.sentence_list_foreign)]
        home_limited = [f"{i}: {(s[:max_len - 3] + "...") if len(s) > max_len else s}" for i, s in
                        enumerate(self.sentence_list_home)]


        # ANALYTICS, DISPLAY
        if settings.input_use_graphix:
            self._update_progress(percent=22, message="Initialize graphics...")
            painter = DataPainter(xlabels_foreign=foreign_limited, ylabels_home=home_limited)
            self._update_progress(percent=23, message="Initialize graphics done.")
            self._update_progress(percent=23, message="Creating cutoff demos...")
            painter_add_cutoff_examples(painter, self.daten_matrix_cpu_full, settings, optimal_cutoff, evaluation)
            painter_add_boxes_with_cutoff(painter, self.daten_matrix_cpu_full, optimal_cutoff, settings)
            self._update_progress(percent=25, message="Creating cutoff demos done.")

        # ACTUAL ALGORITHM

        self._update_progress(percent=25, message="Starting Path-Algorithm...")
        results = matrix_to_optimal_paths(self,settings, self.daten_matrix_cpu_full.copy(), optimal_cutoff)
        self._update_progress(percent=85, message="Path-Algorithm done.")


        self._update_progress(percent=85, message="Exportiere Ergebnisse...")
        for i, result in enumerate(results):
            if settings.input_use_graphix:
                painter.register_points(result.name, result.x, result.y, result.z)

            # build box system:
            dic_foreign, dic_home = build_dictionaries_new_path_boxes_system(self.sentence_list_foreign, self.sentence_list_home,
                                                                             result.x, result.y,
                                                                             settings.input_book_use_shortened_blocks)
            write_sentences_in_csv("sentence_list.csv", dic_foreign, dic_home)
            dic_foreign, dic_home = crop_long_blocks(dic_foreign, dic_home, settings.input_book_block_max_length)

            save_book_versions(find_filename(settings.foreign_filename), i, result, dic_foreign, dic_home)

        self._update_progress(percent=95, message="Export abgeschlossen.")
        if settings.input_use_graphix:
            painter.draw()
        self._update_progress(percent=100, message="Grafiken abgeschlossen.")








def run_main_program(user_settings):
    stop_event = threading.Event()

    def on_close():
        stop_event.set()
        root.destroy()

    root = tk.Tk()
    root.title("Verarbeitung läuft")
    root.protocol("WM_DELETE_WINDOW", on_close)

    status_text = tk.Text(root, height=15, state="disabled")
    status_text.pack(fill="both", expand=True, padx=10, pady=10)

    progress_var = tk.DoubleVar()
    progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
    progress_bar.pack(fill="x", padx=10, pady=10)

    # Definition des Callback
    def progress_callback(percent=None, message=None):
        def update():  # keine Parameter, weil wir sie schon über die Closure haben
            if percent is not None:
                progress_var.set(percent)
            if message is not None:
                status_text.config(state="normal")
                status_text.insert("end", message + "\n")
                status_text.see("end")
                status_text.config(state="disabled")

        root.after(0, update)

    # Main-Klasse starten
    main_app = Main(user_settings, stop_event)
    threading.Thread(target=main_app.run, args=(progress_callback,), daemon=True).start()

    root.mainloop()



if __name__ == "__main__":
    settings = user_input_settings()
    if settings is not None:
        run_main_program(settings)








# TODO OPTIONEN

# verschiedene pdf versionen verschönern / dem user optionen geben
# epub verbessern bei formatierung

# statt ebook auch txt lesen können und zwar va im gespeicherten format
# optimierungen beim lesen der ebooks? formatierung etc...

# sprachversionen

# ist kanten bauen teurer oder der pfad algorithmus selbst? GEHT KANTEN BAUEN GÜNSTIGER?
# INCENTIVE IST FAST NUTZLOS - GIBT ES EINEN BESSEREN ANREIZ FÜR DIAGONALEN?

# EXE BAUEN