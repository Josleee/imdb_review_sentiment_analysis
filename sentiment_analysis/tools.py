from sentiment_analysis import constant


def negation_cues_cal(sentence):
    """
    Calculate the negative polarity of sentence

    :param sentence:
    :return:
    """

    polarity = 1

    for word in constant.negation_cues_set:
        if word in sentence:
            polarity *= -1

    return polarity
