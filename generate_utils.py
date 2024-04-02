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
def generate_column_data(column, table, seed, reference=None):
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
        reference_extended = reference
        while numRowsToSample > len(reference):
            reference_extended += reference
        sampled_answer_row = random.sample(reference_extended, numRowsToSample)
    else:
        # TODO: This should use seed to generate
        if is_number_type(columnType):
            sampled_answer_row = distribution.generate_number_column(column, numRowsToSample, seed)
        elif columnType == "text":
            args = {}
            if "constraints" in column:
                args = column["constraints"]
            sampled_answer_row = text_generation.generate_text_column(numRowsToSample, seed, **args)

    if isNullable:
        null_array = ["null" for i in range(rows - numRowsToSample)]
        string_list = [str(item) for item in sampled_answer_row]
        final_result_array = null_array + string_list
        np.random.seed(seed)
        np.random.shuffle(final_result_array)
        return final_result_array

    return sampled_answer_row

def generate_special_data(column, table, seed, reference=None):
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
        reference_extended = reference
        while numRowsToSample > len(reference):
            reference_extended += reference
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
    if "foreign_key" in table and check_if_field_in_foreignkey(
        table, column["fieldName"]
    ):
        other_table_values = get_foreignkey_data_values(table, output_dir_path)
        # extra check for FK, if our column X is a FK referencing other column Y,
        # and if len(X) > len(Y) while X is a PK, that should be invalid
        # as we do not have enough unique values to maintain the unique property
        if len(other_table_values) < table["numRows"]:
            raise ValueError("Generating PK failed, references another table but not enough unique values!")

    if is_special:
        return generate_special_data(column, table, seed, other_table_values)
    else:
        return generate_column_data(column, table, seed, other_table_values)

def generate_foreign_key_data(column, table, seed, output_dir_path):
    is_special = "specialType" in column
    column["isUnique"] = True
    column["isNullable"] = False

    # if this PK is a FK to some other table, that means we need to use their values
    other_table_values = []
    if "foreign_key" in table and check_if_field_in_foreignkey(
        table, column["fieldName"]
    ):
        other_table_values = get_foreignkey_data_values(table, output_dir_path)

    if is_special:
        return generate_special_data(column, table, seed, other_table_values)
    else:
        return generate_column_data(column, table, seed, other_table_values)

def generate_composite_pkey_data(pks, table, seed):
    return

def generate_composite_fkey_data(fks, table, seed, output_folder, isUnique=False):
    fieldNames = fks["fieldName"]
    references = fks["references"]
    foreign_table = fks["tableName"]
    num_rows = table["numRows"]
    
    reference_to_fieldNames = { references[i]: fieldNames[i] for i in range(len(fieldNames)) }
    # TODO Composite fkey can have isNullable/percentageNull
    # TODO isUnique need to check len to see if possible
    # C[f_a, f_b] 1000 unique
    # A[p_a, p_b] 100
    
    foreign_table_data = get_foreignkey_data_set(foreign_table, references, output_folder)
    random.seed(seed)
    added = set()
    result = { fieldNames[i]: [] for i in range(len(fieldNames)) }
    for i in range(num_rows):
        # { 'fieldName': [data], 'fieldName2': [data]}
        index = random.int(0, len(foreign_table_data[fieldNames[0]]) - 1)
        if isUnique:
            while index in added:
                index = random.int(0, len(foreign_table_data[fieldNames[0]]) - 1)
        added.add(index)

        for key in foreign_table_data.keys():
            fieldName = reference_to_fieldNames[key]
            result[fieldName].append(foreign_table_data[key][index])

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
    return (False, [])

def check_if_field_in_foreignkey(table, field):
    foreign_keys = table.get("foreign_key", [])
    for f in foreign_keys:
        if f.get("fieldName", [""])[0] == field:
            return True
    return False

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

def get_foreignkey_data_values(table, output_dir_path):
    # guaranteed to be single pk by if-else order, but just check
    if len(table["foreign_key"]) > 1:
        raise ValueError(
            "Composite PK detected when trying to generate single PK as a FK!"
        )
    foreign_table = table["foreign_key"][0]["tableName"]# @ryan its not always guranteed to be referencing the first fk
    foreign_table_pk = table["foreign_key"][0]["references"]
    pks = get_foreignkey_data_set(foreign_table, foreign_table_pk, output_dir_path)
    other_table_values = pks.get(foreign_table_pk[0])# @ryan isnt this a dictionary?
    return other_table_values
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
