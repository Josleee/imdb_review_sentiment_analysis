import matplotlib.pyplot as plt
import numpy as np

from sentiment_analysis import constant


def negation_cues_cal(sentence):
    """
    Calculate the negative polarity of sentence

    :param sentence:
    :return:
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
        plt.plot(x, y, label=item['key_word'])
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

        fit_list_y_values.append({'key_word': 'fit-' + item['key_word'], 'pos_type': item['pos_type'],
                                  'list': fit_y.tolist()})

    return fit_list_y_values
