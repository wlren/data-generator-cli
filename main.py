import argparse
import json
import os

import numpy as np

SPECIAL_TYPES = set(['PERSON_NAME', 'PERSON_EMAIL'])

def get_parser():
    parser = argparse.ArgumentParser(description='Process some files.')

    # Add the arguments
    parser.add_argument('-i', '--in', dest='input_file_path', help='Input file', type=str,required=True)
    parser.add_argument('-o', '--out', dest='output_directory_path', help='Output directory', type=str, default='output')
    parser.add_argument('-s', '--seed', dest='seed', help='Random seed', type=int, default=42)
    # TODO: decide how to structure output files -- maybe one per table?

    return parser

def get_json_data(input_file_path):
    if not input_file_path.endswith('.json'):
        raise ValueError('Input file must be a json file')
    with open(input_file_path, 'r') as file:
        data = json.load(file)

    return data

def generate_sample_data(column, num_rows, seed):
    if column['specialType'] not in SPECIAL_TYPES:
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
            df[column["fieldName"]] = generate_sample_data(column, num_rows, seed)
        else:
            # Generate placeholder data if no specialType is provided
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
    if not input_file_path.endswith('.json'):
        raise ValueError('Input file must be a json file')

    # Parse input json file
    generator_json_data = get_json_data(input_file_path)
    tables = generator_json_data["tables"]
    # output each table name and its column in a different csv file
    for table in tables:
        generate_table_data(table, output_directory_path, seed)


if __name__ == '__main__':
    main()