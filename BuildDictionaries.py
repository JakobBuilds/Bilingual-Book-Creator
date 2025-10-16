from UtilDebug import write_string_list_in_txt


def build_dictionaries_starting_box_system(input_fr, input_de, datamatrix, debug = False):
    result_fr = []
    result_de = []
    rows, cols = datamatrix.shape
    started_box_coordinates = [0,0]


    for row_x in range(rows):  # rows sind fremdsprachige sätze
        # neue zeile, entweder max gleiche spalte oder weiter rechts
        col_y = datamatrix[row_x].argmax()  # index von höchstem wert in reihe - beste passung

        # diagonaler schritt - alles von start-koordinate bis vor aktuelle koordinate zusammenfügen
        if col_y > started_box_coordinates[1]:
            satz_liste_fremd = []

            for r in range(started_box_coordinates[0], row_x):
                satz_liste_fremd.append(str(r) + ": " + input_fr[r]) if debug else satz_liste_fremd.append(input_fr[r])
            satz_liste_fremd.append("\n\n") if debug else None
            satz_fremd = "".join(satz_liste_fremd)
            result_fr.append(satz_fremd)

            satz_liste_heim = []
            for c in range(started_box_coordinates[1], col_y):
                satz_liste_heim.append(str(c) + ": " + input_de[c]) if debug else satz_liste_heim.append(input_de[c])
            satz_liste_heim.append("\n\n") if debug else None
            satz_heim = "".join(satz_liste_heim)
            result_de.append(satz_heim)

            # box wurde abgeschlossen und mit den aktuellen koordinaten startet die nächste
            started_box_coordinates = [row_x,col_y]

    # ende der schleife - wsl mind in einer dimension noch inhalt - beide sprachen bis zum ende erweitern
    satz_liste_fremd = []

    for r in range(started_box_coordinates[0], rows):
        satz_liste_fremd.append(str(r) + ": " + input_fr[r]) if debug else satz_liste_fremd.append(input_fr[r])
    satz_liste_fremd.append("\n\n") if debug else None
    satz_fremd = "".join(satz_liste_fremd)
    result_fr.append(satz_fremd)

    satz_liste_heim = []
    for c in range(started_box_coordinates[1], cols):
        satz_liste_heim.append("column " + str(c) + ": " + input_de[c]) if debug else satz_liste_heim.append(input_de[c])
    satz_liste_heim.append("\n\n") if debug else None
    satz_heim = "".join(satz_liste_heim)
    result_de.append(satz_heim)

    if debug:
        satz_liste = []
        kuerzere_liste, laengere_liste = (satz_liste_fremd, satz_liste_heim) if len(satz_fremd) < len(satz_liste_heim) else (satz_liste_heim, satz_liste_fremd)
        for index in range(len(kuerzere_liste)):
            satz_liste.append(satz_liste_fremd[index])
            satz_liste.append(satz_liste_heim[index])
        for index in range(len(kuerzere_liste),len(laengere_liste)):
            satz_liste.append(laengere_liste[index])

        write_string_list_in_txt(satz_liste, "# translations box system.txt")

    return result_fr, result_de


def crop_long_blocks(dic_fremd, dic_heim, max_laenge):
    dic_f = []
    dic_h = []
    for block_index in range(len(dic_fremd)):
        words = dic_fremd[block_index].split()
        blocks_getrennt_fremd = [' '.join(words[i:i + max_laenge]) for i in range(0, len(words), max_laenge)]
        words = dic_heim[block_index].split()
        blocks_getrennt_heim = [' '.join(words[i:i + max_laenge]) for i in range(0, len(words), max_laenge)]

        # Gleiche die Längen der Listen an
        len_diff = len(blocks_getrennt_fremd) - len(blocks_getrennt_heim)
        if len_diff > 0:
            # fremd ist länger → heim auffüllen
            blocks_getrennt_heim.extend([" "] * len_diff)
        elif len_diff < 0:
            # heim ist länger → fremd auffüllen
            blocks_getrennt_fremd.extend([" "] * (-len_diff))
        dic_f.extend(blocks_getrennt_fremd)
        dic_h.extend(blocks_getrennt_heim)

    return dic_f, dic_h

