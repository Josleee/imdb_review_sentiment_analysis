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


def display_word_frequency_distribution(dict_y_values):
    """
    Plot word frequency distribution figure

    :param dict_y_values:
    :return:
    """

    for key, values in dict_y_values.iteritems():
        x = np.array(range(1, 11), np.int32)
        y = np.array(values, np.float)
        plt.plot(x, y, label=key)
        plt.xlabel('Rating')
        plt.ylabel('Frequency rate')

    plt.legend()
    plt.show()
