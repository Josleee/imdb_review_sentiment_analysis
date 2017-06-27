import re
from collections import OrderedDict

import spacy

from network_tools import config
from sentiment_analysis import constant, tools
from utilities import caching, progressbar

nlp = spacy.load('en')


class ReviewParser:
    def __init__(self):
        """
        Review parser module.
        Parse whole review corpus.

        """

        self.pos_dict_statistic = {}
        self.neg_dict_statistic = {}

        if caching.read_from_file(config.get_tag_analyzed(), 1):
            list_dict = caching.read_from_file(config.get_tag_analyzed(), 1)
            self.pos_dict_statistic = list_dict[0]
            self.neg_dict_statistic = list_dict[1]
            return

        self.dict_reviews = caching.read_from_file(config.chart_category[config.category_selector], 1)

        index = 0
        progressbar.print_progress(index, len(self.dict_reviews), 'Progress:', 'Complete', 1, 50)
        for key, value in self.dict_reviews.iteritems():
            for comment in value:
                if comment['rating'] == -1:
                    comment['rating'] = 0

                # sentences = []
                parsed_data = nlp(comment['content'])
                # for span in parsed_data.sents:
                # go from the start to the end of each span, returning each token in the sentence
                # combine each token using join()
                # sent = ''.join(parsed_data[i].string for i in range(span.start, span.end)).strip()
                # sentences.append(sent)

                # sentences = filter(None, re.split('[.?!]+', comment['content']))
                # separated_words = filter(None, re.split('[ ,.:()?"/]+', comment['content'].lower()))
                for sentence in parsed_data.sents:
                    negation_polarity = tools.negation_cues_cal(sentence)
                    for word in sentence:
                        if word.lower_ in constant.exceptional_set:
                            continue

                        # Add a dictionary in the two POS list
                        if word.pos_ not in self.pos_dict_statistic:
                            self.pos_dict_statistic[word.pos_] = [dict() for i in range(0, 11)]
                        if word.pos_ not in self.neg_dict_statistic:
                            self.neg_dict_statistic[word.pos_] = [dict() for i in range(0, 11)]

                        if negation_polarity:
                            if word.lower_ not in self.pos_dict_statistic[word.pos_][comment['rating']]:
                                self.pos_dict_statistic[word.pos_][comment['rating']][word.lower_] = 1
                            else:
                                self.pos_dict_statistic[word.pos_][comment['rating']][word.lower_] += 1
                        else:
                            if word.lower_ not in self.neg_dict_statistic[word.pos_][comment['rating']]:
                                self.neg_dict_statistic[word.pos_][comment['rating']][word.lower_] = 1
                            else:
                                self.neg_dict_statistic[word.pos_][comment['rating']][word.lower_] += 1

            index += 1
            progressbar.print_progress(index, len(self.dict_reviews), 'Progress:', 'Complete', 1, 50)
        caching.dump_to_file([self.pos_dict_statistic, self.neg_dict_statistic], config.get_tag_analyzed(), 1)

    def display_top_hit(self, pos_type, dict_type, top_n=10):
        """
        Print to hit key word by different ratings

        :param pos_type:
        :param dict_type:
        :param top_n:
        :return:
        """

        if dict_type:
            iter_dict = self.pos_dict_statistic
            dict_name = 'Positive word list'
        else:
            iter_dict = self.neg_dict_statistic
            dict_name = 'Negative word list'

        for key, value in iter_dict.iteritems():
            if key != pos_type:
                continue

            print '%s, part of speech is %s' % (dict_name, key)
            for i in xrange(1, 11):
                ordered = OrderedDict(sorted(value[i].items(), key=lambda t: t[1], reverse=True))
                print 'Word frequency distribution of rating %d:' % i

                index = 1
                for key2, value2 in ordered.iteritems():
                    if key2 in constant.exceptional_set:
                        continue

                    print '%-15s occurs %6d times  %.2f%%' % (key2, value2, (value2 * 100 / float(len(ordered))))
                    if index >= top_n:
                        break
                    else:
                        index += 1
                print

    def find_sample(self, rating, word, limited=5):
        """
        Find samples in the corpus by some conditions.

        :param rating:
        :param word:
        :param limited:
        :return:
        """

        if not hasattr(self, 'dict_reviews'):
            self.dict_reviews = caching.read_from_file(config.chart_category[config.category_selector], 1)

        index = 1
        print 'Results of searching word \'%s\' in %d star reviews:' % (word, rating)
        for key, value in self.dict_reviews.iteritems():
            for comment in value:
                if rating == comment['rating'] or (rating == 0 and comment['rating'] == -1):
                    for match in re.finditer("(^|\s)+[A-Za-z,;'\"\s]+" + word + "+[A-Za-z,;'\"\s]+([.?!]|$)",
                                             comment['content'], re.DOTALL):
                        print 'Sample: %s' % match.group(0).strip()
                        if index >= limited:
                            return
                        else:
                            index += 1


if __name__ == '__main__':
    # parsed_data = nlp(unicode(
    #     'Because it\'s the same story but you don\'t care who wins or loses. you just want the franchise to please end. Sorry Mr Bay but this is a total and utter failure.'))
    # for span in parsed_data.sents:
    #     print tools.negation_cues_cal(span)
    #     for word in span:
    #         print type(word.lower_)
    #         print word.lower_
    #     print

    r_parser = ReviewParser()
    r_parser.display_top_hit('ADJ', True, 30)
    r_parser.display_top_hit('ADJ', False, 30)
    r_parser.find_sample(1, 'good')

    # parser = DiscourseParser('../data/to_be_analysed/review2.txt')
    # parser.parse()
    # for ds in parser.get_summary():
    #     separated_words = nlp(ds['content'].lower())
    #     for word in separated_words:
    #         print word.pos_, word.text
    # parser.unload()
