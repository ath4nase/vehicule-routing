import json
import math
import columngenerationsolverpy
import elementaryshortestpathwithsingleslot as elp

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
            if (data["locations"] != []):
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
            else :
                locations = []
                number_of_duplicates = 0
                on_time = True
                total_travelled_distance = 0


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
        #depot.visit_interval = [0, 0]
        listClient : list[Location]= [depot]
        for i in range(len(instance.locations)):
            if (self.already_visited[i] != 0):
                continue
            listClient.append(instance.locations[i])
        nbClient = len(listClient)
        if (nbClient == 0):
            return []
        pricing_instance = elp.Instance()
        for loc in listClient:
            pricing_instance.add_location(loc.visit_interval, loc.x, loc.y, duals[loc.id])

        # TODO END

        # Solve subproblem instance.
        # TODO START
        res = elp.dynamic_programming(pricing_instance)
        # TODO END

        # Retrieve column.
        column = columngenerationsolverpy.Column()
        # TODO START
        column.extra = [v for v in res]
        column.objective_coefficient = 0
        if res == []:
            return [column]
        u = 0
        column.row_indices.append(u)
        column.row_coefficients.append(1)
        for i in range(len(res)):
            v = res[i]
            column.row_indices.append(v)
            column.row_coefficients.append(1)
            column.objective_coefficient += instance.duration(u, v)
            u = v
        column.objective_coefficient += instance.duration(v, depot.id)
        if DEBUG:
            print("--Column value")
            print(column.objective_coefficient)
        # TODO END

        return [column]


def reducedcostIdToId(i, j, listClient, duals):
    id_i = listClient[i].id
    id_j = listClient[j].id
    if i == -1:
        id_i = 0
    if j == -1:
        id_j = 0
    
    if id_i == 0 and id_j == 0:
        return 0
    return instance.duration(id_i, id_j) - .5*(duals[i+1] + duals[j+1])

def feasible_and_improve(i:int, j:int, listClient, old_values, new_values, visited, duals):
    feasible = i != j and (listClient[i].visit_interval[1] + instance.duration(listClient[i].id, listClient[j].id) <= listClient[j].visit_interval[0])
    elementary = not j in visited[i]
    improved = old_values[i] + reducedcostIdToId(i, j, listClient, duals) < new_values[j]
    return feasible and elementary and improved

def get_parameters(instance: Instance):
    # TODO START
    number_of_constraints = len(instance.locations)
    p = columngenerationsolverpy.Parameters(number_of_constraints)
    p.objective_sense = "min"
    if number_of_constraints != 0:
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
    # TODO END
    # Pricing solver.
    p.pricing_solver = PricingSolver(instance)
    return p


def to_solution(columns, fixed_columns):
    solution = []
    for column, value in fixed_columns:
        tour = [v for v in column.extra]
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

    elif args.algorithm == "column_generation":
        instance = Instance(args.instance)
        output = columngenerationsolverpy.column_generation(
                get_parameters(instance))

    else:
        instance = Instance(args.instance)
        parameters = get_parameters(instance)
        if len(instance.locations) >1:
            if args.algorithm == "greedy":
                output = columngenerationsolverpy.greedy(
                        parameters)
            elif args.algorithm == "limited_discrepancy_search":
                output = columngenerationsolverpy.limited_discrepancy_search(
                        parameters)
            solution = to_solution(parameters.columns, output["solution"])
        else :
            solution =[]
        if args.certificate is not None:
            data = {"locations": solution}
            with open(args.certificate, 'w') as json_file:
                json.dump(data, json_file)
            print()
            instance.check(args.certificate)