import argparse
import json
import os

import pandas as pd


SPECIAL_TYPES = set(['PERSON_NAME', 'PERSON_EMAIL'])

def get_parser():
    parser = argparse.ArgumentParser(description='Process some files.')

    # Add the arguments
    parser.add_argument('-i', '--in', dest='input_file_path', help='Input file', type=str,required=True)
    parser.add_argument('-o', '--out', dest='output_directory_path', help='Output directory', type=str, required=True, default='output')
    parser.add_argument('-s', '--seed', dest='seed', help='Random seed', type=int, default=42)
    # TODO: decide how to structure output files -- maybe one per table?

    return parser

def get_json_data(input_file_path):
    if not input_file_path.endswith('.json'):
        raise ValueError('Input file must be a json file')
    with open(input_file_path, 'r') as file:
        data = json.load(file)

    return data

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
        table_name = table["tableName"]
        # for column in table["columns"]:
        #     if column["specialType"]:
        #         pass
                
        column_names = [column["fieldName"] for column in table["columns"]]
        output_path = os.path.join(output_directory_path, f"{table_name}.csv")
        df = pd.DataFrame(columns=column_names)
        df.to_csv(output_path, index=False)
        print(f"Table {table_name} written to {output_path}")

if __name__ == '__main__':
    main()