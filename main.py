import pandas as pd

from toposort import topological_sort
import IOHandler
import random
import numpy as np
import generate_utils as gen
# TODO: check if column in a foreign key, if so, cannot define isNullable in column, define in foreign key object instead

def init_generator():
    args = IOHandler.get_parser().parse_args()
    print(f"Processing file: {args.input_file_path} with seed {args.seed}")
    
    generator_json_data = IOHandler.get_json_data(args.input_file_path)
    return generator_json_data, args

def main():
    generator_json_data, args = init_generator()
    seed, output_directory_path = args.seed, args.output_directory_path
    random.seed(seed)
    np.random.seed(seed)
    tables = generator_json_data["tables"]
    table_order = topological_sort(generator_json_data)

    # output each table name and its column in a different csv file
    for table_name in table_order:
        for tableObject in tables:
            if tableObject["tableName"] == table_name:
                table = tableObject
                break

        column_data = {}
        primary_key = table["primary_key"]
        foreign_keys = table.get("foreign_keys", [])

        # Single key
        for column in table["columns"]:

            column_name = column["fieldName"]

            if column_name in column_data:
                continue

            # Composite PK
            if column_name in primary_key and len(primary_key) > 1:
                composite_pk = handle_composite_pk_data(table, seed, primary_key, output_directory_path, column_data)
                
                for name, data in composite_pk.items():
                    column_data[name] = data
                    
                # for name, data in composite_pk.items():
                #     if len(name) == 1:
                #         column_data[name] = data
                #     else:
                #         for i in range(len(name)):
                #             column_data[name[i]] = data[i]

            #Composite FK
            elif gen.is_foreign_key(table, column_name)[0] and len(gen.is_foreign_key(table, column_name)[1]['fieldName']) > 1:
                composite_fk = handle_composite_fk_data(table, seed, gen.is_foreign_key(table, column_name)[1], output_directory_path)
                
                for name, data in composite_fk.items():
                    column_data[name] = data
            #Single PK (+ FK if total participation)
            elif column_name in primary_key:
                column_data[column_name] = gen.generate_primary_key_data(column, table, seed, output_directory_path)
            # Single FK
            elif gen.is_foreign_key(table, column_name)[0]:
                column_data[column_name] = gen.generate_foreign_key_data(
                    column, table, seed, output_directory_path, gen.is_foreign_key(table, column_name)[1])
            # Speical type
            elif 'specialType' in column:
                column_data[column_name] = gen.generate_special_data(column, table, seed)
            # Normal type
            else:
                result = gen.generate_column_data(column, table, seed)
                column_data[column_name] = result

        df = pd.DataFrame(column_data)

        IOHandler.writeCSV(output_directory_path, df, table_name)
  
  
def handle_composite_pk_data(table, seed, primary_key, output_directory_path, column_data):
    pk_data_set = {}
    generated = set()
    for pk in primary_key:
        if pk in column_data or pk in generated:
            continue
        
        is_foreign_key = gen.is_foreign_key(table, pk)[0]
        fk_object = gen.is_foreign_key(table, pk)[1]
        
        if is_foreign_key:
            # # composite total participation  
            # if len(fk_object['fieldName']) == len(primary_key):
            #     fk_object["isNullable"] = False
            #     fk_object["percentageNull"] = 0
            #     fk_object["isUnique"] = True
            #     foreign_key_data = gen.generate_composite_fkey_data(fk_object, table, seed, output_directory_path)
                
            #     for name in foreign_key_data.key():
            #         generated.add(name)
                    
            #     fk_composite = tuple(foreign_key_data.keys())
            #     fk_data = [foreign_key_data[name] for name in fk_composite]
                
            #     pk_data_set[fk_composite] = fk_data
                
            # Composite FK in PK
            if len(fk_object['fieldName']) > 1:
                fieldNames = fk_object["fieldName"]
                references = fk_object["references"]
                foreign_table_data = gen.get_foreignkey_data_set(fk_object["tableName"], references, output_directory_path)
                fieldNames_to_references = { fieldNames[i]: references[i] for i in range(len(fieldNames)) }
                
                for name in fieldNames:
                    generated.add(name)
                fk_composite = tuple(fieldNames)
                fk_data = [foreign_table_data[fieldNames_to_references[name]] for name in fk_composite]
                
                pk_data_set[fk_composite] = fk_data
                
            # part of PK is single FK
            elif len(fk_object['fieldName']) == 1:
                fk_object["isNullable"] = False
                fk_object["percentageNull"] = 0
                references = fk_object["references"]
                pk_data_set[pk] = gen.get_foreignkey_data_set(fk_object["tableName"], references, output_directory_path)[references[0]]
                generated.add(pk)
        else:
            curr_column = None
            for column in table["columns"]:
                if column["fieldName"] == pk:
                    curr_column = column
                    break
            pk_data_set[pk] = gen.generate_primary_key_data(curr_column, table, seed, output_directory_path)
            generated.add(pk)
        
    return gen.generate_composite_pkey_data(pk_data_set, primary_key, table["numRows"], seed)

def handle_composite_fk_data(table, seed, fk_object, output_directory_path):
    foreign_key_data = gen.generate_composite_fkey_data(fk_object, table, seed, output_directory_path)
    return foreign_key_data

if __name__ == '__main__':
    main()
