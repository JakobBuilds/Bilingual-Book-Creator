import numpy as np
import copy
from scipy.signal import convolve2d, correlate2d
from sentence_transformers import SentenceTransformer, util
from UtilDebug import write_string_list_in_txt,write_matrix_in_csv

def compute_similarity_matrix(fr_saetze, de_saetze):
    # Embeddings berechnen
    print("compute embeddings...")
    model = SentenceTransformer("distiluse-base-multilingual-cased-v2", device="cuda")
    emb_de = model.encode(de_saetze, convert_to_tensor=True)
    emb_fr = model.encode(fr_saetze, convert_to_tensor=True)
    print("compute embeddings done")

    # Cosine Similarity zwischen allen Paaren
    print("compute cosine similarity...")
    similarity_matrix = util.cos_sim(emb_fr, emb_de)
    print("cosine similarity done")
    # Muss daten auf cpu schieben, sonst nicht bearbeitbar
    cpu_tensor = similarity_matrix.cpu()
    daten_matrix_cpu = cpu_tensor.numpy()
    return daten_matrix_cpu


# nicht eingesetzt, weil es nur Lücken von länge 1 überbrückt und sonst zu viel aufwand ist und zu fehleranfällig
# lücken von länge 1 sind im praktischen ergebnis egal und diese lösung hier wäre nur eine vermutung
def find_gap_matrix_with_convolution_methods(verbesserte_datenspur_mit_luecken):
    # jetzt mit correlate2d logik einbauen für lücken
    kernel_1 = np.array([[1, 0, 0],
                         [0, 0, 0],
                         [0, 0, 1]])
    kernel_2 = np.array([[1, 0, 0],
                         [-9, 0, 0],
                         [0, 1, 0]])
    kernel_3 = np.array([[1, -9, 0],
                         [0, 0, 1],
                         [0, 0, 0]])
    kernel_4 = np.array([[0, 0, 0],
                         [1, 0, 0],
                         [0, -9, 1]])
    kernel_5 = np.array([[0, 1, 0],
                         [0, 0, -9],
                         [0, 0, 1]])
    kernel_23_L = np.array([[1, 0, 0],
                            [0, 0, 0],
                            [0, 0, 0]])
    kernel_4_L = np.array([[0, 0, 0],
                           [1, 0, 0],
                           [0, 0, 0]])
    kernel_5_L = np.array([[0, 1, 0],
                           [0, 0, 0],
                           [0, 0, 0]])
    kernel_2_R = np.array([[0, 0, 0],
                           [0, 0, 0],
                           [0, 1, 0]])
    kernel_3_R = np.array([[0, 0, 0],
                           [0, 0, 1],
                           [0, 0, 0]])
    kernel_45_R = np.array([[0, 0, 0],
                            [0, 0, 0],
                            [0, 0, 1]])
    kernel_bulls_eye = np.array([[0, 0, 0],
                                 [0, 1, 0],
                                 [0, 0, 0]])

    print("begin convolution")
    conv_result_1 = correlate2d(verbesserte_datenspur_mit_luecken, kernel_1, mode='same', boundary='fill', fillvalue=0)
    conv_result_2 = correlate2d(verbesserte_datenspur_mit_luecken, kernel_2, mode='same', boundary='fill', fillvalue=0)
    conv_result_3 = correlate2d(verbesserte_datenspur_mit_luecken, kernel_3, mode='same', boundary='fill', fillvalue=0)
    conv_result_4 = correlate2d(verbesserte_datenspur_mit_luecken, kernel_4, mode='same', boundary='fill', fillvalue=0)
    conv_result_5 = correlate2d(verbesserte_datenspur_mit_luecken, kernel_5, mode='same', boundary='fill', fillvalue=0)
    conv_result_23_L = correlate2d(verbesserte_datenspur_mit_luecken, kernel_23_L, mode='same', boundary='fill',
                                   fillvalue=0)
    conv_result_4_L = correlate2d(verbesserte_datenspur_mit_luecken, kernel_4_L, mode='same', boundary='fill',
                                  fillvalue=0)
    conv_result_5_L = correlate2d(verbesserte_datenspur_mit_luecken, kernel_5_L, mode='same', boundary='fill',
                                  fillvalue=0)
    conv_result_2_R = correlate2d(verbesserte_datenspur_mit_luecken, kernel_2_R, mode='same', boundary='fill',
                                  fillvalue=0)
    conv_result_3_R = correlate2d(verbesserte_datenspur_mit_luecken, kernel_3_R, mode='same', boundary='fill',
                                  fillvalue=0)
    conv_result_45_R = correlate2d(verbesserte_datenspur_mit_luecken, kernel_45_R, mode='same', boundary='fill',
                                   fillvalue=0)
    conv_result_bulls_eye = correlate2d(verbesserte_datenspur_mit_luecken, kernel_bulls_eye, mode='same',
                                        boundary='fill', fillvalue=0)

    print("convolution fertig")

    # print("conv_result_1")
    # print(conv_result_1 * (conv_result_1 ))
    # print("conv_result_2")
    # print(conv_result_2)
    # print("conv_result_3")
    # print(conv_result_3)
    # print("conv_result_4")
    # print(conv_result_4)
    # print("conv_result_5")
    # print(conv_result_5)
    # print("conv_result_bulls_eye")
    # print(conv_result_bulls_eye)    # bulls eye macht gar nichts - belässt einfach die datenmatrix

    luecken_fuellen = (((conv_result_1 > 1) +  # LO, RU
                        ((conv_result_2 > 1) * ((conv_result_23_L - conv_result_2_R) > 0)) +  # LO, MU - LO > MU
                        ((conv_result_3 > 1) * ((conv_result_23_L - conv_result_3_R) > 0)) +
                        ((conv_result_4 > 1) * ((conv_result_4_L - conv_result_45_R) < 0)) +
                        ((conv_result_5 > 1) * ((conv_result_5_L - conv_result_45_R) < 0)))
                       * (conv_result_bulls_eye < 0.001))  # Multipliziere mit leerer Mitte - logisches UND

    return luecken_fuellen


# nicht eingesetzt, weil es nur Lücken von länge 1 überbrückt und sonst zu viel aufwand ist und zu fehleranfällig
# lücken von länge 1 sind im praktischen ergebnis egal und diese lösung hier wäre nur eine vermutung
def fuelle_luecken(verbesserte_datenspur_mit_luecken):
    luecken_fuellen_matrix = find_gap_matrix_with_convolution_methods(verbesserte_datenspur_mit_luecken)
    add_matrix = np.array([[1,0],[0,0]])
    result = broaden_trace_in_matrix(verbesserte_datenspur_mit_luecken, (luecken_fuellen_matrix > 0), add_matrix, 0, 0)
    return result


def schaerfe_datenspur_mit_kernel_convolution(daten_matrix_cpu_only_trail, kernel, min_value):
    # verstärke spur der datenmatrix und lösche outliers
    conv_result = convolve2d(daten_matrix_cpu_only_trail, kernel, mode='same', boundary='fill', fillvalue=0)
    daten_outliers_bereinigt = daten_matrix_cpu_only_trail * (conv_result > min_value)
    return daten_outliers_bereinigt

def spur_verbreiten_und_schaerfen(daten_matrix_cpu, daten_outliers_bereinigt, min_val = 0.7, spur_min_val = 0.5):
    add_matrix = np.array([[0, 1],[1, 1]])
    broad_trace_data = broaden_trace_in_matrix(daten_outliers_bereinigt, (daten_outliers_bereinigt >= min_val), add_matrix, 0, 0)
    daten_matrix_cpu_only_trail = daten_matrix_cpu.copy()

    breitere_datenspur = daten_matrix_cpu_only_trail * (broad_trace_data > min_val)
    verbesserte_datenspur_mit_luecken = breitere_datenspur * (breitere_datenspur > spur_min_val)
    return verbesserte_datenspur_mit_luecken


def broaden_trace_in_matrix(data_matrix, condition_mask, kernel, kernel_center_row, kernel_center_col):
    # Verwende filter_matrix um in der data_matrix bereiche durch punktweise multiplikation hervorzuheben
    # threshold muss überschritten werden im ergebnis, damit stellen in datamatrix aufgedeckt werden (true false matrix)
    # kernel: punktweises produkt und davon summe wird addiert an trefferstellen

    result = data_matrix.copy()
    d_rows, d_cols = data_matrix.shape
    kernel_rows, kernel_cols = kernel.shape
    for i, j in zip(*np.where(condition_mask)):
        min_row, max_row = i - kernel_center_row, i - kernel_center_row + kernel_rows - 1
        min_col, max_col = j - kernel_center_col, j - kernel_center_col + kernel_cols - 1
        if min_row >= 0 and max_row+1 <= d_rows and min_col >= 0 and max_col+1 <= d_cols:  # innerhalb des Feldes
            result[min_row:max_row+1, min_col:max_col+1] += kernel
    return result


def convolution_step_create_filter_matrix(data_matrix, condition_mask, add_matrix):
    # Verwende filter_matrix um in der data_matrix bereiche durch punktweise multiplikation hervorzuheben
    # threshold muss überschritten werden im ergebnis, damit stellen in datamatrix aufgedeckt werden (true false matrix)
    # kernel: punktweises produkt und davon summe wird addiert an trefferstellen

    # kernel muss ungerade zeilen- und spaltenzahl haben

    result = np.zeros_like(data_matrix)
    data_rows, data_cols = data_matrix.shape
    add_matrix_rows, add_matrix_cols = add_matrix.shape
    add_matrix_center_row = int(np.floor(add_matrix_rows / 2))   # start mit 0 also size 11 -> center row 5
    add_matrix_center_col = int(np.floor(add_matrix_cols / 2))

    # Addiere add_matrix nur dort, wo sie auch hinpasst:
    # Prüfe für jede koordinate für die zentriert die add_matrix addiert werden soll
    #   ob sie auch platz hat. Dh passen die äußersten zu addierenden punkte noch in die matrix?:
    for row_i, col_j in zip(*np.where(condition_mask)):
        min_add_row = row_i - add_matrix_center_row
        min_add_col = col_j - add_matrix_center_col

        max_add_row = row_i - add_matrix_center_row + add_matrix_rows
        max_add_col = col_j - add_matrix_center_col + add_matrix_cols

        if min_add_row >= 0 and max_add_row < data_rows and min_add_col >= 0 and max_add_col < data_cols:  # innerhalb des Feldes
            result[min_add_row:max_add_row, min_add_col:max_add_col] += add_matrix

    return result


def convolution_step_corridor(data_matrix, min_val, debug = False, csv_minrow_mincol_maxsize=None):

    # filtere stellen die 6 von 11 treffern haben auf der diagonale
    # dazu wird ein kernel verwendet, der eine diagonale auf breite 5 filtert
    # wenn eine stelle gefunden wurde wird sie markiert (zentrum des kernels)
    # es wird von einer 0-er matrix (mit den daten-dimensionen) ausgehend an allen markierten koordinaten
    #       die add_matrix addiert (zentriert und am rand abgeschnitten)
    # als letztes wird die originale daten-matrix auf die koordinaten reduziert, die in der aufsummierten ungleich 0 sind

    if csv_minrow_mincol_maxsize is None:
        csv_minrow_mincol_maxsize = [0, 0, 0]
    kernel = np.array([[1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                       [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0],
                       [1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0],
                       [0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
                       [0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0],
                       [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
                       [0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0],
                       [0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0],
                       [0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1],
                       [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                       [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]])

    # add_matrix muss "dünn" sein, denn sie wird an vielen koordinaten addiert, denn daten-punkte werden von
    #   leicht veränderten koordinaten auch getroffen
    # nach außen hin verbreiten, damit kurven erkannt werden bei sprüngen
    add_matrix = np.array([[1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1],
                           [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1]])

    trefferstellen_matrix = correlate2d(data_matrix, kernel, mode='same', boundary='fill',fillvalue=0)
    trefferstellen_matrix_filtered = trefferstellen_matrix > min_val

    filter_matrix = convolution_step_create_filter_matrix(data_matrix, trefferstellen_matrix_filtered, add_matrix)

    data_filtered = data_matrix * (filter_matrix > 0)

    if debug and csv_minrow_mincol_maxsize:
        write_matrix_in_csv(trefferstellen_matrix_filtered, "#2a conv_step_treffer_matrix min_val" + str(min_val) + ".csv", csv_minrow_mincol_maxsize[0],csv_minrow_mincol_maxsize[1],csv_minrow_mincol_maxsize[2])
        write_matrix_in_csv(filter_matrix > 0, "#2b conv_step_filter_matrix min_val" + str(min_val) + ".csv", csv_minrow_mincol_maxsize[0],csv_minrow_mincol_maxsize[1],csv_minrow_mincol_maxsize[2])
        write_matrix_in_csv(data_filtered, "#2c conv_step_data_result min_val" + str(min_val) + ".csv", csv_minrow_mincol_maxsize[0],csv_minrow_mincol_maxsize[1],csv_minrow_mincol_maxsize[2])
    return  data_filtered




def loesche_outliers_diagonalmethode(data_matrix, debug = False, csv_minrow_mincol_maxsize = None):

    def summe_der_abstaende(zahl, zahlen_liste):
        return sum(abs(z - zahl) for z in zahlen_liste)

    def entferne_zwei_groesste_ausreisser(liste):
        if len(liste) < 8:
            return liste

        median = np.median(liste)
        abstaende = [(abs(x - median), i) for i, x in enumerate(liste)]

        # Sortiere nach Abstand (größter zuerst)
        abstaende.sort(reverse=True)

        # Indizes der zwei größten Ausreißer
        zu_entfernen = sorted([abstaende[0][1], abstaende[1][1]], reverse=True)

        # Neue Liste ohne diese zwei
        neue_liste = liste.copy()
        for index in zu_entfernen:
            del neue_liste[index]

        return neue_liste

    d_rows, d_cols = data_matrix.shape
    rows_indices = []
    for r in range(0,d_rows):
        # für jede zeile füge indexe der nicht 0 elemente als liste hinzu
        row = data_matrix[r]
        non_zero_indices = np.nonzero(row)[0]
        non_zero_list = non_zero_indices.tolist()
        rows_indices.append(non_zero_list)
    rows_indices_copy = copy.deepcopy(rows_indices)

    debug_log = []
    for r_i in range(len(rows_indices)):
        if debug:
            debug_log.append(str("Zeile " + str(r_i) + ", Elemente: "))
            debug_strings = []
            for r_index_element in rows_indices[r_i]:
                debug_strings.append(str(r_index_element) + ", ")
            debug_log.append("".join(debug_strings))


        # falls in reihe r_i zwei nicht-0 elemente sind, muss der geringere abstand zur diagonalen gefunden werden:
        if len(rows_indices[r_i]) > 0:
            debug_log.append("     Anzahl Elemente: " + str(len(rows_indices[r_i]))) if debug else None

            # sammle elemente mit diagonal-korrektur
            vergleichs_elemente = []
            vergleichs_zeilen = []
            # gehe i reihen hoch und runter (von r_i) und sammle bis je 4 EINDEUTIGE elemente gefunden
            # wenn uneindeutig, dann wird die auswahl in die mitte geskewed...
            # (diagonalen-korrigiert) für den vergleich:
            previous_confirmed_indices = []
            i = 0
            first_found_distance = 0
            while r_i - i >= 0 and len(previous_confirmed_indices) < 5:
                if len(rows_indices[r_i - i]) == 1:
                    if first_found_distance == 0:
                        first_found_distance = i
                    # korrigiere vergleichselemente um diagonale: (i links -> i nach oben) ist "erwartete koordinate"
                    previous_confirmed_indices.append(rows_indices[r_i - i][0] + i)
                    vergleichs_zeilen.append(str(r_i - i))
                i += 1
            further_confirmed_indices = []
            i = 0
            while r_i + i < len(rows_indices) and len(further_confirmed_indices) < 5:
                if len(rows_indices[r_i + i]) == 1:
                    # korrigiere vergleichselemente um diagonale: (i rechts -> i nach unten) ist "erwartete koordinate"
                    further_confirmed_indices.append(rows_indices[r_i + i][0] - i)
                    vergleichs_zeilen.append(str(r_i + i))
                i += 1

            # problem: ausreißer (eindeutig in zeile) führt bias ein für nachbarn bei kandidatenvergleich
            # lösung: werde ihn in kandidatenvergleich los, indem man 5 kandidaten nimmt und 2 extreme entfernt
            # wenn unter 5 kandidaten, wird bei mindestens 2 kandidaten (unklarheit) einfach keiner gewählt
            vergleichs_elemente.extend(previous_confirmed_indices)
            vergleichs_elemente.extend(further_confirmed_indices)
            vgl_print = vergleichs_elemente.copy() if debug else None
            vergleichs_elemente = entferne_zwei_groesste_ausreisser(vergleichs_elemente)


            # wähle nur das element, das die summe der abstände (diagonalkorrigiert) minimiert:
            summen = [(x, summe_der_abstaende(x, vergleichs_elemente)) for x in rows_indices[r_i]]
            # Finde das Tupel mit der kleinsten Summe
            optimales_index_element, minimale_summe = min(summen, key=lambda t: t[1])
            #optimales_index_element = min(rows_indices[r_i], key=lambda x: summe_der_abstaende(x, vergleichs_elemente))

            # Fall behandeln: korrekte stellen alle 0, aber in selber zeile anderswo ungleich 0
            #  -> darf nicht das andere nehmen, sondern 0
            # deshalb als heuristik - durchschnitts-abstand (diagonalbereinigt) zu vergleichselementen sollte max 4 sein (eh viel)

            # filtere die datenmatrix, sodass nur die optimalen elemente verbleiben:
            # data_matrix[r_i] = [data_matrix[r_i][i] if i == optimales_index_element else 0 for i in range(len(data_matrix[r_i]))]
            filter_mask = np.zeros_like(data_matrix[r_i], dtype=bool)

            debug_log.append("     Bester Kandidat: " + str(optimales_index_element)) if debug else None

            verhaeltnis = minimale_summe / len(vergleichs_elemente)
            vergleichs_wert_tabelle = {5:5,
                                       8:7,
                                       12:9,
                                       15:17,
                                       20:25,
                                       25:35}
            vergleichs_faktor = 5000
            for grenze in sorted(vergleichs_wert_tabelle):
                if first_found_distance < grenze:
                    vergleichs_faktor = vergleichs_wert_tabelle[grenze]
                    break

            if minimale_summe < vergleichs_faktor * len(vergleichs_elemente):
                rows_indices[r_i][:] = [optimales_index_element]
                filter_mask[optimales_index_element] = True
                debug_log.append(str(optimales_index_element) + "   angenommen. Vergleichselemente: " + str(vgl_print)) if debug else None
                debug_log.append("          MinSum-Abst-Verh-VglFaktor: [" + str(minimale_summe) + "," + str(
                    first_found_distance) + "," + str(verhaeltnis) + "," + str(vergleichs_faktor) + "]")
                debug_log.append("\n\n")
            else:
                if debug:
                    debug_log.append("     Zeile " +  str(r_i) + ": kandidaten abgelehnt" + str(rows_indices[r_i]))
                    debug_log.append("          Vergleichselemente: " + str(vgl_print))
                    debug_log.append("          Vergleichs-Zeilen: " + str(vergleichs_zeilen))
                    debug_log.append("          MinSum-Abst-Verh-VglFaktor: [" + str(minimale_summe) + "," + str(
                        first_found_distance) + "," + str(verhaeltnis) + "," + str(vergleichs_faktor) + "]")

                    debug_log.append("\n\n")
                rows_indices[r_i][:] = []
            data_matrix[r_i] = data_matrix[r_i] * filter_mask





    # drucke maximal-abstand zwischen zwei nachbars-indizes
    max_abstand = 0
    max_index = None
    for i in range(len(rows_indices) - 1):
        current = rows_indices[i]
        next_ = rows_indices[i + 1]
        if len(current) == 1 and len(next_) == 1:
            abstand = abs(next_[0] - current[0])
            if abstand > max_abstand:
                max_abstand = abstand
                max_index = i  # Index des ersten Elements im Paar
    if debug:
        debug_log.append("ROW INDICES:")
        for ind in range(len(rows_indices)):
            debug_log.append("row: "+ str(ind) + "  --  " + str(rows_indices[ind]) + str(rows_indices_copy[ind]))
        if max_index is not None:
            debug_log.append(
                f"Größter Argmax-Sprung: {max_abstand} bei Index {max_index} (zwischen {rows_indices[max_index][0]} und {rows_indices[max_index + 1][0]})")
            print(f"Größter Argmax-Sprung: {max_abstand} bei Index {max_index} (zwischen {rows_indices[max_index][0]} und {rows_indices[max_index + 1][0]})")
        else:
            debug_log.append("Kein gültiges Paar gefunden.")
        write_string_list_in_txt(debug_log, "# argmax_diagonal_algorithmus.txt", False, "\n")


    return data_matrix




