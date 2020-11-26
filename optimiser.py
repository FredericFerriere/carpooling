import numpy as np
from sklearn.cluster import KMeans
from addressPoint import AddressPoint
from utilities.utils import *


def global_optimise(emp_addresses, target_address, max_pass):
    return 0


async def optimise_group_async(cur_group, emp_points, tgt_point):
    """
    :param cur_group: a list of addresses
    :param emp_points: dictionary of {address: addressPoint}
    :param tgt_point: addressPoint of target location
    :return: list, each element = [list of addresses, sumIndividualDistances, optimisedDistance]
    """
    emp_sub_points = {el: emp_points[el] for el in cur_group}
    emp_dist_matrix = await get_employees_distance_matrix_async(emp_sub_points)
    tgt_dist_matrix = await get_employees_distance_to_target_async(emp_sub_points, tgt_point)
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
    res = []
    for g in fin_paths:
        res.append([g, sum([tgt_dist_matrix[el] for el in g]), path_distance(g, emp_dist_matrix, tgt_dist_matrix)])
    return res


def group_employees(emp_coords, max_pass):
    """
    :param emp_coords: employees' cartesian coordinates, a dictionary {address: (x,y)}
    :param max_pass: integer. maximum number of passengers in a car
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



