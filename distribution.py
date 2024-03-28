import numpy as np

def generate_normal_distribution(mean, stddev, rows):
    data = np.random.normal(mean, stddev, size=rows)
    return data
def generate_uniform_integer_distribution(min, max, rows):
    ans = []
    for i in range(rows):
         rand_int = np.random.randint(low=min, high=max)
         ans.append(rand_int)
    return ans
def generate_uniform_decimal_distribution(min, max, rows):
    ans = []
    np.random.uniform(low=min, high=max, size = rows)
    return ans

if __name__ == '__main__':
    print("HAHA")