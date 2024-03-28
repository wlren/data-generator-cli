import argparse
import json

# Create the parser
def get_parser():
    parser = argparse.ArgumentParser(description='Process some files.')

    # Add the arguments
    parser.add_argument('-i', '--in', dest='input_file_path', help='Input file', type=str,required=True)
    parser.add_argument('-s', '--seed', dest='seed', help='Random seed', type=int, default=42)
    # TODO: decide how to structure output files -- maybe one per table?
    # parser.add_argument('-o', '--out', dest='output_file', help='Output file', default='output.csv')

    return parser

def main():
    # Parse the arguments
    parser = get_parser()
    args = parser.parse_args()

    # Parse input json file
    input_file_path = args.input_file_path
    if not input_file_path.endswith('.json'):
        raise ValueError('Input file must be a json file')
    with open(input_file_path, 'r') as file:
        data = json.load(file)
    
    seed = args.seed

    # Your script can now use args.input_file as the input file name
    print(f"Processing file: {args.input_file_path} with seed {seed}")

if __name__ == '__main__':
    main()