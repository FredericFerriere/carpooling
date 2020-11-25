import numpy as np
from sklearn.cluster import KMeans
from addressPoint import AddressPoint
from utilities.utils import *


def global_optimise(emp_addresses, target_address, max_pass):
    emp_points = {emp_address: AddressPoint(emp_address) for emp_address in emp_addresses}
    tgt_point = AddressPoint(target_address)
    emp_coords = {k: cartesian_coordinates(p, tgt_point, tgt_point.latitude)
                  for k, p in emp_points.items()}
    tgt_dist_mat = get_employees_distance_to_target(emp_points, tgt_point)
    emp_dist_mat = get_employees_distance_matrix(emp_points)
    init_groups = group_employees(emp_coords, max_pass)
    final_groups = []
    for g in init_groups:
        final_groups += optimise_group(g, emp_dist_mat, tgt_dist_mat, emp_coords)
    return final_groups


def optimise_group(cur_group, emp_dist_matrix, tgt_dist_matrix, emp_coords):
    sorted_group = sorted(cur_group, key=lambda emp: tgt_dist_matrix[emp])
    fin_paths = [[sorted_group[0]]]
    for i in range(1, len(sorted_group)):
        dist_to_tgt = tgt_dist_matrix[sorted_group[i]]
        ind = np.argmin([emp_dist_matrix[sorted_group[i]][path[-1]] for path in fin_paths])
        dist_to_path = emp_dist_matrix[sorted_group[i]][fin_paths[ind][-1]]
        if dist_to_path < dist_to_tgt:
            fin_paths[ind].append(sorted_group[i])
        else:
            fin_paths.append([sorted_group[i]])
    return fin_paths


def optimise_group_old(cur_group, emp_dist_matrix, tgt_dist_matrix, emp_coords):
    # sort furthest to closest
    sorted_group = sorted(cur_group, key=lambda emp: tgt_dist_matrix[emp], reverse=True)
    print('sorted_group : {}'.format(sorted_group))
    # get path length
    path_length = 0
    for i in range(len(cur_group)-1):
        path_length += emp_dist_matrix[sorted_group[i]][sorted_group[i+1]]
    path_length += tgt_dist_matrix[sorted_group[-1]]
    print('path length: {}'.format(path_length))

    # compare with individual paths
    ind_length = sum([tgt_dist_matrix[emp] for emp in cur_group])
    print('ind length: {}'.format(ind_length))

    res = []

    if path_length > ind_length:
        # split cur_group in 2
        print('splitting further')
        group_A, group_B = [], []
        kmeans = KMeans(n_clusters=2, random_state=4679).fit(np.array([emp_coords[k] for k in cur_group]))
        for i in range(len(kmeans.labels_)):
            if kmeans.labels_[i] == 0:
                group_A.append(cur_group[i])
            else:
                group_B.append(cur_group[i])
        res = res + optimise_group(group_A, emp_dist_matrix, tgt_dist_matrix, emp_coords)\
              + optimise_group(group_B, emp_dist_matrix, tgt_dist_matrix, emp_coords)
    else:
        res = sorted_group

    return res


def group_employees(emp_coords, max_pass):
    """
    :param emp_coords: employees' cartesian coordinates
    :param max_pass: maximum number of passengers in a car
    :return: a list of employee groups. Each element in the list is a list of employee addresses
    """
    cur_list = [[k for k in emp_coords]]
    cur_max = len(emp_coords)
    while cur_max > max_pass:
        new_list = []
        for sub_list in cur_list:
            if len(sub_list) > max_pass:
                kmeans = KMeans(n_clusters=2, random_state=4679).fit(np.array([emp_coords[k] for k in sub_list]))
                group_A, group_B = [], []
                for i in range(len(kmeans.labels_)):
                    if kmeans.labels_[i] == 0:
                        group_A.append(sub_list[i])
                    else:
                        group_B.append(sub_list[i])
                new_list.append(group_A)
                new_list.append(group_B)
            else:
                new_list.append(sub_list)
        cur_list = [sub_list for sub_list in new_list]
        cur_max = max([len(sub_l) for sub_l in cur_list])

    return cur_list



