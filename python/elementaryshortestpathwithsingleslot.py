import json
import math

INF = 10000000

class Location:
    id = -1
    visit_interval: list[int]
    x = 0
    y = 0
    value = 0

    def depot():
        depot = Location()
        depot.visit_interval = [-INF, INF]
        return depot
    
    def get_beginning(self):
        return self.visit_interval[0]
    def get_end(self):
        return self.visit_interval[1]


class Instance:

    locations : list[Location]

    def __init__(self, filepath=None):
        self.locations = []
        if filepath is not None:
            with open(filepath) as json_file:
                data = json.load(json_file)
                locations = zip(
                        data["visit_intervals"],
                        data["xs"],
                        data["ys"],
                        data["values"])
                for (intervals, x, y, value) in locations:
                    self.add_location(intervals[0], x, y, value)

    def add_location(self, visit_interval, x, y, value):
        location = Location()
        location.id = len(self.locations)
        location.visit_interval = visit_interval
        location.x = x
        location.y = y
        location.value = value
        self.locations.append(location)

    def duration(self, location_id_1, location_id_2):
        xd = self.locations[location_id_2].x - self.locations[location_id_1].x
        yd = self.locations[location_id_2].y - self.locations[location_id_1].y
        d = round(math.sqrt(xd * xd + yd * yd))
        return d

    def cost(self, location_id_1, location_id_2):
        xd = self.locations[location_id_2].x - self.locations[location_id_1].x
        yd = self.locations[location_id_2].y - self.locations[location_id_1].y
        d = round(math.sqrt(xd * xd + yd * yd))
        return d - self.locations[location_id_2].value

    def write(self, filepath):
        data = {"visit_intervals": [location.visit_intervals
                                    for location in self.locations],
                "xs": [location.x for location in self.locations],
                "ys": [location.y for location in self.locations],
                "values": [location.value for location in self.locations]}
        with open(filepath, 'w') as json_file:
            json.dump(data, json_file)

    def check(self, filepath):
        print("Checker")
        print("-------")
        with open(filepath) as json_file:
            data = json.load(json_file)
            locations = data["locations"]
            on_time = True
            total_cost = 0
            current_time = -math.inf
            location_pred_id = 0
            if (len(locations) > 0):
                for location_id in data["locations"]:
                    location = self.locations[location_id]
                    t = current_time + self.duration(location_pred_id, location_id)
                    if t <= location.visit_interval[0]:
                        current_time = location.visit_interval[1]
                    else:
                        on_time = False
                    total_cost += self.cost(location_pred_id, location_id)
                    location_pred_id = location_id
                total_cost += self.cost(location_pred_id, 0)
                number_of_duplicates = len(locations) - len(set(locations))
            else :
                number_of_duplicates = 0
            is_feasible = (
                    (number_of_duplicates == 0)
                    and (on_time)
                    and 0 not in locations)
            print(f"Number of duplicates: {number_of_duplicates}")
            print(f"On time: {on_time}")
            print(f"Feasible: {is_feasible}")
            print(f"Cost: {total_cost}")
            return (is_feasible, total_cost)
        
    def time_range(self):
        max = 0
        for location in self.locations :
            if location.visit_interval[1] > max :
                max = location.get_end()
        return max

def dynamic_programming(instance:Instance):
    depot = Location.depot()
    listClient = [v for v in instance.locations][1:]
    nbClient = len(listClient)
    # TODO START
    min_path_values = [instance.cost(0, listClient[i].id) for i in range (nbClient)]
    predecessor = [None for _ in range(nbClient)]
    visited_clients = [{} for _ in range(nbClient)]
    previous_visited_clients = [v for v in visited_clients]
    previous_values = [v for v in min_path_values]

    # computing minimal path from depot for all clients
    # if values doesn't change, finished. |V|-1 iteration at most
    while(True): 
        previous_values = [v for v in min_path_values]
        previous_visited_clients = [v for v in visited_clients]
        for i in range(nbClient):
            for j in range(nbClient):
                if feasible_and_improve(listClient[i].id, listClient[j].id, previous_values, min_path_values, previous_visited_clients):
                    predecessor[j] = i
                    min_path_values[j] =  previous_values[i] + instance.cost(listClient[i].id, listClient[j].id)
                    visited_clients[j] = {i}.union(previous_visited_clients[i])
        if min_path_values == previous_values:
            break
    if (nbClient == 0):
        return []
    # then pick best cycle by adding the edge (u, depot) to the shortest path (depot, u)
    best_path_end = min([(i, min_path_values[i] + instance.cost(listClient[i].id, 0)) for i in range(nbClient)], key= lambda a : a[1])
    current = best_path_end[0]
    res : list[Location] = []
    while current != None:
        res.append(listClient[current].id)
        current = predecessor[current]
    
    res.reverse()
    # TODO END
    return res

def feasible_and_improve(i, j, old_values, new_values, visited):
    feasible = i != j and (i == 0 or instance.locations[i].visit_interval[1] + instance.duration(i, j) <= instance.locations[j].visit_interval[0])
    elementary = not j in visited[i-1]
    improved = old_values[i-1] + instance.cost(i, j) < new_values[j-1]
    return feasible and elementary and improved

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
            "-a", "--algorithm",
            type=str,
            default="dynamic_programming",
            help='')
    parser.add_argument(
            "-i", "--instance",
            type=str,
            help='')
    parser.add_argument(
            "-c", "--certificate",
            type=str,
            default=None,
            help='')

    args = parser.parse_args()

    if args.algorithm == "dynamic_programming":
        instance = Instance(args.instance)
        solution = []
        if (len(instance.locations)>1):
            solution = dynamic_programming(instance)
        if args.certificate is not None:
            data = {"locations": solution}
            with open(args.certificate, 'w') as json_file:
                json.dump(data, json_file)
            print()
            instance.check(args.certificate)

    elif args.algorithm == "checker":
        instance = Instance(args.instance)
        instance.check(args.certificate)
