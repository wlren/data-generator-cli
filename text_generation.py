import random
import string

DEFAULT_MIN_LENGTH = 0
DEFAULT_MAX_LENGTH = 255
def generate_random_string(min_length, max_length):
    """
    Generate a random string of specified minimum and maximum length.

    Parameters:
        min_length (int): Minimum length of the generated string.
        max_length (int): Maximum length of the generated string.

    Returns:
        str: Random string of length between min_length and max_length.
    """
    # Generate a random length between min_length and max_length
    length = random.randint(min_length, max_length)

    # Generate a random string of specified length
    random_string = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

    return random_string
def generate_text_column(column, rows, seed, minLength=DEFAULT_MIN_LENGTH, maxLength=DEFAULT_MAX_LENGTH):
    ans = []
    isUnique = column.get("isUnique", False)
    if not has_enough_unique_strings(minLength, maxLength, rows):
        raise TypeError(f"Number of row to be generated is less than the possible values rows: {rows} length = {maxLength - minLength}")
    random.seed(seed)
    ans = set()
    while(len(ans) < rows):
        # Keep generating until we get number of len
        ans.add(generate_random_string(minLength, maxLength))
    return list(ans)

def has_enough_unique_strings(minLength, maxLength, rowsToBeGenerated):
    num_possible_values = 1
    ascii_char_length = len(string.ascii_letters + string.digits)
    # print(ascii_char_length)
    if(maxLength == 0):
        return rowsToBeGenerated <= 1
    
    num_possible_prev_length = 1
    for _ in range(minLength):
        num_possible_prev_length *= ascii_char_length
        if num_possible_prev_length >= rowsToBeGenerated:
            return True
    
    num_possible_values = num_possible_prev_length
    for _ in range(minLength + 1, maxLength + 1):
        num_possible_values += ascii_char_length * num_possible_prev_length
        if num_possible_values >= rowsToBeGenerated:
            return True
        num_possible_prev_length *= ascii_char_length
    
    print("JALSDHSDHALSHDLSKAD", num_possible_values)
    return False

