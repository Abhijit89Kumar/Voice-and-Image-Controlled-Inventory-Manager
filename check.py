import logging
from loggings import log_function_call


@log_function_call
def example_function():
    return "This is an example function"
    # Example function
    # logging.info("This is an example log message from the example_function")
    # logging.warning("This is a warning message from the example_function")

if __name__ == "__main__":
    example_function()


# def generate_unique_id(object_name):
#         # Calculate ASCII sum of characters in object name
#         ascii_sum = ''.join(str(ord(char)) for char in object_name)

#         # Increase the length of the ID by appending additional unique digits
#         if len(ascii_sum) < 10:
#             # Add unique digits at the end to make it 10 characters long
#             ascii_sum += ''.join(str(random.randint(0, 9)) for _ in range(10 - len(ascii_sum)))

#         # Take the first 10 characters
#         unique_id = ascii_sum[:5]+ascii_sum[-5:]
#         return unique_id
# generate_unique_id("M1")


