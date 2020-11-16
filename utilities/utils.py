import math
import numpy as np
import requests


def get_employee_data(file_path):
    '''
    :param file_path:
    :return: list of employee data. each element of the list is a list [first_name, last_name, address]
    '''
    with open(file_path, 'r') as f:
        employee_info = f.readlines()
    employee_info = [emp[:-1] for emp in employee_info[1:]]
    employee_info = [emp.split(';') for emp in employee_info]
    return employee_info


def get_route_distance(location_a, location_b):
    '''
    uses OSRM API to calculate 'car' distance between two points
    result returned in km
    :param location_a:
    :param location_b:
    :return:
    '''
    api_base_str = 'http://router.project-osrm.org/route/v1/driving/'
    getStr = '{}/{},{};{},{}?overview=false'.format(api_base_str, location_a.longitude, location_a.latitude,
                                                    location_b.longitude, location_b.latitude)
    optRoute = requests.get(getStr)
    return optRoute.json()['routes'][0]['distance'] / 1000.0


def get_employees_distance_matrix(employee_locs):
    '''
    :param employee_locs:
    :return:
    '''

    num_emp = len(employee_locs)
    dist = np.ndarray((num_emp, num_emp))
    for i in range(num_emp):
        loc_i = employee_locs[i]
        dist[i, i] = 0
        for j in range(i+1, num_emp):
            loc_j = employee_locs[j]
            dist[i, j] = get_route_distance(loc_i, loc_j)
            dist[j, i] = dist[i, j]
    return dist


def get_employees_distance_to_target(employee_locs, target_loc):
    '''
    :param employee_locs:
    :param target_loc:
    :return: distance vector of each employee to target_location
    '''
    num_emp = len(employee_locs)
    dist = np.empty(num_emp)
    for i in range(num_emp):
        loc_i = employee_locs[i]
        dist[i] = get_route_distance(loc_i, target_loc)
    return dist


def deg_to_rad(deg_angle):
    return deg_angle * math.pi/180.0


def cartesian_coordinates(location_i, central_location, base_latitude):
    '''
    converts latitude/longitude data points to cartesian coordinates
    using equirectangular projection
    :param location_i: (.longitude, .latitude): the point for which we want the coordinates
    :param central_location: (.longitude, .latitude): center of the map
    :param base_latitude: (double): the latitude at which projected distances are preserved
    :return:
    '''
    R = 6371

    x = R * deg_to_rad(location_i.longitude - central_location.longitude) * math.cos(deg_to_rad(base_latitude))
    y = R * deg_to_rad(location_i.latitude - central_location.latitude)

    return x, y
