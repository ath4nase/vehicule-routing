import json
import math
import treesearchsolverpy
from functools import total_ordering
import numpy as np
import copy

class Location:
    id = None
    visit_intervals = None
    x = None
    y = None
    value = None


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
                    self.add_location(intervals, x, y, value)

    def add_location(self, visit_intervals, x, y, value):
        location = Location()
        location.id = len(self.locations)
        location.visit_intervals = visit_intervals
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
                try:
                    interval = min(
                            (interval for interval in location.visit_intervals
                             if interval[0] >= t),
                            key=lambda interval: interval[1])
                    current_time = interval[1]
                except ValueError:
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


class BranchingScheme:

    @total_ordering
    class Node:

        id = None
        father = None
        # TODO START
        visited = [] #Save the nodes visited by the current node
        path = [] #Save the node on the current path
        time = 0 #current time
        next_child_pos = None 
        next_child_interval = 0 #Either 1 or 0 depending on which time we visited
        cost = None
        idP = None
        
        # TODO END
        guide = None 
        

        def __lt__(self, other):
            if self.guide != other.guide:
                return self.guide < other.guide
            return self.id < other.id
        
        def next_child(self, instance):
            comparisonTime = 0 #instance.locations[self.next_child_pos].visit_intervals[self.next_child_interval][1] 
            minTime = np.infty
            minInterval = 0
            minId = None
            
            #print(self.visited)
            #print(self.path)
            #print("cp time: "+str(comparisonTime))
            #print("next: "+str(self.next_child_pos))
            
            #finding the next child in ordered way not allowing to go to an already visited client and interval for this node or for the path
            for ii in range(len(instance.locations)):
                #print(ii)
                #if site ii first slot not visited yet
                if ((ii not in self.path) and (ii not in self.visited) and ii+len(instance.locations) not in self.visited):
                    #print("0: "+str(ii))
                    travel = instance.duration(self.idP, ii)+self.time
                    #if it can be visited in time
                    if (travel <= instance.locations[ii].visit_intervals[0][0]):
                        #print("pan")
                        temp = instance.locations[ii].visit_intervals[0][1]
                        #find the next visit that will finish the earliest
                        if(temp>comparisonTime and temp<minTime):
                            minTime = temp
                            minInterval = 0
                            minId = ii
                            
                            #print(temp)
                            #print(str(ii)+"  "+str(0)+"  "+str(minId))
                            
                #if site ii 2nd slot not visited yet
                if (ii not in self.path and ii+len(instance.locations) not in self.visited and ii not in self.visited):
                    #print("1: "+str(ii))
                    travel = instance.duration(self.idP, ii)+self.time
                    #if it can be visited in time
                    if (travel <= instance.locations[ii].visit_intervals[1][0]):
                        temp = instance.locations[ii].visit_intervals[1][1]
                        #find the next visit that will finish the earliest
                        if(temp>comparisonTime and temp<minTime):
                            minTime = temp
                            minInterval = 0
                            minId = ii
                            #print(temp)
                            #print(str(ii)+"  "+str(1)+"  "+str(minId))
                #print("minId: "+str(minId))
            
            self.next_child_pos = minId
            self.next_child_interval = minInterval
            #print("next pos: "+str(self.next_child_pos))
            #print(self.cost)

    def __init__(self, instance):
        self.instance = instance
        self.id = 0

    def root(self):
        node = self.Node()
        node.father = None
        # TODO START
        node.visited = [0]
        node.path = [0]
        node.time = 0
        node.cost = 0
        node.idP = 0
        node.guide = None
        
        #finding the first closest child   ==> should be transformed to try by smallest cost first
        minTime = np.infty
        minInterval = 0
        minId = None

        for ii in range(len(self.instance.locations)):
            travel = self.instance.duration(0, ii)
            
            if (self.instance.locations[ii].visit_intervals[0][1]<minTime and ii not in node.visited):
                if (travel <= self.instance.locations[ii].visit_intervals[0][0]):
                    minTime = self.instance.locations[ii].visit_intervals[0][1]
                    minInterval = 0
                    minId = ii
            
            if (self.instance.locations[ii].visit_intervals[1][1]<minTime and ii+len(self.instance.locations) not in node.visited):
                if (travel<=self.instance.locations[ii].visit_intervals[1][0]):
                    minTime = self.instance.locations[ii].visit_intervals[1][1]
                    minInterval = 1
                    minId = ii
                    
        node.next_child_pos = minId
        node.next_child_interval = minInterval
                
        # TODO END
        node.guide = 0
        node.id = self.id
        self.id += 1
        return node

    def next_child(self, father):
        # TODO START
        idNext = father.next_child_pos
        intervalNext = father.next_child_interval
        
        temp = idNext+intervalNext*len(self.instance.locations)
        #print(temp)
        if temp in father.path or idNext is None or temp in father.visited: #normally idNext == 1 should be sufficient
            if (temp not in father.visited):
                father.visited.append(temp) #interval is stocked in it
            #update the father node
            father.next_child(self.instance)
            return None
        
        father.visited.append(temp) #interval is stocked in it
        father.next_child(self.instance)
        
        #build the child node
        child = self.Node()
        child.idP = idNext
        child.chosenInterval = intervalNext
        child.father = father
        child.visited = [idNext]

        child.path = copy.deepcopy(father.path)
        child.path.append(idNext)
        child.time = self.instance.locations[idNext].visit_intervals[intervalNext][1]
        child.cost = father.cost+self.instance.cost(father.idP,idNext)
        
        print(child.path)
        print(child.cost + self.instance.cost(idNext,0))
        print(child.time)
        
        child.next_child(self.instance)
        child.guide = child.cost
        
        #print(child.next_child_pos)
        child.id = self.id
        self.id += 1

        return child
        pass
        # TODO END

    def infertile(self, node):
        # TODO START
        #print("pan")
        return (node.next_child_pos is None) #might need to change every return None to None as None is used in the lib
        pass
        # TODO END

    def leaf(self, node):
        # TODO START
        return (node.idP == 0)
        pass
        # TODO END

    def bound(self, node_1, node_2):
        # TODO START
        if(node_2.idP == 0):
            return False
        d2 = node_2.cost + self.instance.cost(node_2.idP, 0)
        return node_1.cost >= d2
        pass
        # TODO END

    # Solution pool.

    def better(self, node_1, node_2):
        # TODO START
        if(node_1.idP == 0):
            return False
        if(node_2.idP == 0):
            return True
        # Compute the objective value of node_1.
        d1 = node_1.cost + self.instance.cost(node_1.idP, 0)
        # Compute the objective value of node_2.
        d2 = node_2.cost + self.instance.cost(node_2.idP, 0)
        return d1 < d2
        pass
        # TODO END

    def equals(self, node_1, node_2):
        # TODO START
        """if(node_1.idP != 0 or node_1.idP is None):
            return False
        if(node_2.idP != 0 or node_2.idP is None):
            return False
        # Compute the objective value of node_1.
        d1 = node_1.cost + self.instance.cost(node_1.idP, 0)
        # Compute the objective value of node_2.
        d2 = node_2.cost + self.instance.cost(node_2.idP, 0)
        return d1 == d2"""
        return False
        pass
        # TODO END

    # Dominances.

    def comparable(self, node):
        # TODO START
        return (node.idP==0 and self.node.idP==0)
        pass
        # TODO END

    class Bucket:

        def __init__(self, node):
            self.node = node

        def __hash__(self):
            # TODO START
            return hash((self.node.idP, self.node.chosenInterval, self.node.cost))
            pass
            # TODO END

        def __eq__(self, other):
            # TODO START
            return (self.node.idP == other.node.idP and self.node.visited == other.node.visited)
            pass
            # TODO END

    def dominates(self, node_1, node_2):
        # TODO START
        if node_1.cost <= node_2.cost:
            return True
        return False
        pass
        # TODO END

    # Outputs.

    def display(self, node):
        # TODO START
        # Compute the objective value of node.
        if(node.idP != 0):
            d = node.cost + self.instance.cost(node.idP, 0)
        else:
            d = node.cost
        return str(d)
        pass
        # TODO END

    def to_solution(self, node):
        # TODO START
        locations = []
        node_tmp = node
        while node_tmp.father is not None:
            locations.append(node_tmp.idP)
            node_tmp = node_tmp.father
        locations.reverse()
        return locations
        pass
        # TODO END


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
            "-a", "--algorithm",
            type=str,
            default="iterative_beam_search",
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
                value = random.randint(0, 100)
                instance.add_location(
                        [(s1, s1 + p1), (s2, s2 + p2)], x, y, value)
            instance.write(
                    args.instance + "_" + str(number_of_locations) + ".json")

    else:
        instance = Instance(args.instance)
        branching_scheme = BranchingScheme(instance)
        if args.algorithm == "greedy":
            output = treesearchsolverpy.greedy(
                    branching_scheme)
        elif args.algorithm == "best_first_search":
            output = treesearchsolverpy.best_first_search(
                    branching_scheme,
                    time_limit=30)
        elif args.algorithm == "iterative_beam_search":
            output = treesearchsolverpy.iterative_beam_search(
                    branching_scheme,
                    time_limit=30)
        solution = branching_scheme.to_solution(output["solution_pool"].best)
        if args.certificate is not None:
            data = {"locations": solution}
            with open(args.certificate, 'w') as json_file:
                json.dump(data, json_file)
            print()
            instance.check(args.certificate)
