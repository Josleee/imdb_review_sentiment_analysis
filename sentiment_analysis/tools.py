from sentiment_analysis import constant


def negation_cues_cal(sentence):
    """
    Calculate the negative polarity of sentence

    :param sentence:
    :return:
    """

    polarity = 1

    for cue in constant.negation_cues_set:
        for word in sentence:
            if cue == word.text:
                print word.text
                polarity *= -1

    for word in sentence:
        if 'n\'t' in word.text:
            print word.text
            polarity *= -1

    return polarity
