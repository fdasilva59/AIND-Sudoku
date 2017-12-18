
from utils import *


row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
unitlist = row_units + column_units + square_units

# TODO: Update the unit list to add the new diagonal units
diag1 = [rows[i]+cols[i] for i in range(9)] 
diag2 = [rows[i]+cols[8-i] for i in range(9)]
unitlist = unitlist + [diag1] + [diag2]
assert(len(unitlist)==29) 
assert(['A1', 'B2', 'C3', 'D4', 'E5', 'F6', 'G7', 'H8', 'I9'] in unitlist )
assert(['A9', 'B8', 'C7', 'D6', 'E5', 'F4', 'G3', 'H2', 'I1'] in unitlist )

units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the naked twins eliminated from peers

    Notes
    -----
    Your solution can either process all pairs of naked twins from the input once,
    or it can continue processing pairs of naked twins until there are no such
    pairs remaining -- the project assistant test suite will accept either
    convention. However, it will not accept code that does not process all pairs
    of naked twins from the original input. (For example, if you start processing
    pairs of twins and eliminate another pair of twins before the second pair
    is processed then your code will fail the PA test suite.)

    The first convention is preferred for consistency with the other strategies,
    and because it is simpler (since the reduce_puzzle function already calls this
    strategy repeatedly).
    """
    # TODO: Implement this function!
    
    from collections import Counter
    
    # Loop over each of the puzzle's units
    for unit in unitlist:
        
        # Filter boxes with only 2 possible values 
        len2_values = [box for box in unit if len(values[box]) == 2]
          
        # Search for twins amongs these values (size 2) 
        # Count the nb of occurence for each value
        values_occurence = Counter()
        for box in len2_values:
            values_occurence[values[box]]+=1
  
        # Build a list of twins boxes in the current unit
        twins_values = {box : values[box] for box in len2_values if values_occurence[values[box]]==2}
        
        # If there are twins boxes, 
        if len(twins_values) > 0 : 
            #print('[DEBUG] Found Twins values ', twins_values, 'in unit: ', unit)
            
            # Create an reverse dict of Twins {v: [k]}
            # This will make the things easier to process in case of multiple pair of twins
            revdict={}
            for k,v in twins_values.items():
                revdict.setdefault(v, []).append(k)
            #print(revdict)
            
            # Create a list of box in the unit, excluding the Twins pairs
            for v, k in revdict.items():
                update_unit = [box for box in unit if box not in k ]
                #print("unit to update:" , update_unit)
                # Delete the Twins values from the other possible values in the rest of the unit
                for box in update_unit:
                    for digit in v:
                        values[box] = values[box].replace(digit,'')

                        
    return values
    
    
    


def eliminate(values):
    """Apply the eliminate strategy to a Sudoku puzzle

    The eliminate strategy says that if a box has a value assigned, then none
    of the peers of that box can have the same value.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with the assigned values eliminated from peers
    """
    # TODO: Copy your code from the classroom to complete this function
    
    # Create a list of solved boxes (containing a single value)
    solved = [ box for box in values.keys() if len(values[box]) == 1 ]

    # Loop over the list of solved boxes...
    for box in solved:
        # ... and then Loop over its peers...
        for peer in peers[box]:
            # ... to remove that value from the possible list of values for the peers 
            values[peer]=values[peer].replace(values[box],'')
        
    return values

def only_choice(values):
    """Apply the only choice strategy to a Sudoku puzzle

    The only choice strategy says that if only one box in a unit allows a certain
    digit, then that box must be assigned that digit.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict
        The values dictionary with all single-valued boxes assigned

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    """
   # TODO: Copy your code from the classroom to complete this function
    
    # For each unit in the puzzle (row, column, box) 
    for unit in unitlist:
        # For each digit values
        for digit in '123456789':
            # Build a list of cell ID containing that digit
            digit_location = [box for box in unit if digit in values[box]]
            # if one digit appears only in one single location, then the value must be that digit 
            if len(digit_location)==1:
                values[digit_location[0]] = digit
        
    return values


def reduce_puzzle(values):
    """Reduce a Sudoku puzzle by repeatedly applying all constraint strategies

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary after continued application of the constraint strategies
        no longer produces any changes, or False if the puzzle is unsolvable 
    """
    # TODO: Copy your code from the classroom and modify it to complete this function
    
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        
        # Add Naked-Twins Strategy
        values = naked_twins(values)
        #display(values)
        
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values


def search(values):
    """Apply depth first search to solve Sudoku puzzles in order to solve puzzles
    that cannot be solved by repeated reduction alone.

    Parameters
    ----------
    values(dict)
        a dictionary of the form {'box_name': '123456789', ...}

    Returns
    -------
    dict or False
        The values dictionary with all boxes assigned or False

    Notes
    -----
    You should be able to complete this function by copying your code from the classroom
    and extending it to call the naked twins strategy.
    """
    # TODO: Copy your code from the classroom to complete this function
    "Using depth-first search and propagation, try all possible values."

    # Reduce the puzzle
    values = reduce_puzzle(values)
    if values is False:
        return False ## Failed earlier
    if all(len(values[s]) == 1 for s in boxes): 
        return values ## Solved!
    
    # Choose one of the unfilled squares with the fewest possibilities
    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    
    # Now use recurrence to solve each one of the resulting sudokus, and 
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt


def solve(grid):
    """Find the solution to a Sudoku puzzle using search and constraint propagation

    Parameters
    ----------
    grid(string)
        a string representing a sudoku grid.
        
        Ex. '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'

    Returns
    -------
    dict or False
        The dictionary representation of the final sudoku grid or False if no solution exists.
    """
    values = grid2values(grid)
    values = search(values)
    return values


if __name__ == "__main__":
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(grid2values(diag_sudoku_grid))
    result = solve(diag_sudoku_grid)
    display(result)

    try:
        import PySudoku
        PySudoku.play(grid2values(diag_sudoku_grid), result, history)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
