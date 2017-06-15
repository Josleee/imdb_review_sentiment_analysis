import json
import traceback


def dump_to_file(caching_data):
    """
    Save data to file.

    :param caching_data:
    :return:
    """

    with open('data/data.json', 'w') as f:
        json.dump(caching_data, f)


def read_from_file():
    """
    Read data from file.

    :return:
    """

    caching_data = {}

    with open('data/data.json', 'r') as f:
        try:
            caching_data = json.load(f)
        # if the file is empty the ValueError will be thrown
        except ValueError:
            traceback.print_exc()
        finally:
            return caching_data
