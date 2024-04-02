from enum import Enum, auto

class SpecialTypes(Enum):
    PERSON_EMAIL = auto()
    PERSON_FIRST_NAME = auto()
    PERSON_LAST_NAME = auto()
    PERSON_NAME = auto()
    COUNTRY_ID = auto()
    COUNTRY_LAT = auto()
    COUNTRY_LON = auto()
    COUNTRY_NAME = auto()
    USA_STATE_CODE = auto()
    USA_STATE_NAME = auto()
    SKILLS = auto()
    UNIVERSITIES = auto()
    IP_ADDRESS = auto()
    
    def get_normal_type(self):
        if self in [SpecialTypes.COUNTRY_LAT, SpecialTypes.COUNTRY_LON]:
            return 'float'
        else:
            return 'text'

    def has_matching_normal_type(self, normal_type):
        return normal_type == self.get_normal_type()
    
    def convert_to_normal_type(self, data):
        if self in [SpecialTypes.COUNTRY_LAT, SpecialTypes.COUNTRY_LON]:
            return float(data)
        else:
            return data