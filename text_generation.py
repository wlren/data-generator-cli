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
def generate_text_column(column, size, seed, minLength=DEFAULT_MIN_LENGTH, maxLength=DEFAULT_MAX_LENGTH):
    ans = []
    isUnique = column.get("isUnique", False)
    random.seed(seed)
    for i in range(size):
        ans.append(generate_random_string(minLength, maxLength))
    return ans