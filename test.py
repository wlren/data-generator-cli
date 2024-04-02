from itertools import product

def generate_composite_key_permutations(pk_data_set):
    """
    Generate all possible permutations for a composite primary key based on foreign key values.

    Parameters:
    - pk_data_set: A dictionary where keys are foreign key references (or tuples for composite keys)
                   and values are lists of possible values for these keys.

    Returns:
    - A list of tuples, each representing a unique permutation of the composite primary key.
    """
    # Prepare lists for the Cartesian product
    lists_to_combine = []

    for fk_ref, values in pk_data_set.items():
        # If the foreign key reference is composite (a tuple), values are already in the right format
        if isinstance(fk_ref, tuple):
            lists_to_combine.append(values)
        else:
            # For a simple key, ensure the values are wrapped in a list to maintain consistency
            lists_to_combine.append(values)
    
    # Generate and return the Cartesian product of the lists
    return list(product(*lists_to_combine))

# Example usage
pk_data_set = {
    ('key1', 'key2'): [(1, 'a'), (2, 'b'), (3, 'c')],
    'key3': ['x', 'y', 'z']
}

permutations = generate_composite_key_permutations(pk_data_set)
for perm in permutations:
    print(perm)
