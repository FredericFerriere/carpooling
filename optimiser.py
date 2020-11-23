import numpy as np
from sklearn.cluster import KMeans
from addressPoint import AddressPoint
from utilities.utils import *


def global_optimise(emp_addresses, target_address, max_pass):
    emp_address_dict = {emp_address: AddressPoint(emp_address) for emp_address in emp_addresses}
    tgt_address_point = AddressPoint(target_address)
    emp_coords = {k: cartesian_coordinates(p, tgt_address_point, tgt_address_point.latitude)
                  for k, p in emp_address_dict.items()}
    groups = group_employees(emp_coords, max_pass)
    res = []
    for g in groups:
        opt_g = optimise_group(g)
        for sub_g in opt_g:
            res.append(sub_g)
    return res


def optimise_group(cur_group):
    """
    check if cur_group needs to be split further
    for each sub_group, reorder from furthest to closest to target address
    :param cur_group:
    :return: a list of lists of strings (addresses)
    """
    return [cur_group]


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



