import math
import numpy as np
import requests
from geopy.geocoders import Nominatim
from geopy.geocoders import BANFrance
import aiohttp
import asyncio

from aiohttp import ClientSession

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


def get_latitude_longitude(str_address):
    #geolocator = Nominatim(user_agent="covoiturage")
    geolocator = BANFrance()
    location = geolocator.geocode(str_address)
    if location is None:
        res = None, None
    else:
        res = location.latitude, location.longitude
    return res


async def get_route_distance_optimised(address_point_a, address_point_b, session):
    '''
    uses OSRM API to calculate 'car' distance between two points
    result returned in km
    :param address_point_a:
    :param address_point_b:
    :param session:
    :return:
    '''

    api_base_str = 'http://router.project-osrm.org/route/v1/driving/'
    getStr = '{}/{},{};{},{}?overview=false'.format(api_base_str, address_point_a.longitude, address_point_a.latitude,
                                                    address_point_b.longitude, address_point_b.latitude)

    optRoute = await session.request(method='GET', url=getStr)
    optRoute_json = await optRoute.json()

    return optRoute_json['routes'][0]['distance'] / 1000.0


async def get_employees_distance_to_target_optimised(employee_points, target_point):
    '''
    :param employee_points:
    :param target_point:
    :return:
    '''
    emp_list = list(employee_points.keys())
    async with ClientSession() as session:
        ret_list = await asyncio.gather(
            *[get_route_distance_optimised(employee_points[emp], target_point, session) for emp in emp_list])
    dist = {emp_list[k]: ret_list[k] for k in range(len(emp_list))}
    return dist


async def get_employees_distance_matrix_optimised(employee_points):
    adds = list(employee_points.keys())
    num_emp = len(adds)
    # print(num_emp)
    dist = np.ndarray((num_emp, num_emp))
    async with ClientSession() as session:
        ret_list = await asyncio.gather(
            *[get_route_distance_optimised(employee_points[adds[i]], employee_points[adds[j]], session) for i in
              range(num_emp - 1) for j in range(i + 1, num_emp)])
        # print(len(ret_list))
    count = 0
    for i in range(num_emp):
        dist[i, i] = 0
        for j in range(i + 1, num_emp):
            ind = int(i * (num_emp - 1 - 0.5 * (i - 1)) + j - i - 1)
            # print('i: {}, j: {}, count: {}, ind: {}'.format(i,j, count, ind))
            dist[i, j] = ret_list[ind]
            dist[j, i] = dist[i, j]
            count += 1
    res = {adds[i]: {adds[j]: dist[i, j] for j in range(num_emp)} for i in range(num_emp)}
    return res


def get_route_distance(address_point_a, address_point_b):
    '''
    uses OSRM API to calculate 'car' distance between two points
    result returned in km
    :param address_point_a:
    :param address_point_b:
    :return:
    '''
    api_base_str = 'http://router.project-osrm.org/route/v1/driving/'
    getStr = '{}/{},{};{},{}?overview=false'.format(api_base_str, address_point_a.longitude, address_point_a.latitude,
                                                    address_point_b.longitude, address_point_b.latitude)
    optRoute = requests.get(getStr)
    return optRoute.json()['routes'][0]['distance'] / 1000.0


def get_employees_distance_matrix(employee_points):
    '''
    :param employee_points:
    :return:
    '''
    adds = list(employee_points.keys())
    num_emp = len(adds)
    dist = np.ndarray((num_emp, num_emp))
    for i in range(num_emp):
        loc_i = employee_points[adds[i]]
        dist[i, i] = 0
        for j in range(i+1, num_emp):
            loc_j = employee_points[adds[j]]
            dist[i, j] = get_route_distance(loc_i, loc_j)
            dist[j, i] = dist[i, j]
    res = {adds[i]: {adds[j]: dist[i, j] for j in range(num_emp)} for i in range(num_emp)}
    return res


def get_employees_distance_to_target(employee_points, target_point):
    '''
    :param employee_points:
    :param target_point:
    :return:
    '''
    dist = {k: get_route_distance(emp, target_point) for k, emp in employee_points.items()}
    return dist


def deg_to_rad(deg_angle):
    return deg_angle * math.pi/180.0


def rad_to_deg(rad_angle):
    return rad_angle * 180/math.pi


def cartesian_coordinates(point, central_point, base_latitude):
    '''
    converts latitude/longitude data points to cartesian coordinates
    using equirectangular projection
    :param point: (.longitude, .latitude): the point for which we want the coordinates
    :param central_point: (.longitude, .latitude): center of the map
    :param base_latitude: (double): the latitude at which projected distances are preserved
    :return:
    '''
    R = 6371

    x = R * deg_to_rad(point.longitude - central_point.longitude) * math.cos(deg_to_rad(base_latitude))
    y = R * deg_to_rad(point.latitude - central_point.latitude)

    return x, y


def latitude_longitude_from_cartesians(x, y, central_point, base_latitude):
    R = 6371
    longitude = rad_to_deg(x / (R * math.cos(deg_to_rad(base_latitude)))) + central_point.longitude
    latitude = rad_to_deg(y / R) + central_point.latitude
    return latitude, longitude


def path_distance(path, emp_dist_mat, tgt_dist_mat):
    # path expected to be sorted from closest to furthest to target.
    dist = tgt_dist_mat[path[0]]
    for i in range(len(path)-1):
        dist += emp_dist_mat[path[i]][path[i+1]]
    return dist
