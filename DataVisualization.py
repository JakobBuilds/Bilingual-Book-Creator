from DataPainter import DataPainter
from Datenbearbeitung import matrix_to_sorted_coordinates, xyz_cut_sort_and_clean, filter_matrix_by_xy_boxes, \
    matrix_to_optimal_paths


def painter_add_cutoff_examples(painter, daten_matrix_cpu_full, settings, optimal_cutoff, cutoff_evaluation):
    if settings.input_use_graphix:
        for _, cutoff in enumerate(settings.input_demo_cutoffs):
            x, y, z = matrix_to_sorted_coordinates(daten_matrix_cpu_full.copy())
            x, y, z = xyz_cut_sort_and_clean(x, y, z, cutoff, False, False)
            painter.register_points(f"demo cut at {cutoff:.2f}", x,y,z)


        x, y, z = matrix_to_sorted_coordinates(daten_matrix_cpu_full.copy())
        x2, y2, z2 = xyz_cut_sort_and_clean(x, y, z, optimal_cutoff,False,False)
        painter.register_points("opt_cut:" + f"{optimal_cutoff:.2f} cut", x2,y2,z2)
        x3, y3, z3 = xyz_cut_sort_and_clean(x2, y2, z2, optimal_cutoff,True, False)
        painter.register_points("opt_cut:" + f"{optimal_cutoff:.2f} multiclean", x3,y3,z3)
        x4, y4, z4 = xyz_cut_sort_and_clean(x3, y3, z3, optimal_cutoff,False,True)
        painter.register_points("opt_cut:" + f"{optimal_cutoff:.2f} gradient clean results in " + str(cutoff_evaluation) + " boxes", x4,y4,z4)


def painter_add_boxes_with_cutoff(painter, daten_matrix_cpu_full, optimal_cutoff, settings):
    x, y, z = matrix_to_sorted_coordinates(daten_matrix_cpu_full.copy())
    x, y, z = xyz_cut_sort_and_clean(x, y, z, optimal_cutoff)

    for _, box_cutoff in enumerate(settings.input_demo_cutoffs):
        x_c, y_c, z_c = filter_matrix_by_xy_boxes(x, y, daten_matrix_cpu_full.copy(), box_cutoff)
        painter.register_points("opt+boxes_"+ str(box_cutoff), x_c, y_c, z_c)




