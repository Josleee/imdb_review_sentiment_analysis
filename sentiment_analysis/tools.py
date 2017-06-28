import matplotlib.pyplot as plt
import numpy as np

from sentiment_analysis import constant


def negation_cues_cal(sentence):
    """
    Calculate the negative polarity of sentence

    :param sentence:
    :return: if return true, polarity does not change; if return false, polarity does change
    """

    polarity = True

    for cue in constant.negation_cues_set:
        for word in sentence:
            if cue == word.lower_:
                polarity = not polarity

    for word in sentence:
        if 'n\'t' in word.lower_:
            polarity = not polarity

    return polarity


def display_word_frequency_distribution(list_y_values, all_data=True):
    """
    Plot word frequency rate distribution figure

    :param list_y_values:
    :param all_data: if not pass this variable, the instantly plot the figure; otherwise or False,
            wait for next calling with the variable set to be True or default
    :return:
    """

    if not list_y_values:
        return

    for item in list_y_values:
        x = np.array(range(1, 11), np.int32)
        y = np.array(item['list'], np.float)
        plt.plot(x, y, label='fit-' + item['key_word'] if item['fitted'] is True else item['key_word'])
        plt.xlabel('Rating (stars)')
        plt.ylabel('Frequency rate (%)')

    if all_data:
        plt.legend()
        plt.show()


def fit_curve(list_y_values):
    """
    Fit the frequency rate distribution using curves

    :param list_y_values:
    :return:
    """

    if not list_y_values:
        return

    fit_list_y_values = []

    for item in list_y_values:
        x = np.array(range(1, 11), np.int32)
        y = np.array(item['list'], np.float)

        z = np.polyfit(x, y, 3)
        f = np.poly1d(z)
        # fit_x = np.linspace(x[0], x[-1], 50)
        # fit_y = f(fit_x)
        fit_y = f(x)
        non_negation_list = [0 if i < 0 else i for i in fit_y.tolist()]

        fit_list_y_values.append({'key_word': item['key_word'], 'pos_type': item['pos_type'],
                                  'list': non_negation_list, 'fitted': True})

    return fit_list_y_values


def calculate_relative_scores(list_y_values):
    """
    Calculate relative scores by y values

    :param list_y_values:
    :return:
    """

    if not list_y_values:
        return

    list_scored = []

    for item in list_y_values:
        min_value = float(min(item['list'])) if min(item['list']) > 0.05 else float(0.05)
        max_value = max(item['list'])
        score = (max_value / min_value) if (max_value / min_value) < 10 else 10

        list_scored.append({'key_word': item['key_word'], 'pos_type': item['pos_type'],
                            'list': [v / max_value * score for v in item['list']], 'fitted': True})

    return list_scored


def data_std(list_y_values):
    for item in list_y_values:
        np.std(item['list'])
