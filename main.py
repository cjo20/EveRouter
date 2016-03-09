from model.Map import SolarMap
import csv
from colorama import init, deinit, Fore, Style
from io import StringIO
import re
try:
	import readline
except:
	import pyreadline as readline
import time
import itertools
init()
class bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def dict_from_csvqfile(file_path):
	reader = None
	f = open(file_path)
	text = f.read()
	stri = StringIO(text)
	reader = csv.reader(stri, delimiter=';')
	return reader

def name2id(sys_desc, name):
	for key, value in sys_desc.items():
		if re.match(value[0],name, re.I):
			return key
	return None

def id2name(sys_desc, id):
	try:
		sys_name = sys_desc[id][0]
	except KeyError:
		sys_name = None
	return sys_name

def print_route(route, sys_desc):
	print("%d jumps:" % (len(route)-1), end="")
	for x in route:
		sec_status = sys_desc[x][2]
		color = Fore.CYAN
		if sec_status < 1.0:
			color = Fore.GREEN
		if sec_status < 0.5:
			color = Fore.YELLOW
		if sec_status < 0.1:
			color = Fore.RED
		print(id2name(sys_desc, x) + "(" + color + Style.BRIGHT +  "%.1f" % (sys_desc[x][2]) +  Style.RESET_ALL + ") -> " , end="")

	print("DONE")

print("Eve Route finder")

gates = [[int(rows[0]), int(rows[1])] for rows in dict_from_csvqfile("resources/database/system_jumps.csv")]
system_desc = {
 			int(rows[0]): [rows[1], rows[2], float(rows[3])]
            for rows in dict_from_csvqfile("resources/database/system_description.csv")
        }

solar_map = SolarMap()



def completer(text, state):
	options = [system_desc[x][0] for x in system_desc if re.match(text, system_desc[x][0], re.I)]
	try:
		return options[state]
	except IndexError:
		return None

readline.set_completer(completer)
readline.parse_and_bind("tab: complete")

for x in system_desc:
	sec_status = max(system_desc[x][2], 0.0)
	solar_map.add_system(x, sec_status)

for x in gates:
	solar_map.add_connection(x[0], x[1])

inp = input("Start> ")
start_system = name2id(system_desc, str(inp.strip()))
inp = input("Dest> ")
dest_system = name2id(system_desc, str(inp.strip()))
inp = input("Avoid> ")
avoid_sys = inp.split(",")
avoid_list = []
for x in avoid_sys:
	avoid_list.append(name2id(system_desc, str(x.strip())))
#jita_id = name2id(system_desc,  str(sys.argv[2]))

counter = itertools.count()
solar_map.build_list(counter)
print("\nPrefer Shorter:")
start_time = time.time()
route = solar_map.djikstra(start_system,dest_system, avoid_list, SolarMap.PREFER_SHORTER, 50, counter)
stop_time = time.time()
print("--- %.3f ms ---" % ((stop_time - start_time) * 1000))
print_route(route, system_desc)


# import profile
# profile.run('solar_map.djikstra(start_system,dest_system, avoid_list, SolarMap.PREFER_SHORTER, 50, counter)', 'profile.tmp')
# import pstats
# p = pstats.Stats('profile.tmp')
# p.sort_stats('cumulative').print_stats(20)

#print("Prefer Shorter avoiding Niarja:")
#route = solar_map.shortest_path(start_system,dest_system, {name2id(system_desc, "Niarja")}, SolarMap.PREFER_SHORTER, 50)
#print_route(route, system_desc)


print("\nPrefer Safer:")
start_time = time.time()
route = solar_map.djikstra(start_system,dest_system, avoid_list, SolarMap.PREFER_SAFER, 50, counter)
stop_time = time.time()
print("--- %.3f ms ---" % ((stop_time - start_time) * 1000))
print_route(route, system_desc)


# print("Prefer Safer avoiding Uedama:")
# 
# for i in range(0, 100, 5):
	# print("sec_weight: %d " %i, end="")
	# route = solar_map.djikstra(start_system,dest_system, {name2id(system_desc, "Uedama")}, SolarMap.PREFER_SAFER, i)
	# print_route(route, system_desc)

print("\nPrefer Dangerous:")
start_time = time.time()
route = solar_map.djikstra(start_system,dest_system, avoid_list, SolarMap.PREFER_DANGEROUS, 100, counter)
print("--- %.3f ms ---" % ((time.time() - start_time) * 1000))
print_route(route, system_desc)


#print("Prefer Dangerous avoiding Old Man Star:")
#route = solar_map.shortest_path(start_system,dest_system, {name2id(system_desc, "Old Man Star")}, SolarMap.PREFER_DANGEROUS, 10)
#print_route(route, system_desc)

deinit()