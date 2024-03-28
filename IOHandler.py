import argparse
import json
import os

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

def writeCSV(output_directory_path, df, table_name):
    os.makedirs(output_directory_path, exist_ok=True)
    output_path = os.path.join(output_directory_path, f"{table_name}.csv")
    df.to_csv(output_path, index=False)
    print(f"Table {table_name} written to {output_path}")