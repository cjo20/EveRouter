"""Store information related to Eve world """
import re
from model.Map import SolarMap

class EveDB:

    def __init__(self, gates, system_desc):
        self.init = True
        self.gates = gates
        self.system_desc = system_desc

    @staticmethod
    def name2id(sys_desc, name):
        """Converts text system name to ID"""
        for key, value in sys_desc.items():
            if re.match(value[0], name, re.I):
                return key
        return None

    @staticmethod
    def id2name(sys_desc, system_id):
        """Converts system ID to text name"""
        try:
            sys_name = sys_desc[system_id][0]
        except KeyError:
            sys_name = None
        return sys_name

    def get_solar_map(self):
        """Build a solar map by creating a list of connections"""
        solar_map = SolarMap()

        for system_id in self.system_desc:
            sec_status = max(self.system_desc[system_id][2], 0.0)
            solar_map.add_system(system_id, sec_status)

        for gate in self.gates:
            solar_map.add_connection(gate[0], gate[1])

        return solar_map