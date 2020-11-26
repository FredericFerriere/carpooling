import time

from optimiser import *


async def main():
    stime = time.time()
    address_file_path = './data/addresses.csv'
    target_address = '9 Boulevard Decouz, 74000 Annecy France'
    max_pass = 4

    employee_data = get_employee_data(address_file_path)
    print('number of employees: {}'.format(len(employee_data)))
    employee_addresses = [emp[2] for emp in employee_data]

    tgt_point = AddressPoint(target_address)
    print('retrieving GPS coordinates...')
    emp_points = {emp_address: AddressPoint(emp_address) for emp_address in employee_addresses}
    print('retrieving GPS coordinates Done')
    emp_coords = {k: cartesian_coordinates(p, tgt_point, tgt_point.latitude) for k, p in emp_points.items()}
    init_groups = group_employees(emp_coords, max_pass)
    print('initial grouping done')
    print('optimising initial grouping...')
    fin_groups = []
    for g in init_groups:
        fin_groups += await optimise_group_async(g, emp_points, tgt_point)
    etime = time.time()
    ftime = etime - stime
    print('Processing finished in {:.2f} s\n'.format(ftime))
    print_main_statistics(fin_groups)


def print_main_statistics(groups):
    numEmps = sum([len(g[0]) for g in groups])
    numGroups = len(groups)
    indDistance = sum([g[1] for g in groups])
    optDistance = sum([g[2] for g in groups])

    print('number of employees: {}'.format(numEmps))
    print('number of groups: {}'.format(numGroups))
    print('Sum of individual distances: {:.1f} km'.format(indDistance))
    print('Total optimised distance: {:.1f} km'.format(optDistance))
    print('Distance saved (km): {:.1f}'.format(indDistance-optDistance))


if __name__ == '__main__':
    asyncio.run(main())
