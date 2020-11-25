from utilities.utils import *


class AddressPoint:
    def __init__(self, s_address):
        self.str_address = s_address
        self.latitude, self.longitude = get_latitude_longitude(s_address)




