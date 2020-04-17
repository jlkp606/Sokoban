
'''

    2020 CAB320 Sokoban assignment


The functions and classes defined in this module will be called by a marker script. 
You should complete the functions and classes according to their specified interfaces.
No partial marks will be awarded for functions that do not meet the specifications
of the interfaces.


You are NOT allowed to change the defined interfaces.
That is, changing the formal parameters of a function will break the 
interface and results in a fail for the test of your code.
This is not negotiable! 


'''

# You have to make sure that your code works with 
# the files provided (search.py and sokoban.py) as your code will be tested 
# with these files
import search 
import sokoban
import time
from random import random
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def my_team():
    '''
    Return the list of the team members of this assignment submission as a list
    of triplet of the form (student_number, first_name, last_name)
    
    '''
    return [ (10008195, 'Joshua', 'La') ]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def taboo_cells(warehouse):
    '''  
    Identify the taboo cells of a warehouse. A cell inside a warehouse is 
    called 'taboo'  if whenever a box get pushed on such a cell then the puzzle 
    becomes unsolvable. Cells outside the warehouse should not be tagged as taboo.
    When determining the taboo cells, you must ignore all the existing boxes, 
    only consider the walls and the target  cells.  
    Use only the following two rules to determine the taboo cells;
     Rule 1: if a cell is a corner and not a target, then it is a taboo cell.
     Rule 2: all the cells between two corners along a wall are taboo if none of 
             these cells is a target.
    
    @param warehouse: 
        a Warehouse object with a worker inside the warehouse

    @return
       A string representing the puzzle with only the wall cells marked with 
       a '#' and the taboo cells marked with a 'X'.  
       The returned string should NOT have marks for the worker, the targets,
       and the boxes.  
    '''
    corner_cells = [] #all corner pieces including corners on the outside of the warehouse
    taboo_cells = []
    inside_warehouse_coords = []
    col_in_warehouse = False
    row_in_warehouse = False
    # gets all coordinates for the whole warehouse
    for col in range(warehouse.ncols):
        for row in range(warehouse.nrows):
            #for each line go from left to right wall to wall, anything that was not hit isnt inside
            #if inside wall then true(ie you start wall 1 you inside until you hit wall 2 and you inside again when you hit wall 3)
            if ((col, row) in warehouse.walls):
                if ((col, row - 1) not in warehouse.walls):
                    row_in_warehouse = not row_in_warehouse
            if((col, row) in warehouse.walls):
                if ((col - 1, row) in warehouse.walls):
                    col_in_warehouse = not col_in_warehouse
            #gets the coordinates of the empty spaces
            if (((col, row) not in warehouse.walls) and 
                (col_in_warehouse and row_in_warehouse)):
                inside_warehouse_coords.append((col, row))
                #checks if there are two adjacent walls
                #if there is then it will be a taboo cell
                if ((col+1, row) in warehouse.walls) and ((col, row+1) in warehouse.walls):
                    corner_cells.append((col, row))
                elif ((col-1, row) in warehouse.walls) and ((col, row+1) in warehouse.walls):
                    corner_cells.append((col, row))
                elif ((col-1, row) in warehouse.walls) and ((col, row-1) in warehouse.walls):
                    corner_cells.append((col, row))
                elif ((col+1, row) in warehouse.walls) and ((col, row-1) in warehouse.walls):
                    corner_cells.append((col, row))
        row_in_warehouse = False
        col_in_warehouse = False
    warehouse.inside_warehouse_coords = inside_warehouse_coords
    temp_taboo_cells = []
    
    #get rid of outside corners
    #check if you ride along corners there are walls next to it
    for corner in corner_cells:
        for col in range(warehouse.ncols-1):# -1 because there are walls
            if ((corner[0] + col, corner[1]) not in warehouse.walls):
                if (((corner[0] + col, corner[1] + 1) in warehouse.walls) or ((corner[0] + col, corner[1] - 1) in warehouse.walls)):
                    if not (corner[0] + col, corner[1]) in warehouse.targets:
                        temp_taboo_cells.append((corner[0] + col, corner[1]))
                else:
                    temp_taboo_cells = []
                    break
            else:
                break
        taboo_cells.extend(temp_taboo_cells)
        for row in range(warehouse.nrows-1):
            if ((corner[0], corner[1] + row) not in warehouse.walls):
                if (((corner[0] + 1, corner[1] + row) in warehouse.walls) or ((corner[0] - 1, corner[1] + row) in warehouse.walls)):
                    if not (corner[0], corner[1] + row) in warehouse.targets:
                        temp_taboo_cells.append((corner[0], corner[1] + row))
                else:
                    temp_taboo_cells = []
                    break
            else:
                break
        taboo_cells.extend(temp_taboo_cells)

    warehouse.taboo_cells = taboo_cells

    #took this from sokoban.py in the __str__ function

    X,Y = zip(*warehouse.walls) # pythonic version of the above
    x_size, y_size = 1+max(X), 1+max(Y)
    vis = [[" "] * x_size for y in range(y_size)]

    for (x,y) in warehouse.walls:
        vis[y][x] = "#"
    for (x,y) in taboo_cells:
        vis[y][x] = "X"
    return "\n".join(["".join(line) for line in vis])


    
    
# - - - - - - - - - - My Functions - - - - - - - - - - - - - - - - - - -

def distance_between_two_points(point1, point2):
    x_distance = abs(point1[0] - point2[0])
    y_distance = abs(point1[1] - point2[1])
    return x_distance + y_distance

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
class SokobanPuzzle(search.Problem):
    '''
    An instance of the class 'SokobanPuzzle' represents a Sokoban puzzle.
    An instance contains information about the walls, the targets, the boxes
    and the worker.

    Your implementation should be fully compatible with the search functions of 
    the provided module 'search.py'. 
    
    Each SokobanPuzzle instance should have at least the following attributes
    - self.allow_taboo_push
    - self.macro
    
    When self.allow_taboo_push is set to True, the 'actions' function should 
    return all possible legal moves including those that move a box on a taboo 
    cell. If self.allow_taboo_push is set to False, those moves should not be
    included in the returned list of actions.
    
    If self.macro is set True, the 'actions' function should return 
    macro actions. If self.macro is set False, the 'actions' function should 
    return elementary actions.        
    '''
    
    #
    #         "INSERT YOUR CODE HERE"
    #
    #     Revisit the sliding puzzle and the pancake puzzle for inspiration!
    #
    #     Note that you will need to add several functions to 
    #     complete this class. For example, a 'result' function is needed
    #     to satisfy the interface of 'search.Problem'.

    allow_taboo_push = True
    ignore_box = False
    macro = False
    inside_warehouse_coords = []
    taboo_cells = []
    exit = False


    def __init__(self, warehouse, goal=None, ignore_box=False, macro=False, allow_taboo_push = True):

        taboo_cells(warehouse)
        self.taboo_cells = set(warehouse.taboo_cells)

        if (ignore_box):
            self.ignore_box = ignore_box
            self.inside_warehouse_coords = warehouse.inside_warehouse_coords
            if ((goal not in self.inside_warehouse_coords) or (goal in warehouse.boxes)):
                self.exit = True

        self.macro = macro

        self.initial = warehouse
        if (goal == None):
            self.goal = warehouse.targets
        else:
            self.goal = goal

    def can_move_there(self, state, object, is_worker, direction):
        if (direction == 'Right'):
            # if next space is not a wall
            if (((object[0]+1, object[1]) not in state.walls) and
            # and not a box
                (((object[0]+1, object[1]) not in state.boxes))):
                return True

            #else if the object is the worker
            elif ((is_worker) and
                #and it is a box
                ((object[0]+1, object[1]) in state.boxes) and
                # and theres no box behind it
                (((object[0]+2, object[1]) not in state.boxes) and
                # and no wall behind it
                ((object[0]+2, object[1]) not in state.walls)) and
                # and we're not in "ignore boxes" mode
                not self.ignore_box):
                # and if taboo is not allowed 
                if(not self.allow_taboo_push):
                    #if box is pushed to that is not taboo
                    if ((object[0]+2, object[1]) not in self.taboo_cells):
                        #then you can move there
                        return True
                else:
                    return True
        elif (direction == 'Left'):
            if (((object[0]-1, object[1]) not in state.walls) and
                (((object[0]-1, object[1]) not in state.boxes))):
                return True

            elif ((is_worker) and
                ((object[0]-1, object[1]) in state.boxes) and
                (((object[0]-2, object[1]) not in state.boxes) and
                ((object[0]-2, object[1]) not in state.walls)) and
                not self.ignore_box):
                if(not self.allow_taboo_push):
                    if ((object[0]-2, object[1]) not in self.taboo_cells):
                        return True
                else:
                    return True
        
        elif (direction == 'Up'):
            if (((object[0], object[1]-1) not in state.walls) and
                (((object[0], object[1]-1) not in state.boxes))):
                return True

            elif ((is_worker) and
                ((object[0], object[1]-1) in state.boxes) and
                (((object[0], object[1]-2) not in state.boxes) and
                ((object[0], object[1]-2) not in state.walls)) and
                not self.ignore_box):
                if(not self.allow_taboo_push):
                    if ((object[0], object[1]-2) not in self.taboo_cells):
                        return True
                else:
                    return True
        
        elif (direction == 'Down'):
            if (((object[0], object[1]+1) not in state.walls) and
                (((object[0], object[1]+1) not in state.boxes))):
                return True

            elif ((is_worker) and
                ((object[0], object[1]+1) in state.boxes) and
                (((object[0], object[1]+2) not in state.boxes) and
                ((object[0], object[1]+2) not in state.walls)) and
                not self.ignore_box):
                if(not self.allow_taboo_push):
                    if ((object[0], object[1]+2) not in self.taboo_cells):
                        return True
                else:
                    return True
        return False

    def actions(self, state):
        """
        Return the list of actions that can be executed in the given state.
        
        As specified in the header comment of this class, the attributes
        'self.allow_taboo_push' and 'self.macro' should be tested to determine
        what type of list of actions is to be returned.
        """
        L = []

        if (self.macro):
            for box in state.boxes:
                #check if they can be pushed first
                #eg. check if it can be pushed up 
                #then check if i can go underneath
                


                #get the coord around each box and see if you can go there
                #then see if you can push it 
                # if you can append the box coord and which direction you push


                #this is what side the worker will be on. so they will push the box the other way
                adjacent_cells = [((box[0]+1,box[1]), 'RightSide'), ((box[0]-1, box[1]), 'LeftSide'),
                                ((box[0],box[1]+1), 'Below'), ((box[0]+1,box[1]-1), 'Above')]
                
                for cell, direction in adjacent_cells:
                    if (can_go_there(state, cell)):
                        blah_blah = "blah"

        directions = ['Right', 'Left', 'Up', 'Down']
        for direction in directions:
            if (self.can_move_there(state, state.worker, True, direction)):
                L.append(direction)

        # # if next space is not a wall
        # if (((state.worker[0]+1, state.worker[1]) not in state.walls) and
        #     # and not a box
        #     (((state.worker[0]+1, state.worker[1]) not in state.boxes))):
        #     L.append('Right')
        #     # else if it is a box
        # elif (((state.worker[0]+1, state.worker[1]) in state.boxes) and
        #     # and theres no box behind it
        #     (((state.worker[0]+2, state.worker[1]) not in state.boxes) and
        #     # and no wall behind it
        #     ((state.worker[0]+2, state.worker[1]) not in state.walls)) and
        #     # and we're not in "can go there" mode
        #     not self.ignore_box):
        #     # and if taboo is not allowed 
        #     if(not self.allow_taboo_push):
        #         #if box is pushed to that is not taboo
        #         if ((state.worker[0]+2, state.worker[1]) not in self.taboo_cells):
        #             #then you can move there
        #             L.append('Right')
        #     else:
        #         L.append('Right')
        # if (((state.worker[0]-1, state.worker[1]) not in state.walls) and
        #     (((state.worker[0]-1, state.worker[1]) not in state.boxes))):
        #     L.append('Left')
        # elif (((state.worker[0]-1, state.worker[1]) in state.boxes) and
        #     (((state.worker[0]-2, state.worker[1]) not in state.boxes) and
        #     ((state.worker[0]-2, state.worker[1]) not in state.walls)) and
        #     not self.ignore_box):
        #     if(not self.allow_taboo_push and not self.ignore_box):
        #         if (((state.worker[0]-1, state.worker[1]) in state.boxes) and
        #             ((state.worker[0]-2, state.worker[1]) not in self.taboo_cells)):
        #             L.append('Left')
        #     else:
        #         L.append('Left')
        # if (((state.worker[0], state.worker[1]-1) not in state.walls) and
        #     (((state.worker[0], state.worker[1]-1) not in state.boxes))):
        #     L.append('Up')
        # elif (((state.worker[0], state.worker[1]-1) in state.boxes) and
        #     (((state.worker[0], state.worker[1]-2) not in state.boxes) and
        #     ((state.worker[0], state.worker[1]-2) not in state.walls)) and
        #     not self.ignore_box):
        #     if(not self.allow_taboo_push and not self.ignore_box):
        #         if (((state.worker[0], state.worker[1]-1) in state.boxes) and 
        #             ((state.worker[0], state.worker[1]-2) not in self.taboo_cells)):
        #             L.append('Up')
        #     else:
        #         L.append('Up')
        # if (((state.worker[0], state.worker[1]+1) not in state.walls) and
        #     (((state.worker[0], state.worker[1]+1) not in state.boxes))):
        #     L.append('Down')
        # elif (((state.worker[0], state.worker[1]+1) in state.boxes) and
        #     (((state.worker[0], state.worker[1]+2) not in state.boxes) and
        #     ((state.worker[0], state.worker[1]+2) not in state.walls)) and
        #     not self.ignore_box):
        #     if(not self.allow_taboo_push and not self.ignore_box):
        #         if (((state.worker[0], state.worker[1]+1) in state.boxes) and 
        #             ((state.worker[0], state.worker[1]+2) not in self.taboo_cells)):
        #             L.append('Down')
        #     else:
        #         L.append('Down')

        return L
    
    def result(self, state, action):
        #move boxes
        # test this, move boxes
        #look up on state and how its passed
        #state should be box and worker
        next_state = state.copy()# make a copy otherwise it uses an alias
        next_state.boxes = next_state.boxes.copy()# make a copy otherwise it uses an alias
        if action == 'Right':
            next_state.worker = (next_state.worker[0]+1, next_state.worker[1])
            if next_state.worker in next_state.boxes:
                box_index = next_state.boxes.index(next_state.worker)
                next_state.boxes[box_index] = ((next_state.worker[0]+1, next_state.worker[1]))
        elif action == 'Left':
            next_state.worker = (next_state.worker[0]-1, next_state.worker[1])
            if next_state.worker in next_state.boxes:
                box_index = next_state.boxes.index(next_state.worker)
                next_state.boxes[box_index] = ((next_state.worker[0]-1, next_state.worker[1]))
        elif action == 'Up':
            next_state.worker = (next_state.worker[0], next_state.worker[1]-1)
            if next_state.worker in next_state.boxes:
                box_index = next_state.boxes.index(next_state.worker)
                next_state.boxes[box_index] = ((next_state.worker[0], next_state.worker[1]-1))
        elif action == 'Down':
            next_state.worker = (next_state.worker[0], next_state.worker[1]+1)
            if next_state.worker in next_state.boxes:
                box_index = next_state.boxes.index(next_state.worker)
                next_state.boxes[box_index] = ((next_state.worker[0], next_state.worker[1]+1))
        return next_state
        #boxes are resetting to oringinal posistion, once moved they stay there
        
    def goal_test(self, state):
        """Return True if the state is a goal. The default method compares the
        state to self.goal, as specified in the constructor. Override this
        method if checking against a single self.goal is not enough."""
        if (self.ignore_box):
            if (self.exit):
                return True
            else:
                return state.worker == self.goal
        
        return sorted(state.boxes) == sorted(self.goal)


    def solution_path(self, goal_node):
        # path is list of nodes from initial state (root of the tree)
        # to the goal_node
        if (self.ignore_box and self.exit):
            return 'Impossible'
        else:
            if (goal_node != None):
                Message = ''
                path = goal_node.path()
                action_seq = []
                # print the solution
                Message += str("Solution takes {0} steps from the initial state\n".format(len(path)-1))
                Message += str(path[0].state)
                Message += str("\nto the goal state\n")
                Message += str(path[-1].state)
                Message += str("\nBelow is the sequence of moves\n")
                for node in path:
                    if node.action is not None:
                        action_seq.append(node.action)
                return Message + str(action_seq)
            return 'Impossible'
    
    def path_cost(self, c, state1, action, state2):
        """Return the cost of a solution path that arrives at state2 from
        state1 via action, assuming cost c to get up to state1. If the problem
        is such that the path doesn't matter, this function will only look at
        state2.  If the path does matter, it will consider c and maybe state1
        and action. The default method costs 1 for every step in the path."""
        return c + 1

    def h(self, node):
        if (self.ignore_box):
            return distance_between_two_points(node.state.worker, self.goal) + (random()/10)
        else:
            total_distance = 0
            temp_lowest_distance = None
            temp_pair = None
            used_box = []
            used_target = []
            distance_list = [(distance_between_two_points(box, target), box, target)
                for box in set(node.state.boxes) 
                for target in set(node.state.targets)]

            for box in set(node.state.boxes):
                for distance, box, target in distance_list:
                    if (temp_lowest_distance == None) :
                        temp_lowest_distance = distance
                        temp_pair = (box, target)
                    elif (distance <= temp_lowest_distance):
                        temp_lowest_distance = distance
                        temp_pair = (box, target)
                
                if (temp_pair != None):
                    used_box.append(temp_pair[0])
                    used_target.append(temp_pair[1])
                    
                    total_distance +=  temp_lowest_distance
                    temp_lowest_distance = None

                    distance_list = [(distance_between_two_points(box, target), box, target)
                        for box in set(node.state.boxes)
                        if box not in used_box
                        for target in set(node.state.targets)
                        if target not in used_target
                        ]
                # add a small random number be because
                # in search.py the PriorityQueue doesn't like it 
                # when two nodes have the same f value 
                # and it throws an error. So adding a small random number
                # will give nodes with the same value a random order
            return total_distance + (random()/10)

    #in sokoban.py from Warehouse __str__ method
    def state_to_string(self, state):
        '''
        Return a string representation of the warehouse
        '''
        ##        x_size = 1+max(x for x,y in self.walls)
        ##        y_size = 1+max(y for x,y in self.walls)
        X,Y = zip(*state.walls) # pythonic version of the above
        x_size, y_size = 1+max(X), 1+max(Y)
        
        vis = [[" "] * x_size for y in range(y_size)]
        # can't use  vis = [" " * x_size for y ...]
        # because we want to change the characters later
        for (x,y) in state.walls:
            vis[y][x] = "#"
        for (x,y) in state.targets:
            vis[y][x] = "."
        # if worker is on a target display a "!", otherwise a "@"
        # exploit the fact that Targets has been already processed
        if vis[state.worker[1]][state.worker[0]] == ".": # Note y is worker[1], x is worker[0]
            vis[state.worker[1]][state.worker[0]] = "!"
        else:
            vis[state.worker[1]][state.worker[0]] = "@"
        # if a box is on a target display a "*"
        # exploit the fact that Targets has been already processed
        for (x,y) in state.boxes:
            if vis[y][x] == ".": # if on target
                vis[y][x] = "*"
            else:
                vis[y][x] = "$"
        return "\n".join(["".join(line) for line in vis])

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def check_elem_action_seq(warehouse, action_seq):
    '''
    
    Determine if the sequence of actions listed in 'action_seq' is legal or not.
    
    Important notes:
      - a legal sequence of actions does not necessarily solve the puzzle.
      - an action is legal even if it pushes a box onto a taboo cell.
        
    @param warehouse: a valid Warehouse object

    @param action_seq: a sequence of legal actions.
           For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
           
    @return
        The string 'Impossible', if one of the action was not successul.
           For example, if the agent tries to push two boxes at the same time,
                        or push one box into a wall.
        Otherwise, if all actions were successful, return                 
               A string representing the state of the puzzle after applying
               the sequence of actions.  This must be the same string as the
               string returned by the method  Warehouse.__str__()
    '''
    sp = SokobanPuzzle(warehouse)
    #checks if each action is in the list of possible actions in that given state
    #uses SokobanPuzzle.actions
    state = warehouse
    for action in list(action_seq):
        actions = sp.actions(state)
        if action not in actions:
            return 'Impossible'
        else:
            state = sp.result(state,action)
        
    return sp.state_to_string(state)


# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_sokoban_elem(warehouse):
    '''    
    This function should solve using A* algorithm and elementary actions
    the puzzle defined in the parameter 'warehouse'.
    
    In this scenario, the cost of all (elementary) actions is one unit.
    
    @param warehouse: a valid Warehouse object

    @return
        If puzzle cannot be solved return the string 'Impossible'
        If a solution was found, return a list of elementary actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
    '''
    problem = SokobanPuzzle(warehouse)
    print('start search')
    t0 = time.time()
    #solution = search.breadth_first_graph_search(problem)
    solution = search.astar_graph_search(problem)
    t1 = time.time()
    print ("Solver took ",t1-t0, ' seconds')
    
    #if goal is found print solution
    if solution != None:
        return problem.solution_path(solution)
    return 'Impossible'
    

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def can_go_there(warehouse, dst):
    '''    
    Determine whether the worker can walk to the cell dst=(row,column) 
    without pushing any box.
    
    @param warehouse: a valid Warehouse object

    @return
      True if the worker can walk to cell dst=(row,column) without pushing any box
      False otherwise
    '''
    # use astar search to find way next to the box

    problem = SokobanPuzzle(warehouse, goal = dst, ignore_box=True)
    print('start search')
    t0 = time.time()
    solution = search.astar_graph_search(problem)
    t1 = time.time()
    print ("Solver took ",t1-t0, ' seconds')
    print(problem.solution_path(solution))
    if(problem.solution_path(solution) != 'Impossible'):
        return True
    return False

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_sokoban_macro(warehouse):
    '''    
    Solve using using A* algorithm and macro actions the puzzle defined in 
    the parameter 'warehouse'. 
    
    A sequence of macro actions should be 
    represented by a list M of the form
            [ ((r1,c1), a1), ((r2,c2), a2), ..., ((rn,cn), an) ]
    For example M = [ ((3,4),'Left') , ((5,2),'Up'), ((12,4),'Down') ] 
    means that the worker first goes the box at row 3 and column 4 and pushes it left,
    then goes to the box at row 5 and column 2 and pushes it up, and finally
    goes the box at row 12 and column 4 and pushes it down.
    
    In this scenario, the cost of all (macro) actions is one unit. 

    @param warehouse: a valid Warehouse object

    @return
        If the puzzle cannot be solved return the string 'Impossible'
        Otherwise return M a sequence of macro actions that solves the puzzle.
        If the puzzle is already in a goal state, simply return []
    '''
    
    ##         "INSERT YOUR CODE HERE"
    #take the goal node and plug it in as warehouse
    #or make action into something
    
    raise NotImplementedError()

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def solve_weighted_sokoban_elem(warehouse, push_costs):
    '''
    In this scenario, we assign a pushing cost to each box, whereas for the
    functions 'solve_sokoban_elem' and 'solve_sokoban_macro', we were 
    simply counting the number of actions (either elementary or macro) executed.
    
    When the worker is moving without pushing a box, we incur a
    cost of one unit per step. Pushing the ith box to an adjacent cell 
    now costs 'push_costs[i]'.
    
    The ith box is initially at position 'warehouse.boxes[i]'.
        
    This function should solve using A* algorithm and elementary actions
    the puzzle 'warehouse' while minimizing the total cost described above.
    
    @param 
     warehouse: a valid Warehouse object
     push_costs: list of the weights of the boxes (pushing cost)

    @return
        If puzzle cannot be solved return 'Impossible'
        If a solution exists, return a list of elementary actions that solves
            the given puzzle coded with 'Left', 'Right', 'Up', 'Down'
            For example, ['Left', 'Down', Down','Right', 'Up', 'Down']
            If the puzzle is already in a goal state, simply return []
    '''
    
    raise NotImplementedError()
wh = sokoban.Warehouse()
wh.load_warehouse("./warehouses/warehouse_07.txt")
#taboo_cells(wh)

puzzle = SokobanPuzzle(wh)
print(check_elem_action_seq(wh,["Up",'Right','Up','Up','Left','Left','Up']))
#print(solve_sokoban_elem(wh))
#print(wh)
#print(can_go_there(wh, (3,1)))

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

