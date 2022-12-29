from scipy.linalg import solve

def find_pivot_row_and_column(tableau, obj_row):
    """
    Helper function that finds the labels for
    the pivot row and column in a tableau

    Args:
        tableau (dataframe): dataframe storing the tableau information
        obj_row (str): label of the row you want to optimize

    Returns:
        list of strs: [pivot_row,pivot_column] 
    """
    pivot_column = -1

    # searches for largest negative num negative number in row of interest
    obj_row = tableau.loc[obj_row].to_dict()
    obj_row.pop('b')
    pivot_column = min(obj_row, key=obj_row.get)
    
    #  Get the pivot column and b'
    pivot_column_index = list(obj_row.keys()).index(pivot_column)
    pivot_column_nums = tableau.iloc[:, [pivot_column_index,-1]].T.to_dict('list')

    # Removes z, z_prime, and negative rows in the pivot column 
    non_neg_rows = dict((key, value) for key, value in pivot_column_nums.items() if value[0] >= 0 and key not in ['z','z_prime'])
    
    # Calculates the ratios for each valid row
    ratios = dict((key, value[1] / value[0]) for key, value in non_neg_rows.items() if value[0] > 0)
    
    # deterimine pivot row based on smallest ratio
    pivot_row =  min(ratios, key=ratios.get)

    print("Pivot Column:", pivot_column, "    Pivot Row:", pivot_row, "    Pivot #:", round(tableau.loc[pivot_row,pivot_column],2))
    
    # returns the labels for the pivot row and column
    return [pivot_row,pivot_column]


# Helper function that pivots the tableau
def pivot_tableau(tableau, pivot_row, pivot_column):
    """
    Helper function to pivot tableau based on pivot row and column

    Args:
        tableau (dataframe): dataframe storing the tableau information
        pivot_row (str): label of the pivot row (e.g. "z","x1")
        pivot_column (str): label of the pivot column (e.g. "z" "z_prime" "x3" "x6")

    Returns:
        dataframe: pivoted dataframe with the new tableau information
    """

    pivot_number = tableau.loc[pivot_row,pivot_column]
    temp_tableau = tableau.copy(deep=True)

    # Loop through the rows, and pivot if needed
    for i,row in enumerate(temp_tableau.index.tolist()):
        number_in_row = temp_tableau.loc[row,pivot_column]

        if number_in_row == 0:
            print(f"    R{i}: No pivot needed for {row} row")
            continue
        elif row == pivot_row:
            print(f"    R{i}: PIVOT ROW {row}, new label is {pivot_column}")
            continue
        else:
            multiplier = -number_in_row / pivot_number
            temp_tableau.loc[row] = temp_tableau.loc[row] + multiplier*temp_tableau.loc[pivot_row]
            print(f"    R{i}: {row} <-- {row} + ({round(multiplier,2)})*{pivot_row}")
    
    temp_tableau.rename(index={pivot_row:pivot_column},inplace=True)

    return temp_tableau

def determine_values(tableau):
    """
    helper function that solves the Ax = b linear problem
    to get the values for the basic variables

    Args:
        tableau (dataframe): dataframe storing the tableau information

    Returns:
        dict: dictionary for the value of all non zero variables including z and z_prime
    """
    basic_var = [x for x in tableau.index.tolist() if x not in ['z','z_prime','b']]
    basic_var = [x for x in basic_var if x[0] == 'x' or x[0] == 'z']
    zero_var = [x for x in tableau.columns.tolist() if x not in ['z','z_prime','b'] + basic_var]
    print(f"Basic Vars: {basic_var}")
    print(f"Zero Vars: {zero_var}")

    rows = [x for x in tableau.index.tolist() if x[0] in ['x','z']]
    columns = rows + ['b']

    reduced_mat = tableau.loc[rows, columns]

    A = reduced_mat.iloc[:,:-1]
    b = reduced_mat.iloc[:,-1]

    x = solve(A, b)

    return dict(zip(rows,x))      
