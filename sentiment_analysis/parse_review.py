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

        self.dict_neg_scores = {}
        self.dict_pos_scores = {}
        self.dict_pos_statistic = {}
        self.dict_neg_statistic = {}

        if caching.read_from_file(config.get_tag_analyzed(), 1):
            list_dict = caching.read_from_file(config.get_tag_analyzed(), 1)
            self.dict_pos_statistic = list_dict[0]
            self.dict_neg_statistic = list_dict[1]
            return

        self.dict_reviews = caching.read_from_file(config.chart_category[config.category_selector], 1)

        index = 0
        progressbar.print_progress(index, len(self.dict_reviews), 'Analysing progress:', 'Complete', 1, 50)
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
                        # if word.lower_ in constant.exceptional_set:
                        #     continue

                        # Add a dictionary in the two POS list
                        if word.pos_ not in self.dict_pos_statistic:
                            self.dict_pos_statistic[word.pos_] = [dict() for i in range(0, 11)]
                        if word.pos_ not in self.dict_neg_statistic:
                            self.dict_neg_statistic[word.pos_] = [dict() for i in range(0, 11)]

                        if negation_polarity:
                            if word.lower_ not in self.dict_pos_statistic[word.pos_][comment['rating']]:
                                self.dict_pos_statistic[word.pos_][comment['rating']][word.lower_] = 1
                            else:
                                self.dict_pos_statistic[word.pos_][comment['rating']][word.lower_] += 1
                        else:
                            if word.lower_ not in self.dict_neg_statistic[word.pos_][comment['rating']]:
                                self.dict_neg_statistic[word.pos_][comment['rating']][word.lower_] = 1
                            else:
                                self.dict_neg_statistic[word.pos_][comment['rating']][word.lower_] += 1

            index += 1
            progressbar.print_progress(index, len(self.dict_reviews), 'Progress:', 'Complete', 1, 50)
        caching.dump_to_file([self.dict_pos_statistic, self.dict_neg_statistic], config.get_tag_analyzed(), 1)

    def display_top_hit(self, pos_type, dict_type, top_n=10):
        """
        Print to hit key word by different ratings

        :param pos_type:
        :param dict_type:
        :param top_n:
        :return:
        """

        if dict_type:
            iter_dict = self.dict_pos_statistic
            dict_name = 'Positive word list'
        else:
            iter_dict = self.dict_neg_statistic
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

    def find_and_display_sample(self, rating, word, limited=5):
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
        if index == 1:
            print 'Not found.'

    def get_word_frequency_rate(self, word, pos_type):
        """
        Get specific word occurrence frequency in certain pos

        :param word:
        :param pos_type:
        :return:
        """

        list_frequency_rate = []

        for key, value in self.dict_pos_statistic.iteritems():
            if key != pos_type:
                continue

            for i in xrange(1, 11):
                if word in value[i]:
                    list_frequency_rate.append(value[i][word] * 100 / float(len(value[i])))
                else:
                    list_frequency_rate.append(0)

        return {'key_word': word, 'pos_type': pos_type, 'list': list_frequency_rate, 'fitted': False}

    def score_all_adj_by_frequency_rates(self):
        """
        Analyse word frequency and generate two adj score lists for sentiment prediction.

        :return:
        """

        if caching.read_from_file(config.get_fr_analyzed(), 1):
            list_dict = caching.read_from_file(config.get_fr_analyzed(), 1)
            self.dict_pos_scores = list_dict[0]
            self.dict_neg_scores = list_dict[1]
            return

        for pos, list_statistic in self.dict_pos_statistic.iteritems():
            if pos != 'ADJ':
                continue

            for i in xrange(1, 11):
                progressbar.print_progress(i - 1, 10, 'Scoring positive progress:', 'Complete', 1, 50)
                for key_word, times in list_statistic[i].iteritems():
                    if key_word in constant.exceptional_set or key_word in self.dict_pos_scores or times < 5:
                        continue

                    # TODO save to dict by adding not replace (consider other pos also has this word's rule)
                    self.dict_pos_scores[key_word] = tools.calculate_relative_scores(
                        tools.fit_curve([self.get_word_frequency_rate(key_word, 'ADJ')]))
            progressbar.print_progress(10, 10, 'Scoring positive progress:', 'Complete', 1, 50)

        for pos, list_statistic in self.dict_neg_statistic.iteritems():
            if pos != 'ADJ':
                continue

            for i in xrange(1, 11):
                progressbar.print_progress(i - 1, 10, 'Scoring negative progress:', 'Complete', 1, 50)
                for key_word, times in list_statistic[i].iteritems():
                    if key_word in constant.exceptional_set or key_word in self.dict_neg_scores or times < 5:
                        continue

                    # TODO save to dict by adding not replace (consider other pos also has this word's rule)
                    self.dict_neg_scores[key_word] = tools.calculate_relative_scores(
                        tools.fit_curve([self.get_word_frequency_rate(key_word, 'ADJ')]))
            progressbar.print_progress(10, 10, 'Scoring negative progress:', 'Complete', 1, 50)

        caching.dump_to_file([self.dict_pos_scores, self.dict_neg_scores], config.get_fr_analyzed(), 1)

    def analyse_given_review(self, text):
        """
        Analyse a given text and return a rating possibility

        :return:
        """

        score = [0 for i in range(0, 10)]
        parsed_text = nlp(text)

        for sentence in parsed_text.sents:
            negation_polarity = tools.negation_cues_cal(sentence)

            for word in sentence:
                if word.lower_ in constant.exceptional_set:
                    continue

                if word.pos_ != 'ADJ':
                    continue

                if negation_polarity:
                    if word.lower_ not in self.dict_pos_scores:
                        continue

                    for rule in self.dict_pos_scores[word.lower_]:
                        if rule['pos_type'] != 'ADJ':
                            continue

                        score = tools.plus_two_lists(rule['list'], score)
                else:
                    if word.lower_ not in self.dict_neg_scores:
                        continue

                    for rule in self.dict_neg_scores[word.lower_]:
                        if rule['pos_type'] != 'ADJ':
                            continue

                        score = tools.plus_two_lists(rule['list'], score)

        print score


if __name__ == '__main__':
    # parsed_data = nlp(unicode('Because it\'s the same story, but you don\'t care who wins or loses. '
    #                           'you just want, the franchise to please end. '
    #                           'Sorry Mr Bay but this is a total and utter failure.'))
    # for span in parsed_data.sents:
    #     print span.text
    #     for word in span:
    #         print word.lower_
    #         print word.pos_
    #     print

    interesting_word_list = ['pure', 'predictable', 'worthy', 'laughable']
    wired_word_list = ['good']
    typical_word_list = ['best', 'terrible', 'willing', 'marvelous']
    unexpected_word_list = ['unexpected', 'intelligent']
    confused_word_list = ['half', 'late']

    r_parser = ReviewParser()
    # r_parser.display_top_hit('ADJ', True, 200)
    # r_parser.display_top_hit('ADJ', False, 200)
    # r_parser.find_sample(10, 'good', 10)

    r_parser.score_all_adj_by_frequency_rates()

    list_words_frequency = []
    word_list = 'appropriate'
    for item in word_list.split(' '):
        list_words_frequency.append(r_parser.get_word_frequency_rate(item, 'ADJ'))

    tools.display_word_frequency_distribution(list_words_frequency, False)
    tools.display_word_frequency_distribution(tools.fit_curve(list_words_frequency))

    text = open('../data/to_be_analysed/review.txt').read()
    r_parser.analyse_given_review(unicode(text))

    # parser = DiscourseParser('../data/to_be_analysed/review2.txt')
    # parser.parse()
    # for ds in parser.get_summary():
    #     separated_words = nlp(ds['content'].lower())
    #     for word in separated_words:
    #         print word.pos_, word.text
    # parser.unload()
