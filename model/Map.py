from queue import PriorityQueue
import heapq
import sys

class CustomPriorityQueue(object):

	def __init__(self, counter, my_heap=[]):
		heapq.heapify(my_heap)
		self.heap = my_heap
		self.entry_finder = dict({i[-1]: i for i in my_heap})
		self.REMOVED = '<remove_marker>'
		self.counter = counter

	def insert(self, node, priority=0):
		if node in self.entry_finder:
			self.delete(node)
		count = next(self.counter)
		entry = (priority, count, node)
		self.entry_finder[node] = entry
		heapq.heappush(self.heap, entry)

	def delete(self, node):
		entry = self.entry_finder[node]
		self.entry_finder[node] = (entry[0], entry[1], self.REMOVED)
		#entry[-1] = self.REMOVED
		return entry[0]

	def pop(self):
		while self.heap:
			priority, count, node = heapq.heappop(self.heap)
			if node is not self.REMOVED:
				del self.entry_finder[node]
				return priority, node
		raise KeyError('pop from an empty priority queue')

	def check(self, node):
		return (self.entry_finder[node])[0]

class SolarSystem:
	def __init__(self, key, sec_status):
		self.id = key;
		self.connected_to =  {}
		self.sec_status = sec_status;

	def add_neighbour(self, neighbour):
		self.connected_to[neighbour] = neighbour.sec_status;

	def get_connections(self):
		return self.connected_to.keys()

	def get_id(self):
		return self.id

	def get_weight(self, neighbour):
		return self.connected_to[neighbour]



class SolarMap:

	PREFER_SHORTER = 0
	PREFER_SAFER = 1
	PREFER_DANGEROUS = 2

	counter = 0
	def __init__(self):
		self.systems_list = {}
		self.total_systems = 0

	def add_system(self, key, sec_status):
		self.total_systems += 1
		new_system = SolarSystem(key, sec_status)
		self.systems_list[key] = new_system
		return new_system

	def get_system(self, key):
		if key in self.systems_list:
			return self.systems_list[key]
		else:
			return None

	def get_all_systems(self):
		return self.systems_list.keys()

	def add_connection(self, source, destination):
		if source not in self.systems_list:
			self.add_system(source)
		if destination not in self.systems_list:
			self.add_system(destination)

		self.systems_list[source].add_neighbour(self.systems_list[destination])
		self.systems_list[destination].add_neighbour(self.systems_list[source])

	def __contains__(self, item):
		return item in self.systems_list

	def __iter__(self):
		return iter(self.systems_list.values())

	def calculate_weight(self, source, neighbour, method, sec_penalty):
		weight = source.get_weight(neighbour)
		if method == SolarMap.PREFER_SHORTER:
			if weight != None:
				return 1.0
			else:
				return None
		elif method == SolarMap.PREFER_SAFER:
			if weight >= 0.5:
				return 1.0
			else:
				return 1.0 * sec_penalty
		elif method == SolarMap.PREFER_DANGEROUS:
			if weight < 0.5:
				return 1.0
			else:
				return 1.0 * sec_penalty

	def build_list(self, counter):
		self.queue_list = [( sys.float_info.max, next(counter), v) for v in self.get_all_systems()]

#	def calculate_weight(self, source, neighbour, method):
#		if method == SolarMap.PREFER_SHORTER:
#			if source.get_weight(neighbour) != None:
#				return 1.0
#			else:
#				return None
#		elif method == SolarMap.PREFER_SAFER:
#			return 1.1 - source.get_weight(neighbour)
#		elif method == SolarMap.PREFER_DANGEROUS:
#			return 0.1 + source.get_weight(neighbour)

	def shortest_path(self, source, destination, avoidance_list, method, sec_penalty):
		path = []
		weight = 0.0
		if source in self.systems_list and destination in self.systems_list:
			if source == destination:
				path = [source]
			else:
				queue = PriorityQueue()

				visited = set([self.get_system(x) for x in avoidance_list])
				parent = {}

				#Starting point
				root = self.get_system(source)
				queue.put((0, self.counter, root))
				self.counter += 1
				visited.add(root)

				while not queue.empty():
					[weight, id, current_sys] = queue.get()

					if current_sys.get_id() == destination:
						path.append(destination)

						while True:
							parent_id = parent[current_sys].get_id()
							path.append(parent_id)

							if parent_id != source:
								current_sys = parent[current_sys]
							else:
								path.reverse()
								return path
					else:
						for neighbour in [x for x in current_sys.get_connections() if x not in visited]:
							weight = self.calculate_weight(current_sys, neighbour, method, sec_penalty)
							parent[neighbour] = current_sys
							visited.add(neighbour)
							queue.put((weight, self.counter, neighbour))
							self.counter += 1

		self.counter = 0
		return path


	def djikstra(self, source, destination, avoidance_list, method, sec_penalty, counter):
		
		#my_heap = [( sys.float_info.max, next(counter), v) for v in self.get_all_systems()]
		my_heap = list(self.queue_list)
		queue = CustomPriorityQueue(counter, my_heap)
		#for v in self.get_all_systems():
			#queue.insert(v, sys.float_info.max)

		processed = {}
		parent = {}
		visited = set([self.get_system(x) for x in avoidance_list])
		
		size = len(queue.heap)
		queue.delete(source)
		queue.insert(source, 0)


		while (size > len(visited)):

			uv = queue.pop()
			current = uv[1]
			distance = uv[0]

			current_sys = self.get_system(current)
			visited.add(current_sys)

			if current == destination:
				break

			#if self.get_system(current).sec_status < 0.5:
			#	destination = current
			#	break

			for neighbour in [x for x in current_sys.get_connections() if x not in visited]:
				#if neighbour in visited:
				#	continue
				neighbour_id = neighbour.get_id()
				new_dist = distance + self.calculate_weight(current_sys, neighbour, method, sec_penalty)
				old_dist = queue.check(neighbour_id)

				if new_dist < old_dist:
					queue.delete(neighbour_id)
					queue.insert(neighbour_id, new_dist)
					parent[neighbour] = current_sys
		
		path = []
		path.append(destination)
		current_sys = self.get_system(destination);
		while True:
			parent_id = parent[current_sys].get_id()
			path.append(parent_id)
			if parent_id != source:
				current_sys = parent[current_sys]
			else:
				path.reverse()
				return path
		return path




