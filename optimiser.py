import numpy as np
from sklearn.cluster import KMeans


def optimise_routes(employee_carts, target_cart, max_pass):
    groups = group_employees(employee_carts, max_pass)
    res = []
    for g in groups:
        opt_g = optimise_single_route(g, target_cart)
        res.append(opt_g)

    return res


def optimise_single_route(group, target_cart):
    
    return group



def group_employees(employee_carts, max_pass):
    '''
    :param employee_carts: employees' cartesian coordinates
    :param max_pass: maximum number of passengers in a car
    :return: a list of employee groups. Each element in the list is a list of employee coordinates
    '''
    # starting from full list, divide list using k-means with k = 2
    # apply iteratively to each element (itself a list) obtained until number of employees in each list <= max_pass
    cur_list = [[emp for emp in employee_carts]]
    cur_max = len(employee_carts)
    while cur_max > max_pass:
        new_list = []
        for sub_list in cur_list:
            if len(sub_list) > max_pass:
                kmeans = KMeans(n_clusters=2, random_state=4679).fit(np.array(sub_list))
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



