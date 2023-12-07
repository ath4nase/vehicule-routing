import json
import math
from operator import attrgetter
from re import DEBUG
import numpy as np

DEBUG = False


class Location:
    id = -1
    visit_interval = 0
    x = 0
    y = 0
    value = 0


class Instance:

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
            is_feasible = (
                (number_of_duplicates == 0)
                and (on_time)
                and 0 not in locations)
            print(f"Number of duplicates: {number_of_duplicates}")
            print(f"On time: {on_time}")
            print(f"Feasible: {is_feasible}")
            print(f"Cost: {total_cost}")
            return (is_feasible, total_cost)


def dynamic_programming(instance):
    if instance.locations == []:
        return []
    depot = instance.locations[0]
    depot.visit_interval = [0, 0]
    listClient = instance.locations
    nbClient = len(instance.locations)
    orderedLocation = sorted(
        listClient, key=attrgetter('visit_interval'))
    if DEBUG:
        print("--Loc--")
        for i in instance.locations:
            print(i.visit_interval)
        print("--SortedLoc--")
        for i in orderedLocation:
            print(i.visit_interval)
        print("duration = ", instance.duration(7, 2))
    c = np.zeros((nbClient, nbClient), dtype=object)
    for i in range(nbClient):
        for j in range(nbClient):
            if i == 0 or j == 0:
                c[i][j] = (0, [], 0)
            else:
                prevLocation = c[i][j-1][1]
                if prevLocation == []:
                    prevLocation = 0
                else:
                    prevLocation = c[i][j-1][1][-1]
                if orderedLocation[i].visit_interval[0] >= (c[i][j-1][2]+instance.duration(prevLocation, orderedLocation[i].id)):
                    tpath = c[i][j-1][1].copy()
                    tpath.append(orderedLocation[i].id)
                    c[i][j] = min(c[i-1][j], (path_cost(tpath, instance), tpath,
                                  instance.locations[tpath[-1]].visit_interval[1]),
                                  (0, [], 0), key=lambda a: a[0])
                else:
                    c[i][j] = c[i][j-1]
    print("chosen path = ", c[-1][-1][1])
    print("total cost = ", c[-1][-1][0])
    return c[-1][-1][1]


# give the total cost of a given path in the graph
def path_cost(id_list, instance):
    if len(id_list) == 0:
        return 0
    total_cost = instance.cost(0, id_list[0])
    for i in range(len(id_list)-1):
        total_cost += instance.cost(id_list[i], id_list[i+1])
    total_cost += instance.cost(id_list[-1], 0)
    return total_cost


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
