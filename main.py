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
        primary_key = table["primary_key"]
    
        # # Composite key handling
        if len(primary_key) > 1:
            primary_key_data = gen.generate_composite_key_data(primary_key, table, seed)
            for key in primary_key_data:
                column_data[key] = primary_key_data[key]

        
        for column in table["columns"]:
            if column["fieldName"] in primary_key and len(primary_key) > 1:
                next
            elif column["fieldName"] in primary_key:
                column_data[column["fieldName"]] = gen.generate_primary_key_data(column, table, seed)
            elif 'specialType' in column:
                column_data[column["fieldName"]] = gen.generate_special_data(column, table, seed)
            else:
                column_data[column["fieldName"]] = gen.generate_column_data(column, table, seed)

        df = pd.DataFrame(column_data)

        IOHandler.writeCSV(output_directory_path, df, table_name, exclude_header)
    
if __name__ == '__main__':
    main()