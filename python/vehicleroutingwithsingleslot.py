import json
import math
from operator import attrgetter
import columngenerationsolverpy
import numpy as np

DEBUG = True

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
        
    def time_range(self):
        max = 0
        for location in self.locations :
            if location.visit_interval[1] > max :
                max = location.get_end()
        return max


class PricingSolver:

    def __init__(self, instance):
        self.instance = instance
        # TODO START
        self.already_visited : list[Location] = None
        # TODO END

    def initialize_pricing(self, columns, fixed_columns):
        # TODO START
        self.already_visited = [0 for _ in range(len(instance.locations))]
        self.already_visited[0] = 1
        for column_id, column_value in fixed_columns:
            column = columns[column_id]
            for row_index, row_coefficient in zip(column.row_indices, column.row_coefficients):
                self.already_visited[row_index] += column_value*row_coefficient
        # TODO END

    def solve_pricing(self, duals):
        # Build subproblem instance.
        # TODO START
        depot : Location = instance.locations[0]
        depot.visit_interval = [0, 0]
        listClient  : list[Location]= instance.locations
        nbClient = len(instance.locations)
        orderedLocation = sorted(
            listClient, key=attrgetter('visit_interval'))
        # TODO END

        # Solve subproblem instance.
        # TODO START
    ################################################
        if DEBUG:
            for i in range(len(listClient)):
                for j in range(len(listClient)):
                    if i != j:
                        print(instance.cost(i, j), end=" ")
                    else:
                        print(0, end=" ")
                print("")
            print("----------------------")
            for i in range(len(listClient)):
                for j in range(len(listClient)):
                    if i != j:
                        print(instance.duration(i, j), end=" ")
                    else:
                        print(0, end=" ")
                print("")

            print("--Loc--")
            for i in instance.locations:
                print(i.visit_interval)
            print("--SortedLoc--")
            for i in orderedLocation:
                print(i.visit_interval)
    ################################################

        c = np.zeros((nbClient, nbClient), dtype=object)
        for k in range(nbClient):
            for l in range(nbClient):
                if l == 0 or k == 0:
                    c[k][l] = (0, [])
                else:
                    temp = []
                    for kp in range(0, k):
                        for lp in range(0, kp+1):
                            path = c[kp][lp][1].copy()
                            if lp == l:
                                cost = c[kp][lp][0]
                            else:
                                cost = c[kp][lp][0]+reducedcostIdToId(lp, l, orderedLocation, duals) + reducedcostToDepot(
                                    l, orderedLocation, duals)-reducedcostToDepot(lp, orderedLocation, duals)
                            if path == []:
                                path.append(orderedLocation[l].id)
                            if path[-1] != orderedLocation[l].id:
                                path.append(orderedLocation[l].id)
                            if instance.duration(orderedLocation[lp].id, orderedLocation[l].id)+instance.locations[orderedLocation[lp].id].visit_interval[1] < instance.locations[orderedLocation[l].id].visit_interval[0]:
                                temp.append((cost, path))
                            else:
                                temp.append((0, []))
                    # print("k = ", k, " l = ", l, " temp", temp)
                    c[k][l] = (min(temp, key=lambda a: a[0]))
        if DEBUG:
            print("-------------------------------------")
            print(c)
        res : list[Location]= [instance.locations[i]for i in min(c[-1], key= lambda a: a[0])[1]]
        print ([loc.id for loc in res])
        # TODO END

        # Retrieve column.
        column = columngenerationsolverpy.Column()
        # TODO START
        column.objective_coefficient = 0
        if res == []:
            return [column]
        u = depot
        for i in range(len(res)):
            v = res[i]
            column.row_indices.append(len(orderedLocation)*u.id + v.id)
            column.row_coefficients.append(1)
            column.objective_coefficient += instance.cost(u.id, v.id)
            u = v
        column.row_indices.append(len(orderedLocation)*v.id + depot.id)
        column.row_coefficients.append(1)
        column.objective_coefficient += instance.cost(v.id, depot.id)
        # TODO END

        return [column]


def reducedcostIdToId(ordered_id1, ordered_id2, orderedLocation, duals):
    if ordered_id1 == 0 and ordered_id2 == 0:
        return 0
    return instance.cost(orderedLocation[ordered_id1].id, orderedLocation[ordered_id2].id) - .5*(duals[ordered_id1-1] - duals[ordered_id2-1])


def reducedcostToDepot(ordered_id1, orderedLocation, duals):
    if ordered_id1 == 0:
        return 0 - duals[ordered_id1 -1]
    return instance.cost(orderedLocation[ordered_id1].id, 0) - .5*duals[ordered_id1-1]


def get_parameters(instance: Instance):
    # TODO START
    number_of_constraints = len(instance.locations) - 1
    p = columngenerationsolverpy.Parameters(number_of_constraints)
    p.objective_sense = "min"

    # column bounds
    p.column_lower_bound = 0
    p.column_upper_bound = 1
    # row bounds
    for i in range(number_of_constraints):
        p.row_lower_bounds[i] = 0
        p.row_upper_bounds[i] = 1
        p.row_coefficient_lower_bounds[i] = 0
        p.row_coefficient_upper_bounds[i] = 1
        
        p.dummy_column_objective_coefficient = 2
    # TODO END
    # Pricing solver.
    p.pricing_solver = PricingSolver(instance)
    return p


def to_solution(columns, fixed_columns):
    solution = []
    for column, value in fixed_columns:
        s = []
        for index, coef in zip(column.row_indices, column.row_coefficients):
            s += [index] * coef
        solution.append((value, s))
    return solution


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
            "-a", "--algorithm",
            type=str,
            default="column_generation",
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

    if args.algorithm == "checker":
        instance = Instance(args.instance)
        instance.check(args.certificate)

    elif args.algorithm == "column_generation":
        instance = Instance(args.instance)
        output = columngenerationsolverpy.column_generation(get_parameters(instance))

    else:
        instance = Instance(args.instance)
        parameters = get_parameters(instance)
        if args.algorithm == "greedy":
            output = columngenerationsolverpy.greedy(
                    parameters)
        elif args.algorithm == "limited_discrepancy_search":
            output = columngenerationsolverpy.limited_discrepancy_search(
                    parameters)
        solution = to_solution(parameters.columns, output["solution"])
        if args.certificate is not None:
            data = {"locations": solution}
            with open(args.certificate, 'w') as json_file:
                json.dump(data, json_file)
            print()
            instance.check(args.certificate)
