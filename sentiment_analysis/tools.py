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
