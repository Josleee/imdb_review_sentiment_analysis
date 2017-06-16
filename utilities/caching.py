import json
import traceback


def dump_to_file(caching_data, filename, directory):
    """
    Save data to file.

    :param caching_data:
    :param filename:
    :param directory:
    :return:
    """

    with open('../' * directory + 'data/' + filename + '.json', 'w') as f:
        json.dump(caching_data, f)


def read_from_file(filename, directory):
    """
    Read data from file.
    :param filename:
    :param directory:

    :return:
    """

    caching_data = {}

    with open('../' * directory + 'data/' + filename + '.json', 'r') as f:
        try:
            caching_data = json.load(f)
        # if the file is empty the ValueError will be thrown
        except ValueError:
            traceback.print_exc()
        finally:
            return caching_data
