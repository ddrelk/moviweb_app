import json


def create_file(file_path):
    """This function creates an empty JSON file, if the file does not already exist.
    If the file does exist, it does nothing and continues without raising an error.
    """
    try:
        with open(file_path, 'x') as file:
            json.dump([], file)  # initialize file as empty list
    except FileExistsError:
        pass


def _file_exists(file_path):
    try:
        with open(file_path, 'r'):
            return True
    except FileNotFoundError:
        return False


def initialize(file_path):
    if not _file_exists(file_path):
        create_file(file_path)


def load_from_file(file_path):
    try:
        initialize(file_path)
        with open(file_path, "r") as handle:
            return json.load(handle)
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")


def save_file(file_path, data):
    """
    Saves the given product dict to the file, overwriting what's in the file.
    """
    try:
        with open(file_path, 'w') as file:
            json.dump(data, file)
    except Exception as e:
        print(f"An error occurred while saving JSON data to '{file_path}'.")
        print(f"Error message: {str(e)}")
