from collections import defaultdict
from itertools import product
import math
import os
from random import random
import pandas as pd
import IOHandler
import random
import numpy as np
import distribution
import text_generation
from special_types import SpecialTypes

'''
Constraint helpers START
'''
CONSTRAINTS_BY_TYPE = {
    'text': set(['minLength', 'maxLength']),
    'int': set(['min', 'max']),
    'float': set(['min', 'max']),
    'boolean': set([])
}

NUMERIC_TYPES = ['int', 'float', 'date']

def is_number_type(type):
    return type == "integer" or type == "float"

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

'''
Constraint helpers END
'''


'''
Data generation functions START
'''
def generate_column_data(
    column,
    table,
    seed,
    fk_col_name: str = None,
    reference = None,
):
    columnType = column["type"]
    # isUnique = column.get("isUnique", False) This is difficult, what if the user wants uniform distribution min max with unique values
    isNullable = column.get("isNullable", False)
    percentageNull = column.get("percentageNull", 0)
    if not isNullable and percentageNull > 0:
        raise ValueError("Column is not nullable but percentageNull > 0")
    rows = table["numRows"]
    numRowsToSample = math.floor(rows * (1 - percentageNull))

    if reference:
        random.seed(seed)
        # kind of hackish edge case, but eg if we ref column X which only has x rows,
        # and if our curr column Y has y rows st y > x, we have to make sure our arr to sample from is long enough
        reference_extended = reference[fk_col_name]
        while numRowsToSample > len(reference_extended):
            reference_extended += reference[fk_col_name]
        sampled_answer_row = random.sample(reference_extended, numRowsToSample)
    else:
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


def generate_special_data(
    column, table, seed, fk_col_name: str = None, reference = None
):
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

    if reference:
        random.seed(seed)
        reference_extended = reference[fk_col_name]
        while numRowsToSample > len(reference):
            reference_extended += reference[fk_col_name]
        sampled_data = random.sample(reference_extended, numRowsToSample)
    else:
        special_filepath = os.path.join('special_data', f"{column['specialType']}.txt")
        with open(special_filepath, 'r') as file:
            special_data = file.readlines()
        special_data = [line.strip() for line in special_data]

        if not isNullable and percentageNull > 0:
            raise ValueError("Column is not nullable but percentageNull > 0")
        isRepeatable = not isUnique

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


'''
Data generation functions END
'''

'''
Key Columns generation functions START
'''
def generate_primary_key_data(column, table, seed, output_dir_path):
    is_special = "specialType" in column
    column["isUnique"] = True
    column["isNullable"] = False

    # if this PK is a FK to some other table, that means we need to use their values
    other_table_values = None
    truthy, fk = is_foreign_key(table, column["fieldName"])
    if truthy:
        other_table_values = get_foreignkey_data_set(
            fk["tableName"], fk["references"], output_dir_path
        )
        # extra check for FK, if our column X is a FK referencing other column Y,
        # and if len(X) > len(Y) while X is a PK, that should be invalid
        # as we do not have enough unique values to maintain the unique property
        fk_table_name = fk["references"][0]
        if len(other_table_values[fk_table_name]) < table["numRows"]:
            raise ValueError("Generating PK failed, references another table but not enough unique values!")

    if is_special:
        return generate_special_data(
            column,
            table,
            seed,
            fk.get("references", [None])[0],
            other_table_values,
        )
    else:
        return generate_column_data(
            column,
            table,
            seed,
            fk.get("references", [None])[0],
            other_table_values,
        )

def generate_foreign_key_data(column, table, seed, output_dir_path, fk_object):
    is_special = "specialType" in column
    fk_object["isUnique"] = False
    fk_object["isNullable"] = True

    other_table_values = get_foreignkey_data_set(
        fk_object["tableName"], fk_object["references"], output_dir_path
    )

    if is_special:
        return generate_special_data(
            column, table, seed, fk_object.get("references", [None])[0], other_table_values
        )
    else:
        return generate_column_data(
            column, table, seed, fk_object.get("references", [None])[0], other_table_values
        )

def generate_composite_pkey_data(pk_data_set, primary_key, num_rows, seed, threshold = 0.7):
    selected = set()
    res = defaultdict(list)
    random.seed(seed)
    
    total_possible_combinations = 1
    for key, data in pk_data_set.items():
        if isinstance(key, tuple):
            total_possible_combinations *= len(data[0])
        else:
            total_possible_combinations *= len(data)
            
    if num_rows > total_possible_combinations:
        raise ValueError("Not enough combinations to generate all rows for composite primary key")
            
    if num_rows > total_possible_combinations * threshold:
        # generate all possible combinations
        lists_to_combine = []
        for key, data in pk_data_set.items():
            if isinstance(key, tuple):
                values = list(zip(*data))
                lists_to_combine.append(values)
            else:
                lists_to_combine.append([(value,) for value in data])

        cartesian_product = list(product(*lists_to_combine))
        random.shuffle(cartesian_product)
        
        pk_data = list(cartesian_product)[:num_rows]
        for i, key in enumerate(pk_data_set.keys()):
            if isinstance(key, tuple):
                for j in range(len(key)):
                    res[key[j]] = [pk_data[k][i][j] for k in range(num_rows)]
            else :
                res[key] = [pk_data[k][i] for k in range(num_rows)]

    else:
        while len(selected) < num_rows:
            selected_idx = 0
            chosenIndices = (0 for i in range(len(pk_data_set.keys())))
            
            for key, data in pk_data_set.items():
                if isinstance(key, tuple):
                    index = random.randint(0, len(data[0]) - 1)
                    for i in range(len(key)):
                        res[key[i]].append(data[i][index])
                else:
                    index = random.randint(0, len(data) - 1)
                    res[key].append(data[index])

                chosenIndices[selected_idx] = index
                selected_idx += 1
            
            if chosenIndices in selected:
                for key in res.keys():
                    res[key].pop()
                continue
            else:
                selected.add(chosenIndices)
            
        assert(len(primary_key) == len(res.keys()))
    return res

def generate_composite_fkey_data(fk_object, table, seed, output_folder):
    fieldNames = fk_object["fieldName"]
    references = fk_object["references"]
    foreign_table = fk_object["tableName"]
    isUnique = fk_object.get("isUnique", False)
    isNullable = fk_object.get("isNullable", False)
    percentageNull = fk_object.get("percentageNull", 0)
    num_rows = table["numRows"]
    numRowsToSample = math.floor(num_rows * (1 - percentageNull))
    numNullRows = num_rows - numRowsToSample
    nullRowIndexes = set(pd.Series(range(num_rows)).sample(n=numNullRows, random_state=seed, replace=False).tolist())
    
    foreign_table_data = get_foreignkey_data_set(foreign_table, references, output_folder)
    fieldNames_to_references = { fieldNames[i]: references[i] for i in range(len(fieldNames)) }
    result = { fieldNames[i]: [] for i in range(len(fieldNames)) }

    if isUnique and num_rows > len(foreign_table_data[fieldNames[0]]):
        raise ValueError("Composite Foreign Key has isUnique set to True but the referenced table does not have enough unique values")
    
    random.seed(seed)
    added = set()
    
    for i in range(num_rows):
        if i in nullRowIndexes:
            for columnNames in fieldNames:
                result[columnNames].append("null")
            continue
        
        index = random.int(0, len(foreign_table_data[references[0]]) - 1)
        if isUnique:
            while index in added:
                index = random.int(0, len(foreign_table_data[references[0]]) - 1)
        added.add(index)

        for columnName in fieldNames:
            referenceColumn = fieldNames_to_references[columnName]
            result[columnName].append(foreign_table_data[referenceColumn][index])

    return result
'''
Key Columns generation functions END
'''

'''
Foreign Key helpers START
'''
def is_foreign_key(table_schema, column_name):
    if "foreign_key" in table_schema:
        for fk in table_schema["foreign_key"]:
            if column_name in fk["fieldName"]:
                return (True, fk)
    return (False, {})

def get_foreignkey_data_set(
    foreign_table: str, column_name: list[str], output_folder: str
):
    pks: list[list[str]] = IOHandler.read_csv_get_primary_keys(
        f"{output_folder}/{foreign_table}.csv", column_name
    )
    res = {}
    if (len(pks) != len(column_name)):
        raise ValueError("Error when reading PK values from csvs!")
    for i in range(len(column_name)):
        name, pk = column_name[i], pks[i]
        res[name] = pk
    return res

'''
Foreign Key helpers END
'''

# if __name__ == '__main__':
#     column = {
#                     "fieldName": "name",
#                     "type": "text",
#                     # "isUnique": True,
#                     "isNullable": True,
#                     "percentageNull": 0.2,
#                     "constraints": {
#                         "minLength": 1,
#                         "maxLength": 5
#                     }
#                 }
#     print(generate_column_data(column, {"numRows": 100}, 0))
