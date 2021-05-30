import csv
import math
import os

#classes 
class city:
    def __init__(self, name, latitude, longitude):
        self.name = name
        self.latitude = latitude
        self.longitude = longitude

class flights:
    def __init__(self, source, dest, departure, arrival, flightNo, days):
        self.source = source
        self.destination = dest
        self.departure = departure
        self.arrival = arrival
        self.flightNo = flightNo
        self.days = days
## csv files which i have created
class days:
    def __init__(self,name,priority):
        self.name= name
        self.priority=priority
# used in the search alghorithm (a *)
class Node:
    def __init__(self,flight,parent):
        self.parent = parent
        self.flight = flight
        self.f = 0
        self.g =0
        self.h =0


# functions that reads from CSV Files
def readCities():
    c = []
    with open(os.getcwd()+'\\cities.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                c.append(city(row[0], row[1], row[2]))
                line_count += 1
        return c

def readFlights():
    f = []
    D = readDays()
    with open(os.getcwd()+'\\flights.csv') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        for row in csv_reader:
            if line_count == 0:
                line_count += 1
            else:
                days = row[5][1:len(row[5]) - 1].split(", ")
                days_with_priority = []
                for d in days:
                    for x in D:
                        if d in x.name.lower():
                            days_with_priority.append(x)       
                f.append(flights(row[0], row[1], row[2], row[3], row[4], days_with_priority))
                line_count += 1
        return f
def readDays():
    d = []
    with open(os.getcwd()+'\\days.csv') as csv_file:
        csv_reader = csv.reader(csv_file,delimiter=',')
        line_count = 0
        for row in csv_reader:
           if line_count == 0:
               line_count +=1
           else:
               d.append(days(row[0],row[1]))
               line_count+=1
        return d

               
# main function
def system():
   input_arr= takeInput()
   path = aStar_search(input_arr[0],input_arr[1],input_arr[2],input_arr[3])
   results(path)

# function that takes input from user
def takeInput():
    source= input("Enter source:  ")
    destination = input("Enter destination ")
    start_day = input("Enter start day : ")
    end_day = input("Enter end day: ")
    return [source,destination,start_day,end_day]



# returns filtered flights according to the required city between range of the start day and the end day.
def filterFlights(start_day,end_day,requiredCity):
    F = readFlights()
    C = readCities()
    D = readDays()
    # get priority of start_day  and end_day
    for d in D:
        if d.name.lower() == start_day.lower():
            start_priority = d.priority
        if d.name.lower() == end_day.lower():
            end_priority = d.priority
    temp = []
    days_within_range = []
   ## days filtering accorind to priority
    if start_priority < end_priority:
        for f in F:
            for d in f.days:
                if start_priority <= d.priority and d.priority <= end_priority:
                    days_within_range.append(d)
            if len(days_within_range) > 0:
                temp.append(flights(f.source,f.destination,f.departure,f.arrival,f.flightNo,days_within_range))
                days_within_range=[]
    elif start_priority > end_priority:
        for f in F:
            for d in f.days:
                if end_priority < d.priority and d.priority < start_priority:
                    continue
                days_within_range.append(d)
            if len(days_within_range) > 0:
                temp.append(flights(f.source,f.destination,f.departure,f.arrival,f.flightNo,days_within_range))
                days_within_range=[]        
    ## time filter
    for x in temp:
        if contains(end_priority,x.days):
            time_difference = calculateTimeDifference(x.departure,x.arrival)
            #check if the flight departure arrives in the next day or not
            d= x.departure[0:len(x.departure)].split(":")
            d_hours = int(d[0]) * 60
            d_minutes = int(d[1])
            # if total minutes (time difference between departure and arrival + departure hours (in minutes) + departure minutes) exceeds 24 * 60 (1440 minute)
            # then remove this flight else keep
            if time_difference + d_hours + d_minutes > 1440:
                if(len(x.days) > 1):
                   for d in x.days:
                       if d.priority == end_priority:
                           x.days.remove(d)
                           break       
                else:
                    temp.remove(x)
    final_filtered_flights= []
    # filter on day get flights that launches from e.g. cairo
    for f in temp:
        if f.source.lower() == requiredCity.lower():
            final_filtered_flights.append(f)       
    return final_filtered_flights


def calculateHeuristic(Node,goalName,velocity,parent):  
    # assuming velocity in order to make the whole function in term of time (the goal is to minimize the time) 
    f=0
    g=0
    h=0
    parentTime = 0
    if  not(parent == None):
        parentTime = parent.g
    departure = Node.flight.departure
    arrival = Node.flight.arrival
    # get source and destination
    destination = getCity(Node.flight.destination.lower())
    goal = getCity(goalName)
     # Using Euclidean Distance
    # g is distance between the starting point to a given point plus parent cost 
    g= ( parentTime + calculateTimeDifference(departure,arrival) ) / 60 # difference bettwen departure time and arrival time + parent time if exsists
    # calculating h using latitude and longitude divided by velocity in order to make the whole function in terms of time (assuming plane speed per hour )
    h= math.sqrt(
                    (float(destination.latitude) - float(goal.latitude)) ** 2 + (float(destination.longitude) - float(goal.longitude)) ** 2) / velocity
    # f is the summation of g and h
    f = (g + h )
    Node.g=g
    Node.h=h
    Node.f=f         

   
# A* alghorithm
def aStar_search(source,destination,start_day,end_day):
    filtered_flights = filterFlights(start_day,end_day,source)
    openList =[]
    closedList=[]
    # fill open list
    for f in filtered_flights:
        openList.append(Node(f,None))
    # calculate heuristic of the nodes in the open list.
    for node in openList:
        calculateHeuristic(node,destination,200,None)
    while len(openList) > 0:
        # get node with least f (least cost)
        current_node = getNodeWithLeastF(openList) ## Cairo alexandira [tue,wed,thu]

        # remove this node from openList
        openList.remove(current_node)

        # add this node to closed list
        closedList.append(current_node)

        # get successors of this node and choose which one to be added in the open list
        successors = getSuccessors(current_node,end_day)
        # if found break
        path = []
        if current_node.flight.destination.casefold() == destination.casefold():
            # gets path 
            calculateHeuristic(current_node,destination,200,current_node.parent)
            parent = current_node.parent
            path.append(current_node)
            while parent != None:
                path.append(parent)
                parent = parent.parent
            path.reverse()
            return path
        # loop in each successor
        for successor in successors:
            calculateHeuristic(successor,destination,200,successor.parent)
            if not isSameFlight(successor,openList) and not isSameFlight(successor,closedList):
                openList.append(successor)
    return None


            
# return childs of a given node.
def getSuccessors(node,end_day):
    departure = node.flight.departure
    arrival = node.flight.arrival[0:len(node.flight.arrival)].split(":")
    successors = []
    temp = filterFlights(node.flight.days[0].name,end_day,node.flight.destination)
    arrival_in_minutes = int(arrival[0]) * 60 + int(arrival[1])
    filteredFlights =[]
    for f in temp:
        f_departure = f.departure[0:len(f.departure)].split(":")
        f_departure_in_minutes = int(f_departure[0]) * 60 + int(f_departure[1])
        if node.flight.days[0].name == f.days[0].name: 
            if f_departure_in_minutes > arrival_in_minutes:
                filteredFlights.append(f)
        else:
            filteredFlights.append(f)
    # convert flight to Node
    filtered_nodes = []
    for flight in filteredFlights:
        filtered_nodes.append(Node(flight,node))
    return filtered_nodes
        


# gets node with least cost in the open list    
def getNodeWithLeastF(open_list):
    temp = open_list[0]
    for node in open_list:
        if node.f < temp.f:
            temp = node
    return temp          



# returns city by name
def getCity(destination):
    cities = readCities()
    for city in cities:
         if city.name.casefold() == destination.casefold():
             return city   
    return None




# check if a day is in a given list
def contains(value,days):
    for d in days:
        if value == d.priority:
            return True
    return False
           
# calculates time difference between departure and arrival in minutes                
def calculateTimeDifference(departure,arrival):
    t1= departure[0:len(departure)].split(":")
    t2 = arrival[0:len(arrival)].split(":")
    departure_hours = int(t1[0]) * 60
    departure_minutes= int(t1[1])
    arrival_hours = int(t2[0]) * 60
    arrival_minutes= int(t2[1])
    # in minutes
    return math.ceil(abs((arrival_hours+arrival_minutes)-(departure_hours+departure_minutes)))        
    

# checks if two flights are equal
def isSameFlight(f1,openList):
    for node in openList:
        if f1.flight.source == node.flight.source and f1.flight.destination == node.flight.destination:
            return True
    return False
        


# send back results to user in a given format.
def results(path):
    if path == None:
        print("not found")
    else:
        count = 1
        for p in path:
            print("Step ",count," :", "use flight ",p.flight.flightNo,"from ",p.flight.source,"to ",p.flight.destination," departure time:",p.flight.departure," arrival time: ",p.flight.arrival)
            count +=1
            
    


    
   
       
    
