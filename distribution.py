import numpy as np
import math
def generate_normal_distribution(mean, stddev, rows):
    data = np.random.normal(mean, stddev, size=rows)
    return list(data)
class IntegerColumn:
    DEFAULT_MIN_VALUE = -100000000
    DEFAULT_MAX_VALUE = 1000000000
    def __init__(self, isUnique, distribution_field, min_value, max_value):
        self.distribution_field = distribution_field
        self.min_value = min_value
        self.max_value = max_value
        self.isUnique = isUnique

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
            if self.isUnique:
                num_possible_unique_vals = self.max_value - self.min_value + 1
                if num_possible_unique_vals < rows:
                    raise TypeError(f"Too much unique values, possible: {num_possible_unique_vals}, rows requested {rows}")
                return self.generate_unique_integers(self.min_value, self.max_value, rows)
            else:
                return np.random.randint(low=self.min_value, high=self.max_value, size=rows)

            
    
    
    def generate_unique_integers(self, min_value, max_value, rows):
        threshold = 0.9
        if rows < threshold * (max_value - min_value + 1):
            unique_integers = set()
            while len(unique_integers) < rows:
                # Attempt to add a new unique integer
                unique_integers.add(np.random.randint(low=min_value, high=max_value + 1))
            return np.array(list(unique_integers))
        else:
            # If the number of rows is close to the total number of values, generate the full range and shuffle
            all_values = np.arange(min_value, max_value + 1)
            np.random.shuffle(all_values)
            return all_values[:rows]



class FloatColumn:
    DEFAULT_MIN_VALUE = -100000000.0
    DEFAULT_MAX_VALUE = 1000000000.0
    DEFAULT_DECIMAL_POINT = 2
    def __init__(self, isUnique, distribution_field, min_value, max_value, decimal_point=DEFAULT_DECIMAL_POINT):
        self.distribution_field = distribution_field
        self.min_value = min_value
        self.max_value = max_value
        self.decimal_point = decimal_point
        self.isUnique = isUnique

    def generate_data(self, rows):
        # If distribution has min max, then the constraints:{min, max} will be overriden
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
            if self.isUnique:
                data = self.generate_unique_floats(rows, self.decimal_point, self.min_value, self.max_value)
            else:
                data = np.random.uniform(low=self.min_value, high=self.max_value, size=rows)
        #Rounding to decimal point    
        data = [format(datum, f'.{self.decimal_point}f') for datum in data]
        return data
    
    def generate_unique_floats(self, rows, dp, min_value=DEFAULT_MIN_VALUE, max_value=DEFAULT_MAX_VALUE):
        threshold = 0.9
        step = 1/(10**dp)
        numPossibleValues = (max_value - min_value) / step + 1
        if numPossibleValues < rows:
            raise TypeError(f"Too many rows requested :{rows}, {numPossibleValues}")
        if rows < threshold * numPossibleValues:
            unique_floats = set()
            while len(unique_floats) < rows:
                # Attempt to add a new unique float
                unique_floats.add(np.round(np.random.uniform(low=min_value, high=max_value+step), dp))
            return np.array(list(unique_floats))
        else:
            # If the number of rows is close to the total number of values, generate the full range and shuffle
            all_values = np.arange(min_value, max_value + step, step=step)
            np.random.shuffle(all_values)
            return all_values[:rows]


def enforce_distribution_field_structure(distribution_field):
    constraints_map = {
        "normal": ["mean", "stddev"],
        "uniform": ["min", "max"]
    }
    dist_type = distribution_field["type"]
    constraints = constraints_map.get(dist_type, [])
    return all(cs in distribution_field for cs in constraints)

def is_number_type(type):
    return type == "integer" or type == "float"

def generate_number_column(column, rows):
    if not is_number_type(type=column["type"]):
        raise TypeError("Invalid column type")
    distribution_field = {}
    constraints = column.get("constraints", {})

    # #Set the seed for np
    # np.random.seed(seed=seed)

    if "distribution" in column:
        distribution_field = column.get("distribution", {})
        is_valid = enforce_distribution_field_structure(distribution_field)
        if not is_valid:
            raise SyntaxError("Wrong syntax for distribution")
    isUnique = column.get("isUnique", False)
    if column["type"] == "integer":
        return IntegerColumn(isUnique, distribution_field, constraints.get("min", IntegerColumn.DEFAULT_MIN_VALUE), constraints.get("max", IntegerColumn.DEFAULT_MAX_VALUE)).generate_data(rows)
    elif column["type"] == "float":
        dp = column.get("decimal_point", FloatColumn.DEFAULT_DECIMAL_POINT)
        return FloatColumn(isUnique, distribution_field, constraints.get("min", FloatColumn.DEFAULT_MIN_VALUE), constraints.get("max", FloatColumn.DEFAULT_MAX_VALUE), dp).generate_data(rows)
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
