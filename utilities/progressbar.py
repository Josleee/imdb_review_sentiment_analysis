# -*- coding: utf-8 -*-
import sys
from time import sleep


def print_progress(iteration, total, prefix='', suffix='', decimals=1, bar_length=100):
    """
    Print iterations progress.
    Call in a loop to create terminal progress bar.
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        bar_length  - Optional  : character length of bar (Int)
    """

    str_format = "{0:." + str(decimals) + "f}"
    percents = str_format.format(100 * (iteration / float(total)))
    filled_length = int(round(bar_length * iteration / float(total)))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)

    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percents, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()


if __name__ == '__main__':
    items = list(range(0, 9))
    for index, item in enumerate(items):
        sleep(0.5)
        print_progress(index + 1, len(items), 'Progress:', 'Complete', 1, 50)
