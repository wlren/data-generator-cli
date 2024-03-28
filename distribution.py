import numpy as np
import math
import matplotlib.pyplot as plt
MAX_NUMBER = 100000000
MIN_NUMBER = 0
def generate_normal_distribution(mean, stddev, rows):
    data = np.random.normal(mean, stddev, size=rows)
    return list(data)
def generate_uniform_integer_distribution(min, max, rows):
    ans = []
    for i in range(rows):
         rand_int = np.random.randint(low=min, high=max)
         ans.append(rand_int)
    return ans
def generate_uniform_decimal_distribution(min, max, rows):
    ans = np.random.uniform(low=min, high=max, size = rows)
    return list(ans)
def generate_random_numbers(type, size):
    if type == "integer":
        return np.random.randint(MIN_NUMBER, MAX_NUMBER, size=size)
    else:
        return generate_uniform_decimal_distribution(MIN_NUMBER, MAX_NUMBER, size)
    

def generate_distribution(column, rows):
    number_type = ["integer", "float"]
    # Given an integer / decimal type column output a list of integer with the specified constraints of the column
    if column["type"] not in number_type:
        raise TypeError("Not of integer type")
    
    if "distribution" in column:
        distribution_field = column["distribution"]
        isValidNumberDistribution = enforce_distribution_field_structure(distribution_field=distribution_field)
        if not isValidNumberDistribution:
            raise TypeError("Wrong distribution structure")
        number_type = column["type"]
        distribution_type = distribution_field["type"]
        if distribution_type == "normal":
            mean = distribution_field.get("mean")
            stddev = distribution_field.get("stddev")
            if number_type == "float":
                return generate_normal_distribution(mean, stddev, rows)
            else:
                nd = list(generate_normal_distribution(mean, stddev, rows))
                int_normal = list(map(lambda x: math.floor(x), nd))
                return int_normal
        elif distribution_type == "uniform":
            min = distribution_field.get("min")
            max = distribution_field.get("max")
            if number_type == "float": 
                return generate_uniform_decimal_distribution(min, max, rows)
            elif number_type == "integer":
                return generate_uniform_integer_distribution(min, max, rows)
        else:
            return []
    else:
        type = column["type"]
        return generate_random_numbers(type, rows)
        

        

def enforce_distribution_field_structure(distribution_field):
    constraints_map = {
        "normal": ["mean", "stddev"],
        "uniform": ["min", "max"],
        "binomial": ["n", "p"]
    }
    dist_type = distribution_field["type"]
    constraints = constraints_map.get(dist_type, [])
    ans = True
    for cs in constraints:
        if cs not in distribution_field:
            return False
    return ans





if __name__ == '__main__':
    test = {
         "fieldName": "age",
         "type": "float",
       }

    print(generate_distribution(test, 500))
    # List of unsorted numbers
    data = generate_distribution(test,500)