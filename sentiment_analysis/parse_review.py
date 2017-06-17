import re
from collections import OrderedDict

import nltk
import spacy
from nltk.corpus import wordnet
from nltk.stem.porter import PorterStemmer

from network_tools import config
from utilities import caching

nlp = spacy.load('en')


def parse_review():
    """
    Parse whole review corpus

    :return:
    """

    list_statistic = [dict() for i in range(0, 11)]
    dict_reviews = caching.read_from_file(config.chart_category[config.category_selector], 1)

    for key, value in dict_reviews.iteritems():
        for comment in value:
            if comment['rating'] == -1:
                comment['rating'] = 0

            separated_words = filter(None, re.split('[ ,.:()?"/]+', comment['content'].lower()))
            for word in separated_words:
                if word not in list_statistic[comment['rating']]:
                    list_statistic[comment['rating']][word] = 1
                else:
                    list_statistic[comment['rating']][word] += 1

    return list_statistic


def display_top_hit(result):
    """
    Print to hit key word by different ratings

    :param result:
    :return:
    """

    for i in xrange(0, 11):
        ordered = OrderedDict(sorted(result[i].items(), key=lambda t: t[1], reverse=True))
        print 'Word frequency distribution of rating %d:' % i

        index = 0
        for key, value in ordered.iteritems():
            print '\'%-10s\' occurs %6d times' % (key, value)
            if index >= 10:
                break
            else:
                index += 1
        print


if __name__ == '__main__':
    display_top_hit(parse_review())
    print wordnet.synsets('cat')
    nltk.download()
    ps = PorterStemmer()
    print ps.stem('provide')

    doc = nlp(u'They told us to duck.')
    for word in doc:
        print(word.text, word.lemma, word.lemma_, word.tag, word.tag_, word.pos, word.pos_)
