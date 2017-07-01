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


def display_word_frequency_distribution(list_y_values, all_data=True,
                                        x_label='Rating (stars)', y_label='Frequency rate (%)'):
    """
    Plot word frequency rate distribution figure

    :param x_label:
    :param y_label:
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
        plt.plot(x, y, label='fitted-' + item['key_word'] if item['fitted'] is True else item['key_word'])
        plt.xlabel(x_label)
        plt.ylabel(y_label)

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

        if max_value == 0:
            continue

        list_scored.append({'key_word': item['key_word'], 'pos_type': item['pos_type'],
                            'list': [v / max_value * score for v in item['list']], 'fitted': True})

    return list_scored


def plus_two_lists(list_a, list_b):
    """
    Plus values in two lists

    :param list_a:
    :param list_b:
    :return:
    """

    list_c = []

    for index, value in enumerate(list_a):
        list_c.append(value + list_b[index])

    return list_c


def compare_result_to_rating(list_result, rating):
    """
    Compare the result list to rating.
    Return whether the predicted polarity is consistent with rating and
    the difference between user's rating and predicted rating and
    the user's rating' position in ordered predicted possibility rating.

    :param list_result:
    :param rating:
    :return:
    """

    if not list_result:
        return

    b_consistent = False
    list_gap = []
    rank = 0

    for index in [i + 1 for i, j in enumerate(list_result) if j == max(list_result)]:
        list_gap.append(abs(rating - index))

        if (rating <= 5 and index <= 5) or (rating > 5 and index > 5):
            b_consistent = True

    for value in list_result:
        if value > list_result[rating - 1]:
            rank += 1

    return b_consistent, np.mean(list_gap), rank


def data_std(list_y_values):
    for item in list_y_values:
        np.std(item['list'])
