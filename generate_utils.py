import math
import os
import pandas as pd
import numpy as np
import distribution
import text_generation
import IOHandler

from special_types import SpecialTypes
import json
CONSTRAINTS_BY_TYPE = {
    'text': set(['minLength', 'maxLength']),
    'int': set(['min', 'max']),
    'float': set(['min', 'max']),
    'boolean': set([])
}

NUMERIC_TYPES = ['int', 'float', 'date']

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

def meet_numeric_constraints(datum, constraints):
    for constraint in constraints:
        if constraint == 'min':
            min_val = constraints[constraint]
            if datum < min_val:
                return False
        elif constraint == 'max':
            max_val = constraints[constraint]
            if datum > max_val:
                return False
    return True

def meet_constraints(data_type, datum, constraints):
    if data_type == 'text':
        return meet_text_constraints(datum, constraints)
    elif data_type in NUMERIC_TYPES:
        return meet_numeric_constraints(datum, constraints)
    else:
        raise ValueError(f"Data type {data_type} not recognized")

# Necessary to filter out special data that doesn't meet normal type constraints
# e.g. for an email, user can specify max length to be 10, but the txt file may have emails with length > 10
def get_allowable_special_data(column, special_data):
    data_normal_type = column['type']
    allowable_constraints = CONSTRAINTS_BY_TYPE[data_normal_type]
    for constraint in column.get('constraints', {}):
        if constraint not in allowable_constraints:
            raise ValueError(f"Constraint {constraint} not allowed for type {data_normal_type}")
    
    constraints = column.get('constraints', {})
    if not constraints:
        return special_data
    
    allowable_data = list(filter(lambda datum: meet_constraints(data_normal_type, datum, constraints), special_data))

    return allowable_data

def generate_special_data(column, table, seed):
    if not hasattr(SpecialTypes, column['specialType']):
        raise ValueError(f"Special type {column['specialType']} not recognized")
    
    special_type = SpecialTypes[column['specialType']]
    normal_type = column['type']
    if not special_type.has_matching_normal_type(normal_type):
        raise ValueError(f"Special type {column['specialType']} must have type {special_type.get_normal_type()}. Got {normal_type}")

    special_filepath = os.path.join('special_data', f"{column['specialType']}.txt")
    with open(special_filepath, 'r') as file:
        special_data = file.readlines()
    special_data = [special_type.convert_to_normal_type(line.strip()) for line in special_data]
    
    isUnique = column.get("isUnique", False)
    isNullable = column.get("isNullable", True)
    percentageNull = column.get("percentageNull", 0)
    if not isNullable and percentageNull > 0:
        raise ValueError("Column is not nullable but percentageNull > 0")

    isRepeatable = not isUnique
    num_rows = table['numRows']
    
    numRowsToSample = math.floor(num_rows * (1 - percentageNull))
    numNullRows = num_rows - numRowsToSample
    # sample random row indexes to be null from 0 to num_rows - 1
    nullRowIndexes = set(pd.Series(range(num_rows)).sample(n=numNullRows, random_state=seed, replace=False).tolist())
    # make sure data meets constraints
    allowable_data = get_allowable_special_data(column, special_data)
    
    if len(allowable_data) < numRowsToSample:
        raise ValueError(f"Insufficient data for special type {column['specialType']} to meet constraints. Num allowable data: {len(allowable_data)}, num rows to sample: {numRowsToSample}")

    sampled_data = pd.Series(allowable_data).sample(n=numRowsToSample, random_state=seed, replace=isRepeatable).tolist()
    result = []
    for i in range(num_rows):
        if i in nullRowIndexes:
            result.append("null")
        else:
            result.append(sampled_data.pop())
    return result

def generate_composite_key_data(primary_keys, table, seed):
    return []

# Handles FK check
def generate_primary_key_data(column, table, seed):
    is_special = 'specialType' in column
    column.isUnique = True
    column.isNullable = False
    
    if is_special:
        return generate_special_data(column, table, seed)
    
    
    
    return

def generate_column_data(column, table, seed):
    columnType = column["type"]
    
    # isUnique = column.get("isUnique", False) This is difficult, what if the user wants uniform distribution min max with unique values
    isNullable = column.get("isNullable", False)
    percentageNull = column.get("percentageNull", 0)
    if not isNullable and percentageNull > 0:
        raise ValueError("Column is not nullable but percentageNull > 0")
    rows = table["numRows"]
    numRowsToSample = math.floor(rows * (1 - percentageNull))
    if is_number_type(columnType):
        sampled_answer_row = distribution.generate_integer_distribution(column, numRowsToSample)
    elif columnType == "text":
        args = {}
        if "constraints" in column:
            args = column["constraints"]
        sampled_answer_row = text_generation.generate_text_column(numRowsToSample, **args)
    
    if isNullable:
        null_array = ["null" for i in range(rows - numRowsToSample)]
        string_list = [str(item) for item in sampled_answer_row]
        final_result_array = null_array + string_list
        np.random.shuffle(final_result_array)
        return final_result_array
    return sampled_answer_row

def is_number_type(type):
    return type == "integer" or type == "float"

def is_foreign_key(table_schema, column_name):
    if "foreign_key" in table_schema:
        for fk in table_schema["foreign_key"]:
            if column_name in fk["fieldName"]:
                return (True, len(fk["fieldName"]))
    return (False, 0)

def get_foreignkey_data_set(foreign_table: str, column_name: list[str], output_folder: str):
    pks: list[list[str]] = IOHandler.read_csv_get_primary_keys(f"{output_folder}/{foreign_table}.csv", column_name)


if __name__ == '__main__':
    column = {
                    "fieldName": "name",
                    "type": "text",
                    # "isUnique": True,
                    "isNullable": True,
                    "percentageNull": 0.2,
                    "constraints": {
                        "minLength": 1,
                        "maxLength": 5
                    }
                }
    column2 = {
                    "fieldName": "name",
                    "type": "integer",
                    # "isUnique": True,
                    "isNullable": False,
                    "distribution":{
                        "type": "uniform",
                        "min": 10,
                        "max": 100
                    }
                }
    print(generate_column_data(column2, {"numRows": 100}, 0))
