import json
import math
import columngenerationsolverpy
import treesearchsolverpy
import elementaryshortestpathwithslots as elp


class Location:
    id = None
    visit_intervals = None
    x = None
    y = None


class Instance:

    def __init__(self, filepath=None):
        self.locations = []
        if filepath is not None:
            with open(filepath) as json_file:
                data = json.load(json_file)
                locations = zip(
                        data["visit_intervals"],
                        data["xs"],
                        data["ys"])
                for (intervals, x, y) in locations:
                    self.add_location(intervals, x, y)

    def add_location(self, visit_intervals, x, y):
        location = Location()
        location.id = len(self.locations)
        location.visit_intervals = visit_intervals
        location.x = x
        location.y = y
        self.locations.append(location)

    def duration(self, location_id_1, location_id_2):
        xd = self.locations[location_id_2].x - self.locations[location_id_1].x
        yd = self.locations[location_id_2].y - self.locations[location_id_1].y
        d = round(math.sqrt(xd * xd + yd * yd))
        return d

    def write(self, filepath):
        data = {"visit_intervals": [location.visit_intervals
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
                    try:
                        interval = min(
                                (itrv for itrv in location.visit_intervals
                                 if itrv[0] >= t),
                                key=lambda interval: interval[1])
                        current_time = interval[1]
                    except ValueError:
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
        depot = instance.locations[0]
        listClient : list[Location] = [depot]
        for i in range(len(instance.locations)):
            if (self.already_visited[i] != 0):
                continue
            listClient.append( instance.locations[i])
        nbClient = len(listClient)
        if nbClient == 0 :
            return []
        pricing_instance = elp.Instance()
        for loc in listClient:
            pricing_instance.add_location(loc.visit_intervals, loc.x, loc.y, duals[loc.id])

        # TODO END

        # Solve subproblem instance.
        # TODO START
        bs = elp.BranchingScheme(pricing_instance)
        output = treesearchsolverpy.iterative_beam_search(bs, time_limit=10, verbose=False)
        res = bs.to_solution(output["solution_pool"].best)
        # TODO END

        # Retrieve column.
        column = columngenerationsolverpy.Column()
        # TODO START
        column.extra = [listClient[v].id for v in res]
        column.objective_coefficient = 0
        if res == []:
            return [column]
        u = 0
        column.row_indices.append(u)
        column.row_coefficients.append(1)
        for i in range(len(res)):
            v = column.extra[i]
            column.row_indices.append(v)
            column.row_coefficients.append(1)
            column.objective_coefficient += instance.duration(u, v)
            u = v
        column.objective_coefficient += instance.duration(v, depot.id)
        # TODO END

        return [column]


def get_parameters(instance):
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
        # TODO START
        tour = [v for v in column.extra]
        solution.append(tour)
        # TODO END
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

    elif args.algorithm == "generator":
        import random
        random.seed(0)
        for number_of_locations in range(101):
            instance = Instance()
            total_weight = 0
            for location_id in range(number_of_locations):
                s1 = random.randint(0, 1000)
                p1 = random.randint(0, 100)
                s2 = random.randint(0, 1000)
                p2 = random.randint(0, 100)
                x = random.randint(0, 100)
                y = random.randint(0, 100)
                instance.add_location(
                        [(s1, s1 + p1), (s2, s2 + p2)], x, y)
            instance.write(
                    args.instance + "_" + str(number_of_locations) + ".json")

    elif args.algorithm == "column_generation":
        instance = Instance(args.instance)
        output = columngenerationsolverpy.column_generation(
                get_parameters(instance))

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
