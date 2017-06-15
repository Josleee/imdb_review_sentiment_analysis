import json
import traceback


def dump_to_file(caching_data, filename):
    """
    Save data to file.

    :param caching_data:
    :param filename:
    :return:
    """

    with open('data/' + filename + '.json', 'w') as f:
        json.dump(caching_data, f)


def read_from_file(filename):
    """
    Read data from file.
    :param filename:

    :return:
    """

    caching_data = {}

    with open('data/' + filename + '.json', 'r') as f:
        try:
            caching_data = json.load(f)
        # if the file is empty the ValueError will be thrown
        except ValueError:
            traceback.print_exc()
        finally:
            return caching_data
