import re
from collections import OrderedDict

import spacy

from network_tools import config
from sentiment_analysis import constant
from utilities import caching, progressbar

nlp = spacy.load('en')


class ReviewParser:
    def __init__(self):
        """
        Review parser module.
        Parse whole review corpus.

        """

        self.dict_statistic = {}

        if caching.read_from_file(config.get_tag_analyzed(), 1):
            self.dict_statistic = caching.read_from_file(config.get_tag_analyzed(), 1)
            return

        dict_reviews = caching.read_from_file(config.chart_category[config.category_selector], 1)

        index = 0
        progressbar.print_progress(index, len(dict_reviews), 'Progress:', 'Complete', 1, 50)
        for key, value in dict_reviews.iteritems():
            for comment in value:
                if comment['rating'] == -1:
                    comment['rating'] = 0

                sentences = filter(None, re.split('[.?!]+', comment['content']))
                # separated_words = filter(None, re.split('[ ,.:()?"/]+', comment['content'].lower()))
                for sentence in sentences:
                    separated_words = nlp(sentence.lower())
                    for word in separated_words:
                        if word.text in constant.exceptional_set:
                            continue

                        if word.pos_ not in self.dict_statistic:
                            self.dict_statistic[word.pos_] = [dict() for i in range(0, 11)]

                        if word.text not in self.dict_statistic[word.pos_][comment['rating']]:
                            self.dict_statistic[word.pos_][comment['rating']][word.text] = 1
                        else:
                            self.dict_statistic[word.pos_][comment['rating']][word.text] += 1

            index += 1
            progressbar.print_progress(index, len(dict_reviews), 'Progress:', 'Complete', 1, 50)
        caching.dump_to_file(self.dict_statistic, config.get_tag_analyzed(), 1)

    def display_top_hit(self, pos_type, top_n=10):
        """
        Print to hit key word by different ratings

        :param pos_type:
        :param top_n
        :return:
        """

        for key, value in self.dict_statistic.iteritems():
            if key != pos_type:
                continue

            print 'Part of speech is %s' % key
            for i in xrange(0, 11):
                ordered = OrderedDict(sorted(value[i].items(), key=lambda t: t[1], reverse=True))
                print 'Word frequency distribution of rating %d:' % i

                index = 0
                for key2, value2 in ordered.iteritems():
                    print '\'%-15s\' occurs %6d times, %.2f%%' % (key2, value2, (value2 * 100 / float(len(ordered))))
                    if index >= top_n:
                        break
                    else:
                        index += 1
                print


if __name__ == '__main__':
    # separated_words = nlp(unicode("Because it's the same story but you don't care who wins or loses.".lower()))
    # if "it's" in separated_words.text[:]:
    #     print True

    rw_parser = ReviewParser()
    rw_parser.display_top_hit('ADJ', 30)

    # parser = DiscourseParser('../data/to_be_analysed/review2.txt')
    # parser.parse()
    # for ds in parser.get_summary():
    #     separated_words = nlp(ds['content'].lower())
    #     for word in separated_words:
    #         print word.pos_, word.text
    # parser.unload()
