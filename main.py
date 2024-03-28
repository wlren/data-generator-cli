import argparse
import json
import os
import pandas as pd

from toposort import topological_sort


SPECIAL_TYPES = set(['PERSON_NAME', 'PERSON_EMAIL'])

def get_parser():
    parser = argparse.ArgumentParser(description='Process JSON input file to generator random data into CSV files.')

    # Add the arguments
    parser.add_argument('-i', '--in', dest='input_file_path', help='Input file', type=str,required=True)
    parser.add_argument('-o', '--out', dest='output_directory_path', help='Output directory', type=str, default='output')
    parser.add_argument('-s', '--seed', dest='seed', help='Random seed', type=int, default=42)
    parser.add_argument('--no-header', action='store_true', dest="exclude_header", help='Exclude column header')
    
    return parser

def get_json_data(input_file_path):
    if not input_file_path.endswith('.json'):
        raise ValueError('Input file must be a json file')
    with open(input_file_path, 'r') as file:
        data = json.load(file)

    return data

def generate_special_data(column, num_rows, seed):
    if 'specialType' in column and column['specialType'] not in SPECIAL_TYPES:
        raise ValueError(f"Special type {column['specialType']} not recognized")

    special_filepath = os.path.join('special_data', f"{column['specialType']}.txt")
    with open(special_filepath, 'r') as file:
        special_data = file.readlines()
    special_data = [line.strip() for line in special_data]  # Remove newlines
    # Use pandas to handle sampling
    sampled_data = pd.Series(special_data).sample(n=num_rows, random_state=seed, replace=True).tolist()
    return sampled_data

def generate_table_data(table, output_directory_path, seed):
    table_name = table["tableName"]
    num_rows = table.get("numRows", 100)  # Default to 100 rows if not specified
    df = pd.DataFrame()
    for column in table["columns"]:
        if "specialType" in column:
            df[column["fieldName"]] = generate_special_data(column, num_rows, seed)
        else:
            # Generate placeholder data if no specialType is provided
            column_type = column["type"]
            # TODO: make functions for each non-special type of data (text, int, boolean etc.)
            df[column["fieldName"]] = [f"{column['fieldName']}_{i+1}" for i in range(num_rows)]

    output_path = os.path.join(output_directory_path, f"{table_name}.csv")
    df.to_csv(output_path, index=False)
    print(f"Table {table_name} written to {output_path}")

def main():
    parser = get_parser()
    args = parser.parse_args()

    input_file_path = args.input_file_path
    seed = args.seed
    output_directory_path = args.output_directory_path
    os.makedirs(output_directory_path, exist_ok=True)
    
    print(f"Processing file: {input_file_path} with seed {seed}")

    # Parse input json file
    generator_json_data = get_json_data(input_file_path)
    tables = generator_json_data["tables"]
    
    table_order = topological_sort(generator_json_data)
    
    # output each table name and its column in a different csv file
    for table in tables:
        table_name = table["tableName"]
        # for column in table["columns"]:
        #     if column["specialType"]:
        #         pass
        
        if not args.exclude_header:
            column_names = [column["fieldName"] for column in table["columns"]]
        else:
            column_names = None
        output_path = os.path.join(output_directory_path, f"{table_name}.csv")
        df = pd.DataFrame(columns=column_names)
        df.to_csv(output_path, index=False)
        print(f"Table {table_name} written to {output_path}")



if __name__ == '__main__':
    main()