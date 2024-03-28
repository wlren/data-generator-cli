import pandas as pd

from toposort import topological_sort
import IOHandler
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
    input_file_path, seed, output_directory_path, exclude_header = args.input_file_path, args.seed, args.output_directory_path, args.exclude_header

    
    tables = generator_json_data["tables"]
    table_order = topological_sort(generator_json_data)

    # output each table name and its column in a different csv file
    for table in tables:
        table_name = table["tableName"]
        # for column in table["columns"]:
        #     if column["specialType"]:
        #         pass
        
        if not exclude_header:
            column_names = [column["fieldName"] for column in table["columns"]]
        else:
            column_names = None

        df = pd.DataFrame(columns=column_names)
        IOHandler.writeCSV(output_directory_path, df, table_name)
    

if __name__ == '__main__':
    main()