import pandas as pd

from toposort import topological_sort
import IOHandler
import distribution
from generate_utils import generate_special_data
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
        for column in table["columns"]:
            numRows = table["numRows"]
            if 'specialType' in column:
                # Generate data for columns with a specialType
                column_data[column["fieldName"]] = generate_special_data(column, numRows, seed)
            elif is_number_type(column["type"]):
                column_data[column["fieldName"]] = distribution.generate_distribution(column, numRows)
            else:
                # Placeholder for generating data for other types of columns
                # This part needs to be implemented based on column specifications
                pass

        df = pd.DataFrame(column_data)

        IOHandler.writeCSV(output_directory_path, df, table_name, exclude_header)
    
def is_number_type(type):
    return type == "integer" or type == "float"

if __name__ == '__main__':
    main()