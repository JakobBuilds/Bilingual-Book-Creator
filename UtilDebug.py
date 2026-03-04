import csv
import numpy as np

def write_string_list_in_txt(string_list, filename, optional_line_prints = False, abstands_string = "\n\n"):
        with open(filename, "w", encoding="utf-8") as f:
            line = 0
            for s in string_list:
                if optional_line_prints:
                    f.write(str(line))
                    line += 1
                    f.write(": \n")
                f.write(s)
                f.write(abstands_string)


def write_string_in_txt(s, filename):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(s)

def write_matrix_with_sentences_in_csv(matrix, fremd_saetze, heim_saetze, name, start_row= 0, start_col = 0, max_size = 1000):

    max_col = start_col + max_size
    max_row = start_row + max_size

    rows, cols = matrix.shape
    subset = matrix[max(0, start_row):min(max_row, rows), max(0,start_col):min(max_col, cols)]

    row_labels = fremd_saetze.copy()
    col_labels = heim_saetze.copy()

    row_labels = row_labels[max(0, start_row):min(max_row, rows)]
    col_labels = col_labels[max(0, start_col):min(max_col, cols)]

    # kürzen der einzelnen strings
    row_labels = [" ".join(label.split()[:4]) for label in row_labels]
    col_labels = [" ".join(label.split()[:4]) for label in col_labels]

    # Umwandeln in Spalte (shape (3, 1)) und in Strings casten
    row_labels_col = np.array(row_labels).reshape(-1, 1)

    # Cast der numerischen Matrix auf `str`, sonst klappt das Zusammenfügen nicht
    matrix_str = subset.astype(str)

    # Horizontales Zusammenfügen
    matrix_with_rows = np.hstack((row_labels_col, matrix_str))

    # Schritt 3: Spaltenlabelzeile vorbereiten (eins mehr, da erste Spalte Zeilenlabels sind)
    header_row = np.array([""] + col_labels).reshape(1, -1)

    # Schritt 4: Header und Datenmatrix vertikal zusammenfügen
    labelled_table = np.vstack((header_row, matrix_with_rows))

    with open(name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(labelled_table)

def write_matrix_in_csv(matrix, name, start_row= 0, start_col = 0, max_size = 1000):

    max_col = start_col + max_size
    max_row = start_row + max_size

    rows, cols = matrix.shape
    subset = matrix[max(0, start_row):min(max_row, rows), max(0,start_col):min(max_col, cols)]


    with open(name, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(subset)


def write_sentences_in_csv(filename, list_foreign, list_home):
    if len(list_foreign) != len(list_home):
        raise ValueError("Die Listen müssen gleich lang sein.")

    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Foreign", "Home"])
        for satz1, satz2 in zip(list_foreign, list_home):
            writer.writerow([satz1, satz2])

