import search 
import sokoban

def distance_between_two_points(point1, point2):
    x_distance = abs(point1[0] - point2[0])
    y_distance = abs(point1[1] - point2[1])

    return x_distance + y_distance

boxes = [(10,11),(10,12),(10,13),(10,14),(10,15)]
targets = [(12,11),(10,12),(10,13),(10,14),(10,15)]

def h(boxes, targets):
    #h here is the acummulated distance between each set of box and target pairs
    total_distance = 0
    temp_distance = 100
    temp_target = 0
    taken_target = []
    for box in boxes:
        for target in targets:
            if(target not in taken_target):
                distance = distance_between_two_points(box, target)
                if (distance < temp_distance):
                    temp_distance = distance
                    temp_target = target
        total_distance += temp_distance
        taken_target.append(temp_target)
        temp_distance = 100
    return total_distance
#print(h(boxes, targets))


def h2(node):
    print(node.boxes)
    print(node.targets)
    total_distance = 0
    temp_lowest_distance = None
    temp_pair = None
    used_box = []
    used_target = []
    distance_list = [(distance_between_two_points(box, target), box, target)
        for box in set(node.boxes) 
        for target in set(node.targets)]

    for box in set(node.boxes):
        
        print(distance_list)
        print('-------------------------\n')
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
                for box in set(node.boxes)
                if box not in used_box
                for target in set(node.targets)
                if target not in used_target
                ]
    return total_distance

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

    #took this from sokoban.py in the __str__ function
    def str_warehouse():
        X,Y = zip(*warehouse.walls) # pythonic version of the above
        x_size, y_size = 1+max(X), 1+max(Y)
        vis = [[" "] * x_size for y in range(y_size)]

        for (x,y) in warehouse.walls:
            vis[y][x] = "#"
        for (x,y) in taboo_cells:
            vis[y][x] = "X"
        return "\n".join(["".join(line) for line in vis])

    warehouse.taboo_cells = taboo_cells
    return str_warehouse()
    
wh = sokoban.Warehouse()
wh.load_warehouse("./warehouses/warehouse_25.txt")

wh2 = wh
wh3 = wh.copy()
wh3.boxes = wh3.boxes.copy()

#wh2.boxes[0]=(wh.worker[0],wh.worker[1]-1)

print(taboo_cells(wh))
print(wh)