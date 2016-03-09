""" Main (for now) module for EveRouter """

import csv
import itertools
from io import StringIO
import re
try:
    import readline
except ImportError:
    import pyreadline as readline

from colorama import init, deinit, Fore, Style
from model.EveDB import EveDB
from model.Map import SolarMap

def dict_from_csvqfile(file_path):
    """Creates dictionary from a csv file"""
    reader = None
    csv_file = open(file_path)
    text = csv_file.read()
    stri = StringIO(text)
    reader = csv.reader(stri, delimiter=';')
    return reader



def print_route(finished_route, sys_desc):
    """Iterate through route, printing each system. Colour depends on sec status"""
    print("%d jumps:" % (len(finished_route)-1), end="")
    for system_id in finished_route:
        system_sec_status = sys_desc[system_id][2]
        color = Fore.CYAN
        if system_sec_status < 1.0:
            color = Fore.GREEN
        if system_sec_status < 0.5:
            color = Fore.YELLOW
        if system_sec_status < 0.1:
            color = Fore.RED
        print(EveDB.id2name(sys_desc, system_id) + "(", end="")
        print(color + Style.BRIGHT +  "%.1f" % (sys_desc[system_id][2]) +  Style.RESET_ALL, end="")
        print(") -> ", end="")

    print("DONE")


def get_input(system_desc):
    def completer(text, state):
        """Autocomplete system names"""
        options = [system_desc[x][0] for x in system_desc if re.match(text, system_desc[x][0], re.I)]
        try:
            return options[state]
        except IndexError:
            return None

    readline.set_completer(completer)

    readline.set_completer_delims(readline.get_completer_delims() + ",")
    readline.parse_and_bind("tab: complete")

    inp = input("Start> ")
    start_system = EveDB.name2id(system_desc, str(inp.strip()))
    inp = input("Dest> ")
    dest_system = EveDB.name2id(system_desc, str(inp.strip()))
    inp = input("Avoid> ")

    readline.set_completer(None)
    return [start_system, dest_system, inp]

def main():
    """Run the route finder"""
    init()
    print("Eve Route finder")

    gates = [[int(rows[0]), int(rows[1])] for rows in dict_from_csvqfile("resources/database/system_jumps.csv")]
    system_desc = {
        int(rows[0]): [rows[1], rows[2], float(rows[3])]
        for rows in dict_from_csvqfile("resources/database/system_description.csv")
    }

    eve_db = EveDB(gates, system_desc)
    solar_map = eve_db.get_solar_map()

    user_input = get_input(system_desc)
    avoid_sys = user_input[2].split(",")
    avoid_list = []
    for system_name in avoid_sys:
        avoid_list.append(EveDB.name2id(system_desc, str(system_name.strip())))


    counter = itertools.count()
    solar_map.build_list(counter)

    print()
    route = solar_map.djikstra(user_input[0], user_input[1], avoid_list, SolarMap.PREFER_SHORTER, 50, counter)
    print_route(route, system_desc)
    print()
    route = solar_map.djikstra(user_input[0], user_input[1], avoid_list, SolarMap.PREFER_SAFER, 50, counter)
    print_route(route, system_desc)
    print()
    route = solar_map.djikstra(user_input[0], user_input[1], avoid_list, SolarMap.PREFER_DANGEROUS, 100, counter)
    print_route(route, system_desc)

    deinit()


if __name__ == "__main__":
    main()
