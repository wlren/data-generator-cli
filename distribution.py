import numpy as np
import math


def generate_normal_distribution(mean, stddev, rows):
    data = np.random.normal(mean, stddev, size=rows)
    return list(data)
class IntegerColumn:
    DEFAULT_MIN_VALUE = -100000000
    DEFAULT_MAX_VALUE = 1000000000
    def __init__(self, distribution_field, min_value, max_value):
        self.distribution_field = distribution_field
        self.min_value = min_value
        self.max_value = max_value

    def generate_data(self, rows):
        distribution_type = self.distribution_field.get("type", "default")
        if distribution_type == "uniform":
            min = self.distribution_field["min"]
            max = self.distribution_field["max"]
            return np.random.randint(low=min, high=max, size=rows)
        elif distribution_type == "normal":
            mean = self.distribution_field["mean"]
            stddev = self.distribution_field["stddev"]
            data = generate_normal_distribution(mean, stddev, rows)
            return [int(x) for x in data]
        else:
            return np.random.randint(low=self.min_value, high=self.max_value + 1, size=rows)



class FloatColumn:
    DEFAULT_MIN_VALUE = -100000000
    DEFAULT_MAX_VALUE = 1000000000
    DEFAULT_DECIMAL_POINT = 2
    def __init__(self, distribution_field, min_value, max_value, decimal_point=DEFAULT_DECIMAL_POINT):
        self.distribution_field = distribution_field
        self.min_value = min_value
        self.max_value = max_value
        self.decimal_point = decimal_point

    def generate_data(self, rows):
        distribution_type = self.distribution_field.get("type", "default")
        data = []
        if distribution_type == "uniform":
            min = self.distribution_field["min"]
            max = self.distribution_field["max"]
            data = np.random.uniform(low=min, high=max, size=rows)
        elif distribution_type == "normal":
            mean = self.distribution_field["mean"]
            stddev = self.distribution_field["stddev"]
            data = generate_normal_distribution(mean, stddev, rows)
        else:
            data = np.random.uniform(low=self.DEFAULT_MIN_VALUE, high=self.DEFAULT_MAX_VALUE, size=rows)
        data = np.around(data, decimals=self.decimal_point)
        return data


def enforce_distribution_field_structure(distribution_field):
    constraints_map = {
        "normal": ["mean", "stddev"],
        "uniform": ["min", "max"],
        "binomial": ["n", "p"]
    }
    dist_type = distribution_field["type"]
    constraints = constraints_map.get(dist_type, [])
    return all(cs in distribution_field for cs in constraints)

def is_number_type(type):
    return type == "integer" or type == "float"

def generate_number_column(column, rows, seed):
    if not is_number_type(type=column["type"]):
        raise TypeError("Invalid column type")
    distribution_field = {}
    constraints = column.get("constraints", {})
    #Set the seed for np
    np.random.seed(seed=seed)
    if "distribution" in column:
        distribution_field = column.get("distribution", {})
        is_valid = enforce_distribution_field_structure(distribution_field)
        if not is_valid:
            raise SyntaxError("Wrong syntax for distribution")

    if column["type"] == "integer":
        return IntegerColumn(distribution_field, constraints.get("min", IntegerColumn.DEFAULT_MIN_VALUE), distribution_field.get("max", IntegerColumn.DEFAULT_MAX_VALUE)).generate_data(rows)
    elif column["type"] == "float":
        dp = column.get("decimal_point", FloatColumn.DEFAULT_DECIMAL_POINT)
        return FloatColumn(distribution_field, constraints.get("min", FloatColumn.DEFAULT_MIN_VALUE), distribution_field.get("max", FloatColumn.DEFAULT_MAX_VALUE), dp).generate_data(rows)
    else:
        raise TypeError("Invalid number type: only float / integer")
        

if __name__ == '__main__':
    test = {
        "fieldName": "age",
        "type": "float",
        "distribution": {
            "type": "uniform",
            "min": 10,
            "max": 20
        }
    }

    # print(generate_number_column(test, 10))