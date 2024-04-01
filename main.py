import pandas as pd

from toposort import topological_sort
import IOHandler
import generate_utils as gen
# SpecialTypes.PERSON_EMAIL.name for string representation

def init_generator():
    # Parse command line arguments
    args = IOHandler.get_parser().parse_args()
    print(f"Processing file: {args.input_file_path} with seed {args.seed}")

    # Parse input json file
    generator_json_data = IOHandler.get_json_data(args.input_file_path)
    return generator_json_data, args

def main():
    generator_json_data, args = init_generator()
    seed, output_directory_path, exclude_header = args.seed, args.output_directory_path, args.exclude_header

    tables = generator_json_data["tables"]
    table_order = topological_sort(generator_json_data)

    # output each table name and its column in a different csv file
    for table_name in table_order:
        for tableObject in tables:
            if tableObject["tableName"] == table_name:
                table = tableObject
                break

        column_data = {}
        print(table)
        primary_key = []
        foreign_keys = []
        if "primary_key" in table:
            primary_key = table["primary_key"] 
        if "foreign_keys" in table:
            foreign_keys = table["foreign_keys"]
        
        # Single key
        for column in table["columns"]:
            column_name = column["fieldName"]
            if column_name in column_data:
                continue
            #Composite PK
            if column_name in primary_key and len(primary_key) > 1:
                composite_pk = handle_composite_pk_data(column, table, seed, primary_key)
            #Composite FK
            elif gen.is_foreign_key(table, column_name)[0] and gen.is_foreign_key(table, column_name)[1] > 1:
                composite_fk = handle_composite_fk_data(column, table, seed, foreign_keys)
            #Single PK (+ FK if total participation)
            elif column_name in primary_key:
                column_data[column_name] = gen.generate_primary_key_data(column, table, seed)
            #Single FK
            elif gen.is_foreign_key(table, column_name)[0]:
                column_data[column_name] = gen.generate_foreign_key_data(column, table, seed)
            #Speical type
            elif 'specialType' in column:
                column_data[column_name] = gen.generate_special_data(column, table, seed)
            #Normal type
            else:
                column_data[column_name] = gen.generate_column_data(column, table, seed)

        df = pd.DataFrame(column_data)

        IOHandler.writeCSV(output_directory_path, df, table_name, exclude_header)
  
  
def handle_composite_pk_data(column, table, seed, primary_key):
    # Check if pk is part of fk, if so, generate entire fk and return entire fk
    primary_key_data = gen.generate_composite_key_data(primary_key, table, seed)
    # if pk not in any fk, generate pk data
    return primary_key_data

def handle_composite_fk_data(column, table, seed, foreign_keys):
    # just generate fk data
    foreign_key_data = gen.generate_composite_key_data(foreign_keys, table, seed)

    return foreign_key_data

if __name__ == '__main__':
    main()