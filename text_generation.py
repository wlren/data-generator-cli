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

def generate_text_column(column, rows, minLength=DEFAULT_MIN_LENGTH, maxLength=DEFAULT_MAX_LENGTH):
    isUnique = column.get("isUnique", False)
    if isUnique and not has_enough_unique_strings(minLength, maxLength, rows):
        raise TypeError(f"Number of row to be generated is less than the possible values rows: {rows} length = {maxLength - minLength}")

    if isUnique:
        ans = set()
        while(len(ans) < rows):
            ans.add(generate_random_string(minLength, maxLength))
    
        return list(ans)
    else:
        return [generate_random_string(minLength, maxLength) for _ in range(rows)]

# directly calculate the power assuming maxLength 
def has_enough_unique_strings(minLength, maxLength, rowsToBeGenerated):
    print("haha")
    minLength = max(minLength, 0)
    maxLength = max(maxLength, 0)
    char_set_length = len(string.ascii_letters + string.digits)

    if (maxLength == 0):
        return rowsToBeGenerated <= 1
    
    num_possible_strings = sum(char_set_length ** length for length in range(minLength, maxLength + 1))

    print(f"num_possible_strings: {num_possible_strings}")
    return num_possible_strings >= rowsToBeGenerated
