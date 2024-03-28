import math
import os
import pandas as pd

from special_types import SpecialTypes

CONSTRAINTS_BY_TYPE = {
    'text': set(['minLength', 'maxLength']),
    'int': set(['min', 'max'])
}

def meet_text_constraints(datum, constraints):
    for constraint in constraints:
        if constraint == 'minLength':
            minLength = constraints[constraint]
            if len(datum) < minLength:
                return False
        elif constraint == 'maxLength':
            maxLength = constraints[constraint]
            if len(datum) > maxLength:
                return False
    return True

def meet_constraints(data_type, datum, constraints):
    if data_type == 'text':
        return meet_text_constraints(datum, constraints)
    elif data_type == 'int':
        # return meet_int_constraints(datum, constraints)
        pass
    else:
        raise ValueError(f"Data type {data_type} not recognized")

def get_allowable_data(column, special_data):
    data_normal_type = column['type']
    allowable_constraints = CONSTRAINTS_BY_TYPE[data_normal_type]
    for constraint in column.get('constraints', {}):
        if constraint not in allowable_constraints:
            raise ValueError(f"Constraint {constraint} not allowed for type {data_normal_type}")
    
    constraints = column.get('constraints', {})
    if not constraints:
        return special_data

    allowable_data = []
    for data in special_data:
        if not meet_constraints(data_normal_type, data, constraints):
            continue
        allowable_data.append(data)

    return allowable_data

def generate_special_data(column, num_rows, seed):
    if 'specialType' in column and not hasattr(SpecialTypes, column['specialType']):
        raise ValueError(f"Special type {column['specialType']} not recognized")

    special_filepath = os.path.join('special_data', f"{column['specialType']}.txt")
    with open(special_filepath, 'r') as file:
        special_data = file.readlines()
    special_data = [line.strip() for line in special_data]  # Remove newlines
    isUnique = column.get("isUnique", False)
    isNullable = column.get("isNullable", False)
    percentageNull = column.get("percentageNull", 0)
    if not isNullable and percentageNull > 0:
        raise ValueError("Column is not nullable but percentageNull > 0")
    isRepeatable = not isUnique
    numRowsToSample = math.floor(num_rows * (1 - percentageNull))
    numNullRows = num_rows - numRowsToSample
    # sample random row indexes to be null from 0 to num_rows - 1
    nullRowIndexes = set(pd.Series(range(num_rows)).sample(n=numNullRows, random_state=seed, replace=False).tolist())
    # make sure data meets constraints
    allowable_data = get_allowable_data(column, special_data)

    sampled_data = pd.Series(allowable_data).sample(n=numRowsToSample, random_state=seed, replace=isRepeatable).tolist()
    result = []
    for i in range(num_rows):
        if i in nullRowIndexes:
            result.append("null")
        else:
            result.append(sampled_data.pop())
    return result