from special_types import SpecialTypes
import pandas as pd
import os


def generate_special_data(column, num_rows, seed):
    if 'specialType' in column and  hasattr(SpecialTypes, column['specialType']):
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
