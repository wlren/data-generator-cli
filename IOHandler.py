import argparse
import json
import os
import csv

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

def writeCSV(output_directory_path, df, table_name, excludeHeader):
    os.makedirs(output_directory_path, exist_ok=True)
    output_path = os.path.join(output_directory_path, f"{table_name}.csv")
    df.to_csv(output_path, index=False, header = not excludeHeader)
    print(f"Table {table_name} written to {output_path}")

# if pks are [id, name], returns all possible combinations in [ [id1, id2, ...], [name1, name2, ...] ]
def read_csv_get_primary_keys(input_file_path: str, primary_key: list[str]) -> list[list[str]]:
    with open(input_file_path, newline='') as csvfile:
        reader: list[str] = csv.reader(csvfile, delimiter=',')

        # read in headers, get primary key indexes in array
        headers: list[str] = next(reader)
        pk_indexes: list[int] = []
        buckets = {}
        for i, h in enumerate(headers):
            if h in primary_key:
                pk_indexes.append(i)
                buckets[i] = []
        
        # stores arrays of primary keys
        for row in reader:
            for i in pk_indexes:
                buckets[i].append(row[i])
        
        pks = []
        for i in pk_indexes:
            pks.append(buckets[i])
        return pks
    