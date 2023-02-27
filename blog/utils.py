import string
import random
import re

def generate_slug(count=10, letters=string.ascii_letters, digits=string.digits):
    alphanumeric = letters + digits
    result = ''
    
    for c in range(count):
        result += random.choice(alphanumeric)
        if c % 5 == 0:
            result += random.choice('_-')
        
    return result

def remove_non_alphanumeric(input_string):
    # Define a regular expression pattern to match all non-alphanumeric characters
    pattern = r'[^\sa-zA-Z0-9]'

    # Use re.sub to replace all non-alphanumeric characters with an empty string
    output_string = re.sub(pattern, '', input_string)

    return output_string


def slugify(chars):
    alphanumeric = remove_non_alphanumeric(chars)
    slug = re.sub(r'\s', '-', alphanumeric)
    
    return slug

def title_as_slug(title):
    return slugify(title)[:20] + generate_slug(20)