import json
import math
from operator import attrgetter
import columngenerationsolverpy

INF = 100000000
DEBUG = False

class Location:
    id = None
    visit_interval = None
    x = None
    y = None


class Instance:

    def __init__(self, filepath=None):
        self.locations : list[Location] = []
        if filepath is not None:
            with open(filepath) as json_file:
                data = json.load(json_file)
                locations = zip(
                        data["visit_intervals"],
                        data["xs"],
                        data["ys"])
                for (intervals, x, y) in locations:
                    self.add_location(intervals[0], x, y)

    def add_location(self, visit_interval, x, y):
        location = Location()
        location.id = len(self.locations)
        location.visit_interval = visit_interval
        location.x = x
        location.y = y
        self.locations.append(location)

    def duration(self, location_id_1, location_id_2):
        xd = self.locations[location_id_2].x - self.locations[location_id_1].x
        yd = self.locations[location_id_2].y - self.locations[location_id_1].y
        d = round(math.sqrt(xd * xd + yd * yd))
        return d

    def write(self, filepath):
        data = {"visit_intervals": [location.visit_interval
                                    for location in self.locations],
                "xs": [location.x for location in self.locations],
                "ys": [location.y for location in self.locations]}
        with open(filepath, 'w') as json_file:
            json.dump(data, json_file)

    def check(self, filepath):
        print("Checker")
        print("-------")
        with open(filepath) as json_file:
            data = json.load(json_file)
            # Compute total_distance.
            total_travelled_distance = 0
            on_time = True
            for locations in data["locations"]:
                current_time = -math.inf
                location_pred_id = 0
                for location_id in locations:
                    location = self.locations[location_id]
                    d = self.duration(location_pred_id, location_id)
                    total_travelled_distance += d
                    t = current_time + d
                    if t <= location.visit_interval[0]:
                        current_time = location.visit_interval[1]
                    else:
                        on_time = False
                    location_pred_id = location_id
                total_travelled_distance += self.duration(location_pred_id, 0)
            # Compute number_of_locations.
            number_of_duplicates = len(locations) - len(set(locations))

            is_feasible = (
                    (number_of_duplicates == 0)
                    and (on_time)
                    and 0 not in locations)
            objective_value = total_travelled_distance
            print(f"Number of duplicates: {number_of_duplicates}")
            print(f"On time: {on_time}")
            print(f"Total travelled distance: {total_travelled_distance}")
            print(f"Feasible: {is_feasible}")
            return (is_feasible, objective_value)


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
        listClient  : list[Location]= []
        for i in range(len(instance.locations)):
            if (self.already_visited[i] > .5):
                continue
            listClient.append(instance.locations[i])
        nbClient = len(listClient)
        if DEBUG:
            print("-- To visit--")
            print([v.id for v in listClient])
        # TODO END

        # Solve subproblem instance.
        # TODO START
    ################################################
        if DEBUG:
            for i in range(len(listClient)):
                for j in range(len(listClient)):
                    if i != j:
                        print(reducedcostIdToId(i, j, duals), end=" ")
                    else:
                        print(0, end=" ")
                print("")

            print("--Loc--")
            for i in instance.locations:
                print(i.visit_interval)
    ################################################

        min_path_values = [reducedcostIdToId(0, listClient[i].id, duals) for i in range (nbClient)]
        predecessor = [None for _ in range(nbClient)]
        visited_clients = [{} for _ in range(nbClient)]
        previous_visited_clients = [v for v in visited_clients]
        previous_values = [v for v in min_path_values]

        if DEBUG:
            print("--Dual values--")
            print(duals)

        # computing minimal path from depot for all clients
        # if values doesn't change, finished. |V|-1 iteration at most
        while(True): 
            previous_values = [v for v in min_path_values]
            previous_visited_clients = [v for v in visited_clients]
            for i in range(nbClient):
                for j in range(nbClient):
                    if feasible_and_improve(listClient[i].id, listClient[j].id, previous_values, min_path_values, previous_visited_clients, duals):
                        predecessor[j] = i
                        min_path_values[j] =  previous_values[i] + reducedcostIdToId(listClient[i].id, listClient[j].id, duals)
                        visited_clients[j] = {i}.union(previous_visited_clients[i])
            if min_path_values == previous_values:
                break
        # then pick best cycle by adding the edge (u, depot) to the shortest path (depot, u)
        best_path_end = min([(i, min_path_values[i] + reducedcostIdToId(listClient[i].id, 0, duals)) for i in range(nbClient)], key= lambda a : a[1])
        current = best_path_end[0]
        res : list[Location] = []
        while current != None:
            res.append(listClient[current])
            current = predecessor[current]
        
        res.reverse()
        if DEBUG:
            print("--Column--")
            print ([loc.id for loc in res])
        # TODO END

        # Retrieve column.
        column = columngenerationsolverpy.Column()
        column.extra = [v for v in res]
        # TODO START
        column.objective_coefficient = 0
        if res == []:
            return [column]
        u = depot
        column.row_indices.append(u.id)
        column.row_coefficients.append(1)
        for i in range(len(res)):
            v = res[i]
            column.row_indices.append(v.id)
            column.row_coefficients.append(1)
            column.objective_coefficient += instance.duration(u.id, v.id)
            u = v
        column.objective_coefficient += instance.duration(v.id, depot.id)
        if DEBUG:
            print("--Column value")
            print(column.objective_coefficient)
        # TODO END

        return [column]


def reducedcostIdToId(ordered_id1, ordered_id2, duals):
    if ordered_id1 == 0 and ordered_id2 == 0:
        return 0
    return instance.duration(ordered_id1, ordered_id2) - .5*(duals[ordered_id1] + duals[ordered_id2])

def feasible_and_improve(i:int, j:int, old_values, new_values, visited, duals):
    feasible = i != j and (instance.locations[i].visit_interval[1] + instance.duration(i, j) <= instance.locations[j].visit_interval[0])
    elementary = not j in visited[i-1]
    improved = old_values[i-1] + reducedcostIdToId(i, j, duals) < new_values[j-1]
    return feasible and elementary and improved

def get_parameters(instance: Instance):
    # TODO START
    number_of_constraints = len(instance.locations)
    p = columngenerationsolverpy.Parameters(number_of_constraints)
    p.objective_sense = "min"

    # column bounds
    p.column_lower_bound = 0
    p.column_upper_bound = 1
    # row bounds
    p.row_lower_bounds[0] = 0
    p.row_upper_bounds[0] = len(instance.locations) - 1
    p.row_coefficient_lower_bounds[0] = 1
    p.row_coefficient_upper_bounds[0] = 1
    for i in range(1, number_of_constraints):
        p.row_lower_bounds[i] = 1
        p.row_upper_bounds[i] = 1
        p.row_coefficient_lower_bounds[i] = 0
        p.row_coefficient_upper_bounds[i] = 1
    
    values = []
    for i in range (len(instance.locations)):
        for j in range (len(instance.locations)):
            values.append(instance.duration(i, j))
    p.dummy_column_objective_coefficient = 3*max(values)
    print(" Coeff dummy = ", p.dummy_column_objective_coefficient)
    # TODO END
    # Pricing solver.
    p.pricing_solver = PricingSolver(instance)
    return p


def to_solution(columns, fixed_columns):
    solution = []
    for column, value in fixed_columns:
        tour = [v.id for v in columns[column].extra]
        solution.append(tour)
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


    else:
        instance = Instance(args.instance)
        parameters = get_parameters(instance)
        if args.algorithm == "greedy":
            output = columngenerationsolverpy.greedy(
                    parameters)
        elif args.algorithm == "column_generation":
            output = columngenerationsolverpy.column_generation(parameters)
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
