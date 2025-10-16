from PDFexport import export_pdf_vertical,export_pdf_horizontal,export_pdf_horizontal_foreign_right
from PDFexport import export_best_style
from UtilDebug import write_matrix_mit_saetzen_in_csv

from Datenbearbeitung import compute_similarity_matrix
from Datenbearbeitung import loesche_outliers_diagonalmethode, convolution_step_corridor

from Filepicker import pick_epubs_and_output, read_text_files_to_list
from BuildDictionaries import build_dictionaries_starting_box_system,crop_long_blocks

import os
import numpy as np


# Für alle Druckvorgänge der Matrizen (code intern)
np.set_printoptions(precision=2, suppress=True, linewidth=400, threshold=1000000)



#### TEXTE EINLESEN
print("Starte Filepicker...")
result = pick_epubs_and_output()
heimsprach_file, fremdsprach_file, output_folder, debug_values = result

debug_mode = debug_values["enabled"]
if debug_mode:
    csv_minrow_mincol_maxsize = [int(x) for x in debug_values["thresholds"]]
else:
    csv_minrow_mincol_maxsize = [0,0,100]

os.chdir(output_folder)

# READ INPUT FILES
sentence_list_foreign, sentence_list_home  = read_text_files_to_list(fremdsprach_file, heimsprach_file, debug_mode)

fremd_saetze = np.array(sentence_list_foreign)
heim_saetze = np.array(sentence_list_home)




#### COMPUTE COSINE SIMILARITY MATRIX FOR BOTH LANGUAGES AND REDUCE TO ONLY HIGHER VALUES
daten_matrix_cpu_full = compute_similarity_matrix(fremd_saetze, heim_saetze)
daten_matrix_cpu_only_trail = daten_matrix_cpu_full.copy()
daten_matrix_cpu_only_trail[daten_matrix_cpu_only_trail < 0.6] = 0

if debug_mode:
    write_matrix_mit_saetzen_in_csv(daten_matrix_cpu_only_trail,
                                    fremd_saetze,
                                    heim_saetze,
                                    "#1 matrix 06-gefiltert.csv",
                                    csv_minrow_mincol_maxsize[0],
                                    csv_minrow_mincol_maxsize[1],
                                    csv_minrow_mincol_maxsize[2])



#### LÖSCHE OUTLIER MIT KERNEL CONVOLUTION UND ANSCHLIESSENDEM LÖSCHEN VON NIEDRIGEN WERTEN
#daten_outliers_bereinigt = schaerfe_datenspur_mit_kernel_convolution(daten_matrix_cpu_only_trail, np.eye(3), 1)
#print("Daten Outliers bereinigt: \n" , daten_outliers_bereinigt[40:100,40:100])
#daten_outliers_bereinigt = loesche_outliers_diagonalmethode(daten_outliers_bereinigt, debug = True)


data_outliers_filtered = convolution_step_corridor(daten_matrix_cpu_only_trail, min_val= 2, debug = debug_mode, csv_minrow_mincol_maxsize = csv_minrow_mincol_maxsize)


data_outliers_removed = loesche_outliers_diagonalmethode(data_outliers_filtered, debug = debug_mode, csv_minrow_mincol_maxsize = csv_minrow_mincol_maxsize)



#write_matrix_in_csv(daten_outliers_bereinigt, "outliers_bereinigt 06 ohne conv mit neuer methode.csv")
if debug_mode:
    write_matrix_mit_saetzen_in_csv(data_outliers_removed,fremd_saetze,heim_saetze,"#3 matrix diagonalmethoden-gelöscht.csv",csv_minrow_mincol_maxsize[0],csv_minrow_mincol_maxsize[1],csv_minrow_mincol_maxsize[2])





#### PDF PRINT
# build box system:
print("start building dics")
dic_foreign, dic_home = build_dictionaries_starting_box_system(sentence_list_foreign, sentence_list_home, data_outliers_removed, debug_mode)
print("done building dics")


dic_foreign, dic_home = crop_long_blocks(dic_foreign, dic_home, 420)

export_pdf_vertical("bilingual_vertical.pdf", dic_foreign, dic_home)
export_pdf_horizontal("bilingual_horizontal_outbound.pdf", dic_foreign, dic_home)
export_pdf_horizontal_foreign_right("bilingual_horizontal_inbound, foreign right.pdf", dic_foreign, dic_home)
export_best_style("bilingual__horizontal_preference.pdf", dic_foreign, dic_home)
print("pdf done")

### TODO cpu und grafikkarten version in github
### TODO start der diagonal lösch methode
### TODO outliers mit convolution löschen