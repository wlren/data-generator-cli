import argparse
import json
import os

import pandas as pd


SPECIAL_TYPES = set(['PERSON_NAME', 'PERSON_EMAIL'])

# Create the parser
def get_parser():
    parser = argparse.ArgumentParser(description='Process some files.')

    # Add the arguments
    parser.add_argument('-i', '--in', dest='input_file_path', help='Input file', type=str, required=True, default='input/sample.json')
    parser.add_argument('-s', '--seed', dest='seed', help='Random seed', type=int, default=42)
    parser.add_argument('-o', '--out', dest='output_folder', help='Output folder', default='output')

    return parser

def get_json_data(input_file_path):
    if not input_file_path.endswith('.json'):
        raise ValueError('Input file must be a json file')
    with open(input_file_path, 'r') as file:
        data = json.load(file)

    return data

def main():
    # Parse the arguments
    parser = get_parser()
    args = parser.parse_args()
    seed = args.seed
    output_folder = args.output_folder
    os.makedirs(output_folder, exist_ok=True)

    # Parse input json file
    data = get_json_data(args.input_file_path)
    tables = data["tables"]
    # output each table name and its column in a different csv file
    for table in tables:
        table_name = table["tableName"]
        # for column in table["columns"]:
        #     if column["specialType"]:
        #         pass
                
        column_names = [column["fieldName"] for column in table["columns"]]
        output_path = os.path.join(output_folder, f"{table_name}.csv")
        df = pd.DataFrame(columns=column_names)
        df.to_csv(output_path, index=False)
        print(f"Table {table_name} written to {output_path}")

    print(f"Processing file: {args.input_file_path} with seed {seed}")

if __name__ == '__main__':
    main()