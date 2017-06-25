from collections import OrderedDict

import nltk
import spacy
from nltk.corpus import wordnet
from nltk.stem.porter import PorterStemmer

from network_tools import config
from sentiment_analysis.parse_discourse import DiscourseParser
from utilities import caching, progressbar

nlp = spacy.load('en')


def parse_review():
    """
    Parse whole review corpus

    :return:
    """

    dict_statistic = {}
    dict_reviews = caching.read_from_file(config.chart_category[config.category_selector], 1)

    index = 0
    progressbar.print_progress(index, len(dict_reviews), 'Progress:', 'Complete', 1, 50)
    for key, value in dict_reviews.iteritems():
        for comment in value:
            if comment['rating'] == -1:
                comment['rating'] = 0

            # separated_words = filter(None, re.split('[ ,.:()?"/]+', comment['content'].lower()))
            separated_words = nlp(comment['content'].lower())
            for word in separated_words:
                if word.pos_ not in dict_statistic:
                    dict_statistic[word.pos_] = [dict() for i in range(0, 11)]

                if word.text not in dict_statistic[word.pos_][comment['rating']]:
                    dict_statistic[word.pos_][comment['rating']][word.text] = 1
                else:
                    dict_statistic[word.pos_][comment['rating']][word.text] += 1

        index += 1
        progressbar.print_progress(index, len(dict_reviews), 'Progress:', 'Complete', 1, 50)

    return dict_statistic


def display_top_hit(result):
    """
    Print to hit key word by different ratings

    :param result:
    :return:
    """

    for key, value in result.iteritems():
        print 'Type of speech is %s' % key
        for i in xrange(0, 11):
            ordered = OrderedDict(sorted(value[i].items(), key=lambda t: t[1], reverse=True))
            print 'Word frequency distribution of rating %d:' % i

            index = 0
            for key2, value2 in ordered.iteritems():
                print '\'%-10s\' occurs %6d times' % (key2, value2)
                if index >= 30:
                    break
                else:
                    index += 1
            print


if __name__ == '__main__':
    # if not caching.read_from_file(config.get_tag_analyzed(), 1):
    #     data = parse_review()
    #     caching.dump_to_file(data, config.get_tag_analyzed(), 1)
    #     display_top_hit(data)
    # else:
    #     data = caching.read_from_file(config.get_tag_analyzed(), 1)
    #     display_top_hit(data)

    parser = DiscourseParser('../data/to_be_analysed/review.txt')
    parser.parse()
    for ds in parser.get_summary():
        separated_words = nlp(str(ds['content']).lower())
        for word in separated_words:
            print word
    parser.unload()

    # print wordnet.synsets('cat')
    # ps = PorterStemmer()
    # print ps.stem('provide')

    # doc = nlp(u'They told us to duck.')
    # for word in doc:
    #     print(word.text, word.lemma, word.lemma_, word.tag, word.tag_, word.pos, word.pos_)
