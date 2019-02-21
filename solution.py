assignments = []

def cross(a, b):
    "Cross product of elements in A and elements in B."
    return [s+t for s in a for t in b]

rows = 'ABCDEFGHI'
cols = '123456789'
cols_reverse = cols[::-1]
boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diaglona1_units = [[rows[i]+cols[i] for i in range(len(rows))]]
diagonal2_units = [[rows[i]+cols_reverse[i] for i in range(len(rows))]]


unitlist = row_units + column_units + square_units + diaglona1_units + diagonal2_units

def extract_units(unitlist,boxes):
    units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
    return units

def extract_peers(units,boxes):
    peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)
    return peers

# Must be called after all units (including diagonals) are added to the unitlist
units = extract_units(unitlist, boxes)
peers = extract_peers(units, boxes)


def naked_twins(values):
    """Eliminate values using the naked twins strategy.

    The naked twins strategy says that if you have two or more unallocated boxes
    in a unit and there are only two digits that can go in those two boxes, then
    those two digits can be eliminated from the possible assignments of all other
    boxes in the same unit.

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

    See Also
    --------
    Pseudocode for this algorithm on github:
    https://github.com/udacity/artificial-intelligence/blob/master/Projects/1_Sudoku/pseudocode.md
    """
    for unit in unitlist:
        values_in_unit = [values[element] for element in unit]
        dictionary_unit = dict(zip(unit, values_in_unit))
        inv_dict = {}
        for key, value in dictionary_unit.items():
            inv_dict.setdefault(value, []).append(key)
        inverse_twin_dictionary = {key: value for key, value in inv_dict.items() if len(value) == 2 and len(key) == 2}

        # create a list of unsolved boxes in that unit
        boxes_unsolved = [key for key in dictionary_unit.keys() if len(dictionary_unit[key]) > 1]

        # check the value of any unsolved box (exclude twin boxes)
        # if a digit is in any twin box, delete that digit from the unsolved box value
        for tv, tb in inverse_twin_dictionary.items():
            for boxUnsolved in boxes_unsolved:
                if boxUnsolved not in tb:
                    for v in tv:
                        # values[unsolved_box] = values[unsolved_box].replace(digit, '')
                        newV = values[boxUnsolved].replace(v, '')
                        values[boxUnsolved] = newV
    return values


def convertGrid(grid):
    v = [];
    all = '123456789'

    for n in grid:
        if n == '.':
            v.append(all);
        else:
            v.append(n);
    return v;

def grid2values(grid):
    return dict(zip(boxes, convertGrid(grid)))

def display(values):
    """
    Display the values as a 2-D grid.
    Input: The sudoku in dictionary form
    Output: None
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    print

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """
    singleValue = [box for box in values.keys() if len(values[box]) == 1]
    for box in singleValue:
        v = values[box]
        for peer in peers[box]:
            values[peer] = values[peer].replace(v,'')
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                values[dplaces[0]] = digit
    return values


def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    stalled = False
    while not stalled:
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)

        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        stalled = solved_values_before == solved_values_after
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    "Using depth-first search and propagation, create a search tree and solve the sudoku."
    # First, reduce the puzzle using the previous function
    values = reduce_puzzle(values)
    if values == False:
        return False

    if all(len(values[s]) == 1 for s in boxes):
        return values ## Solved!

    n,s = min((len(values[s]), s) for s in boxes if len(values[s]) > 1)
    for value in values[s]:
        new_sudoku = values.copy()
        new_sudoku[s] = value
        attempt = search(new_sudoku)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
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
