from dataclasses import dataclass

import numpy as np
from sentence_transformers import SentenceTransformer, util
import os, torch
import networkx as nx

from Filepicker import Settings

MODEL_NAME = "distiluse-base-multilingual-cased-v2"

def xyz_cut_sort_and_clean(x, y, z, cutoff, clean1 = True, clean2 = True, results = None):
    x_ret,y_ret,z_ret = xyz_cutoff(x, y, z, cutoff)
    if results is not None:
        results.append(PathResults("Cutoff: " + str(cutoff),x_ret,y_ret,z_ret))
    if clean1:
        x_ret,y_ret,z_ret = xyz_clean_vert_horiz_lines(x_ret, y_ret, z_ret)
        if results is not None:
            results.append(PathResults("Cutoff+MultiClean: " + str(cutoff), x_ret, y_ret, z_ret))
    x_ret,y_ret,z_ret = xyz_sort_by_x(x_ret,y_ret,z_ret)
    if clean2:
        x_ret,y_ret,z_ret = xyz_clean_by_gradient(x_ret, y_ret, z_ret)
        if results is not None:
            results.append(PathResults("Cutoff+MultiClean+GradientClean: " + str(cutoff), x_ret, y_ret, z_ret))
    return x_ret,y_ret,z_ret

def matrix_find_best_cutoff(main_instance, matrix: np.ndarray, cutoff_candidates) -> []:
    candidate_list = []

    def progress_callback(percent=None, message=None):
        main_instance._update_progress(percent=percent, message=message)

    x,y,z = matrix_to_sorted_coordinates(matrix)
    i = 0
    for cutoff in cutoff_candidates:
        i += 1
        evaluation = xyz_evaluate_cutoff(x, y, z, cutoff)
        result = (cutoff, evaluation)
        candidate_list.append(result)
        percent_progress = 10 + 10 * i / len(cutoff_candidates)
        progress_callback(percent_progress,
                          "Cutoff candidate " + f"{cutoff:.2f}" + " results in " + str(evaluation) + " blocks")
        print("Cutoff candidate " + f"{cutoff:.2f}" + " results in " + str(evaluation) + "blocks")
    candidate_list.sort(key=lambda x: x[1], reverse=True)
    return candidate_list[0][0], candidate_list[0][1]



# input matrix (rows, cols) = (home,foreign)
def matrix_to_sorted_coordinates(matrix: np.ndarray):

    if matrix.ndim != 2:
        raise ValueError("Eingabe muss eine 2D Matrix sein")

    # Indizes der nicht-null Elemente - x und y anders als bisher x ist foreign
    x, y = np.nonzero(matrix)
    # Werte der Matrix an den (y, x) Positionen
    z = matrix[x, y]
    x,y,z = xyz_sort_by_x(x, y, z)
    return x,y,z

def xyz_sort_by_x(x, y, z):
    order = np.argsort(x)
    x_ret = x[order]
    y_ret = y[order]
    z_ret = z[order]
    return x_ret, y_ret, z_ret

def xyz_cutoff(x, y, z, cutoff):
    cutoff_filter = z >= cutoff
    x_filtered = x[cutoff_filter]
    y_filtered = y[cutoff_filter]
    z_filtered = z[cutoff_filter]
    return x_filtered, y_filtered, z_filtered

# wie viele einträge haben höheres y als diejenigen links von ihnen
def xyz_evaluate_cutoff(x, y, z, cutoff = None) -> int:
    if cutoff is not None:
        x, y, z = xyz_cut_sort_and_clean(x, y, z, cutoff, True, True)

    y_from_one_previous = np.roll(y, 1)
    y_from_one_previous[0] = 0
    differences_y = y - y_from_one_previous
    sum_of_values_higher_than_previous_one = np.count_nonzero(differences_y > 0)
    return int(sum_of_values_higher_than_previous_one)


def xyz_clean_by_gradient(x, y, z):
    x_shift_right = np.roll(x, 1)
    x_shift_right[0] = 0
    x_shift_left = np.roll(x, -1)
    x_shift_left[-1] = 0  ## problem

    y_shift_right = np.roll(y, 1)
    y_shift_right[0] = 0
    y_shift_left = np.roll(y, -1)
    y_shift_left[-1] = 0  ## problem

    differences_x_L = x - x_shift_right
    differences_y_L = y - y_shift_right
    grad_L = differences_y_L / differences_x_L  ## TODO divide by zero

    differences_x_R = x_shift_left - x
    differences_y_R = y_shift_left - y
    grad_R = differences_y_R / differences_x_R ## TODO divide by zero

    cond_R_grad = (grad_R < 4) & (grad_R >= 0)
    cond_L_grad = (grad_L < 4) & (grad_L >= 0)
    condition = cond_R_grad | cond_L_grad   # OR

    return x[condition == 1],y[condition == 1],z[condition == 1]


def xyz_clean_vert_horiz_lines(x, y, z):
    #x = coordinates[:, 0]
    #y = coordinates[:, 1]

    # Häufigkeiten berechnen
    unique_x, counts_x = np.unique(x, return_counts=True)
    unique_y, counts_y = np.unique(y, return_counts=True)
    # Werte mit count == 1
    unique_x_only = unique_x[counts_x == 1]
    unique_y_only = unique_y[counts_y == 1]
    # Maske
    mask = np.isin(x, unique_x_only) & np.isin(y, unique_y_only)
    # Indizes
    indices = np.where(mask)[0]
    x_ret = x[indices]
    y_ret = y[indices]
    z_ret = z[indices]
    return x_ret,y_ret,z_ret



def compute_and_store_embeddings(saetze, filename):
    if os.path.exists(filename):
        print("Embeddings existieren bereits -> lade sie")
        return torch.load(filename)

    print("Berechne embeddings...")
    model = SentenceTransformer(MODEL_NAME, device="cuda")
    emb = model.encode(
        saetze,
        convert_to_tensor=True,
        show_progress_bar=True
    )

    # auf CPU speichern (portabel)
    emb = emb.cpu()
    torch.save(emb, filename)
    print("Embeddings gespeichert:", filename)
    return emb


def find_filename(s):
    # Findet das letzte Vorkommen von '/' oder '\'
    letztes_slash = max(s.rfind('/'), s.rfind('\\'))
    # Extrahiere alles nach dem letzten '/'
    if letztes_slash != -1:
        nach_lastem_slash = s[letztes_slash + 1:]
    else:
        nach_lastem_slash = s  # Falls kein '/' oder '\' gefunden wird

    # Finde das letzte Vorkommen des Punkts '.'
    letzter_punkt = nach_lastem_slash.rfind('.')
    # Extrahiere alles vor dem letzten Punkt
    if letzter_punkt != -1:
        vor_letztem_punkt = nach_lastem_slash[:letzter_punkt]
    else:
        vor_letztem_punkt = nach_lastem_slash  # Falls kein Punkt gefunden wird

    return vor_letztem_punkt

def compute_similarity_from_cache(settings, fr_saetze, de_saetze):
    name_part = find_filename(settings.foreign_filename)
    emb_fr = compute_and_store_embeddings(fr_saetze, name_part + "fr_embeddings.pt")
    emb_de = compute_and_store_embeddings(de_saetze, name_part + "de_embeddings.pt")
    similarity_matrix = util.cos_sim(emb_fr, emb_de)
    return similarity_matrix.numpy()



# legt maske über die matrix die punkte aus der originalmatrix (re)aktiviert,
# die in den boxen zwischen den eindeutigen punkten liegen
def filter_matrix_by_xy_boxes(x, y, orig_matrix, cutoff = 0):
    shape = orig_matrix.shape
    mask = np.zeros(shape, dtype=bool)

    for x1, y1, x2, y2 in zip(x[:-1], y[:-1], x[1:], y[1:]):
        if x1<x2 and y1<=y2:
            xs = slice(min(x1, x2), max(x1, x2) + 1)
            ys = slice(min(y1, y2), max(y1, y2) + 1)
            mask[xs, ys] = True
    filtered_matrix = np.where(mask, orig_matrix, 0)
    x, y, z = matrix_to_sorted_coordinates(filtered_matrix)
    x, y, z = xyz_cut_sort_and_clean(x, y, z, cutoff, False, False)
    return x,y,z


@dataclass
class PathResults:
    name: str
    x: list
    y: list
    z: list

def matrix_to_optimal_paths(main_instance, settings : Settings, full_matrix, optimal_cutoff) -> list[PathResults]:
    results = []

    def progress_callback(percent=None, message=None):
        main_instance._update_progress(percent=percent, message=message)

    matrix = full_matrix.copy()
    x, y, z = matrix_to_sorted_coordinates(matrix)
    x, y, z = xyz_cut_sort_and_clean(x, y, z, optimal_cutoff)


    if not settings.input_use_path_algorithm or len(settings.input_path_box_cutoffs) == 0:
        progress_callback(60, "Path algorithm skipped. Just cut, sorted and cleanend. Done.")
        results.append(
            PathResults("Result only cutoff " + f"{optimal_cutoff:.2f}", x, y, z))
        return results


    number_of_runs = settings.input_use_path_algorithm * len(settings.input_path_diag_incentives) * len(settings.input_path_box_cutoffs)
    this_run_number = 0
    for i, box_cutoff in enumerate(settings.input_path_box_cutoffs):
        for j, diag_incentive in enumerate(settings.input_path_diag_incentives):
            this_run_number += 1
            x_list = []
            y_list = []
            z_list = []


            # verringert auch werte der fixen x,y,z aus dem fixen pfad von xyz_cut_sort_and_clean(x, y, z, optimal_cutoff)
            # dh muss werte korrigieren für diese punkte
            shape = matrix.shape
            mask_matrix = np.ones(shape, dtype=bool)
            x_np = np.array(x)
            y_np = np.array(y)
            mask_matrix[x_np, y_np] = False
            mask_matrix[matrix >= box_cutoff] = False
            matrix[mask_matrix] = -1


            for x1, y1, x2, y2 in zip(x[:-1], y[:-1], x[1:], y[1:]):
                if x1<x2 and y1<=y2 and x2-x1 < 100 and y2-y1 < 100: # and x1 < 50
                    xs = slice(min(x1, x2), max(x1, x2) + 1)
                    ys = slice(min(y1, y2), max(y1, y2) + 1)
                    mask = np.zeros(shape, dtype=bool)
                    mask[xs, ys] = True

                    x_coords, y_coords = np.where(mask)
                    z_vals = matrix[x_coords, y_coords]
                    #z_vals[z_vals == 0] -= 10

                    x_dom, y_dom, z_dom = longest_dominance_path(x_coords,y_coords, z_vals, diag_incentive)
                    x_list.extend(x_dom)
                    y_list.extend(y_dom)
                    z_list.extend(z_dom)
                    percent_progress = 25 + 60/number_of_runs * ((this_run_number -1) + x1 / max(x))
                    print(str(percent_progress) + " runs: " + str(number_of_runs) + " this: " + str(this_run_number) + " x1: " + str(x1) + " max " + str(max(x)))
                    progress_callback(percent_progress, "Path Opt " + str(this_run_number) + " of " + str(number_of_runs) + " step " + str(x1) + " von " + str(max(x)))
                    #print("path optimization along x: " + str(x1) + " von " + str(max(x)))
            eval = xyz_evaluate_cutoff(x_list, y_list, z_list)
            results.append(PathResults("Final + boxcut " + str(box_cutoff) + ", diag_inc " + str(diag_incentive) + " with " + str(eval) + " boxes", x_list,y_list,z_list))
    return results





def longest_dominance_path(x, y, z, diag_incentive = 0):
    edges = build_edges_from_sorted_points(x, y, z, diag_incentive)
    graph = nx.DiGraph()
    n = len(x)
    for i in range(n):
        graph.add_node(i, pos=(x[i], y[i]))

    for u, v, w in edges:
        graph.add_edge(u, v, weight=w)

    path_ids = nx.dag_longest_path(graph, weight="weight")

    return [x[i] for i in path_ids],[y[i] for i in path_ids],[z[i] for i in path_ids]


def build_edges_from_sorted_points(x, y, z, diag_incentive):
    n = len(x)

    if not (len(y) == n and len(z) == n):
        raise ValueError("x, y, z müssen gleiche Länge haben")

    edges = []

    for i in range(n):
        for j in range(n):

            if i == j:
                continue

            if x[i] < x[j] and y[i] < y[j]:
                edges.append((i, j, z[j]+diag_incentive))
            elif x[i] <= x[j] and y[i] <= y[j]:
                edges.append((i, j, z[j]))

    return edges