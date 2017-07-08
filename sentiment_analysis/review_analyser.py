import random
import re
from collections import OrderedDict
from copy import deepcopy

import spacy

from network_tools import config
from sentiment_analysis import constant, tools
from sentiment_analysis.discourse_parser import DiscourseParser
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

        if caching.read_from_file(config.get_tag_analysed(), 1):
            list_dict = caching.read_from_file(config.get_tag_analysed(), 1)
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
            progressbar.print_progress(index, len(self.dict_reviews), 'Analysing progress:', 'Complete', 1, 50)
        caching.dump_to_file([self.dict_pos_statistic, self.dict_neg_statistic], config.get_tag_analysed(), 1)

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

                total_times = 0
                for times in ordered.values():
                    total_times += times

                index = 1
                for key2, value2 in ordered.iteritems():
                    if key2 in constant.exceptional_set:
                        continue

                    print '%-15s occurs %6d times  %.2f%%' % (key2, value2, (value2 * 100 / float(total_times)))
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

    def get_word_scores(self, word, negation=False):
        """
        Get specific word scores

        :param negation:
        :param word:
        :return:
        """

        if negation:
            dict_score = self.dict_neg_scores
        else:
            dict_score = self.dict_pos_scores

        return dict_score[word]

    def get_word_frequency_rate(self, word, pos_type, negation=False):
        """
        Get specific word occurrence frequency in certain pos

        :param negation:
        :param word:
        :param pos_type:
        :return:
        """

        if negation:
            dict_statistic = self.dict_neg_statistic
        else:
            dict_statistic = self.dict_pos_statistic

        list_frequency_rate = []

        for key, value in dict_statistic.iteritems():
            if key != pos_type:
                continue

            for i in xrange(1, 11):
                total_times = 0
                for times in value[i].values():
                    total_times += times

                if word in value[i]:
                    list_frequency_rate.append(value[i][word] * 100 / float(total_times))
                else:
                    list_frequency_rate.append(0)

        return {'key_word': word, 'pos_type': pos_type, 'list': list_frequency_rate, 'fitted': False}

    def score_all_adj_by_frequency_rates(self, combined=None):
        """
        Analyse word frequency and generate two adj score lists for sentiment prediction.

        :param combined:
        :return:
        """

        if combined:
            if caching.read_from_file(config.get_special_trained(), 1):
                list_dict = caching.read_from_file(config.get_special_trained(), 1)
                self.dict_pos_scores = list_dict[0]
                self.dict_neg_scores = list_dict[1]
                return

        elif caching.read_from_file(config.get_fr_trained(), 1):
            list_dict = caching.read_from_file(config.get_fr_trained(), 1)
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
                        tools.fit_curve([self.get_word_frequency_rate(key_word, 'ADJ', True)]))
            progressbar.print_progress(10, 10, 'Scoring negative progress:', 'Complete', 1, 50)

        if combined:
            caching.dump_to_file([self.dict_pos_scores, self.dict_neg_scores], config.get_special_trained(), 1)
        else:
            caching.dump_to_file([self.dict_pos_scores, self.dict_neg_scores], config.get_fr_trained(), 1)

    def analyse_given_review(self, text):
        """
        Analyse a given text and return a rating possibility

        :return: predicted score list
        """

        score = [0 for i in range(0, 10)]
        text = text.encode('utf8').decode('utf8', 'ignore')
        parsed_text = nlp(text)

        for sentence in parsed_text.sents:
            # print sentence.text
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
                        print 'p_word: %s, predicted rating: %d' % (
                            word.lower_, rule['list'].index(max(rule['list'])) + 1)
                else:
                    if word.lower_ not in self.dict_neg_scores:
                        continue

                    for rule in self.dict_neg_scores[word.lower_]:
                        if rule['pos_type'] != 'ADJ':
                            continue

                        score = tools.plus_two_lists(rule['list'], score)
                        print 'n_word: %s, predicted rating: %d' % (
                            word.lower_, rule['list'].index(max(rule['list'])) + 1)

        return score

    def randomly_sentiment_analysis_testing(self, amount=5, test_name=None, discourse_parser=False,
                                            weighting_scheme=2):
        """
        Randomly pick up movie reviews from corpus, analyse them and compare results to users' ratings

        :param weighting_scheme: the value of nuclei / satellites, bigger than 1
        :param discourse_parser:
        :param amount:
        :param test_name:
        :return:
        """

        polarity_true_count = 0
        rating_difference_smaller_or_equal_than_three_count = 0
        rating_difference_smaller_or_equal_than_two_count = 0
        rating_difference_smaller_or_equal_than_one_count = 0
        rating_exactly_same = 0
        list_test_data = []

        if test_name and caching.read_from_file(test_name, 1):
            list_test_source = caching.read_from_file(test_name, 1)

            s_index = 0
            for comment in list_test_source:
                if discourse_parser:
                    try:
                        d_parser = DiscourseParser()
                        d_parser.parse(content=comment['content'])
                        text = '.'.join([ds['content'].lower() for ds in d_parser.get_summary()[s_index:]])
                        s_index = len(d_parser.get_summary())
                        text = re.sub(' *[,.?!] *\. *| *\. *', ' . ', text)
                    except Exception, e:
                        print e.message
                        continue
                    finally:
                        d_parser.unload()
                else:
                    text = comment['content']

                if discourse_parser and weighting_scheme:
                    result_text = self.analyse_given_review(comment['content'])
                    result_core = self.analyse_given_review(text)
                    comment['result'] = tools.plus_two_lists(result_core, result_text, weighting_scheme - 1)
                    # print result_core
                    # print result_text
                    # print comment['result']
                else:
                    comment['result'] = self.analyse_given_review(text)

                print 'Rating: %d, predicted rating: %d' % (comment['rating'],
                                                            comment['result'].index(max(comment['result'])) + 1)
                print

                polarity_true, rating_difference, difference_to_top_predicted = tools.compare_result_to_rating(
                    comment['result'], comment['rating'])

                if polarity_true:
                    polarity_true_count += 1

                if rating_difference <= 3:
                    rating_difference_smaller_or_equal_than_three_count += 1

                if rating_difference <= 2:
                    rating_difference_smaller_or_equal_than_two_count += 1

                if rating_difference <= 1:
                    rating_difference_smaller_or_equal_than_one_count += 1

                if rating_difference <= 0:
                    rating_exactly_same += 1

                list_test_data.append(comment)

        else:
            for ca in config.chart_category[2:]:
                dict_ca = caching.read_from_file(ca, 1)

                s_index = 0
                for i in range(0, amount / len(config.chart_category[2:])):
                    movie_name = random.choice(dict_ca.keys())
                    comments = dict_ca[movie_name]

                    if not comments:
                        continue

                    comment = random.choice(comments)

                    if comment['rating'] == -1:
                        continue

                    copy_comment = deepcopy(comment)

                    if discourse_parser:
                        try:
                            d_parser = DiscourseParser()
                            d_parser.parse(content=comment['content'])
                            text = '.'.join([ds['content'].lower() for ds in d_parser.get_summary()[s_index:]])
                            s_index = len(d_parser.get_summary())
                            text = re.sub(' *[,.?!] *\. *| *\. *', ' . ', text)
                        except Exception, e:
                            print e.message
                            continue
                        finally:
                            d_parser.unload()
                    else:
                        text = comment['content']

                    if discourse_parser and weighting_scheme:
                        result_text = self.analyse_given_review(comment['content'])
                        result_core = self.analyse_given_review(text)
                        copy_comment['result'] = tools.plus_two_lists(result_core, result_text, weighting_scheme - 1)
                        # print result_core
                        # print result_text
                        # print comment['result']
                    else:
                        copy_comment['result'] = self.analyse_given_review(text)

                    print 'Rating: %d, predicted rating: %d' % (copy_comment['rating'],
                                                                copy_comment['result'].index(
                                                                    max(copy_comment['result'])) + 1)
                    print

                    polarity_true, rating_difference, difference_to_top_predicted = tools.compare_result_to_rating(
                        copy_comment['result'], copy_comment['rating'])

                    if polarity_true:
                        polarity_true_count += 1

                    if rating_difference <= 3:
                        rating_difference_smaller_or_equal_than_three_count += 1

                    if rating_difference <= 2:
                        rating_difference_smaller_or_equal_than_two_count += 1

                    if rating_difference <= 1:
                        rating_difference_smaller_or_equal_than_one_count += 1

                    if rating_difference <= 0:
                        rating_exactly_same += 1

                    list_test_data.append(copy_comment)

        print 'Polarity accuracy: %d%%, rating difference <= 3 accuracy: %d%%, rating difference <= 2 accuracy: %d%%' \
              % (
                  100 * polarity_true_count / float(len(list_test_data)),
                  100 * rating_difference_smaller_or_equal_than_three_count / float(len(list_test_data)),
                  100 * rating_difference_smaller_or_equal_than_two_count / float(len(list_test_data)))
        print 'Rating difference <= 1 accuracy: %d%%, rating difference = 0 accuracy: %d%%' \
              % (
                  100 * rating_difference_smaller_or_equal_than_one_count / float(len(list_test_data)),
                  100 * rating_exactly_same / float(len(list_test_data)))
        print 'Number of samples: %d' % len(list_test_data)

        if test_name:
            caching.dump_to_file(list_test_data, test_name, 1)

        return list_test_data

    def train_by_using_the_same_amount_of_rating_reviews(self):
        """
        Train the corpus by using movie reviews in same amount in different rating categories

        """

        self.dict_pos_statistic = {}
        self.dict_neg_statistic = {}

        if caching.read_from_file(config.get_special_analysed(), 1):
            list_dict = caching.read_from_file(config.get_special_analysed(), 1)
            self.dict_pos_statistic = list_dict[0]
            self.dict_neg_statistic = list_dict[1]
            return

        list_sum = [0 for i in range(0, 10)]
        dict_distribution = {}

        for category_name in config.get_useful_charts():
            dict_reviews = caching.read_from_file(category_name, 1)
            dict_distribution = dict(dict_distribution.items() + dict_reviews.items())

            # list_distribution = self.review_corpus_distribution_analysis(category=category_name, show_result=False)
            # list_sum = tools.plus_two_lists(list_sum, list_distribution)
            # dict_distribution[category_name] = list_distribution

        print len(dict_distribution)

        list_movie_info = [dict() for i in range(0, 10)]
        for movie_name, value in dict_distribution.iteritems():
            list_ratings = [0 for i in range(0, 10)]

            for comment in value:
                if comment['rating'] == -1:
                    continue

                list_ratings[comment['rating'] - 1] += 1

            if sum(list_ratings) == 0:
                continue

            list_weighted_ratings = [list_ratings[i] * (i + 1) for i in range(0, 10)]
            list_sum[sum(list_weighted_ratings) / sum(list_ratings) - 1] += sum(list_ratings)
            # print 'movie: %s, review count: %d, average rating: %.2f' % \
            #       (movie_name, sum(list_ratings), sum(list_weighted_ratings) / float(sum(list_ratings)))
            list_movie_info[sum(list_weighted_ratings) / sum(list_ratings) - 1][movie_name] = sum(list_ratings)

        # list_format = [
        #     {'list': list_sum, 'key_word': '', 'fitted': False, 'pos_type': ''}]
        # print 'Reviews count from rating 1-10: %s' % ', '.join(str(v) for v in list_sum)
        # tools.display_word_frequency_distribution(list_format, y_label='Review pieces')

        # Separate the data set to three parts, whose rating is from 1-4, 4-7 and 7-10 respectively
        # print '%s %s %s' % ((list_sum[0:3]), (list_sum[3:6]), (list_sum[6:9]))
        each_part_reviews_amount = min(sum(list_sum[0:3]), sum(list_sum[3:6]), sum(list_sum[6:9]))

        list_review_distributed = []
        for i in range(0, 3):
            list_review_distributed.extend(tools.equally_distribute(list_sum[i * 3:i * 3 + 3],
                                                                    unassigned_value=each_part_reviews_amount))
        print list_review_distributed

        for r, a in enumerate(list_review_distributed):
            list_review_amount = tools.equally_distribute(list_movie_info[r].values(), unassigned_value=a)
            # print list_review_amount

            progressbar_index = 0
            progressbar.print_progress(progressbar_index, len(list_movie_info[r]),
                                       'Analysing progress:', 'Rating ' + str(r + 1), 1, 50)

            for index, movie_name in enumerate(list_movie_info[r].keys()):
                # print list_review_amount[index]

                comment_index = 0
                for comment in dict_distribution[movie_name]:
                    parsed_data = nlp(comment['content'])

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

                    comment_index += 1
                    if list_review_amount[index] <= comment_index:
                        break

                progressbar_index += 1
                progressbar.print_progress(progressbar_index, len(list_movie_info[r]),
                                           'Analysing progress:', 'Rating ' + str(r + 1), 1, 50)

        caching.dump_to_file([self.dict_pos_statistic, self.dict_neg_statistic], config.get_special_analysed(), 1)

    @staticmethod
    def review_corpus_distribution_analysis(category_selector=-1, category=None, show_result=True):
        """
        Analyse different rating reviews distribution in the corpus and
        adj words count in different rating categories.

        :param category_selector:
        :param category:
        :param show_result:
        :return:
        """

        if category_selector != -1:
            dict_reviews = caching.read_from_file(config.chart_category[category_selector], 1)
        elif category:
            dict_reviews = caching.read_from_file(category, 1)
        else:
            dict_reviews = caching.read_from_file(config.chart_category[config.category_selector], 1)

        list_count_different_category_number = [0 for i in range(0, 10)]

        for key, value in dict_reviews.iteritems():
            for comment in value:
                if comment['rating'] == -1:
                    continue
                list_count_different_category_number[comment['rating'] - 1] += 1

        if show_result:
            # list_format = [
            #     {'list': list_count_different_category_number, 'key_word': '', 'fitted': False, 'pos_type': ''}]
            print 'Reviews count from rating 1-10: %s, total: %s' % \
                  (', '.join(str(v) for v in list_count_different_category_number),
                   sum(list_count_different_category_number))
            # tools.display_word_frequency_distribution(list_format, y_label='Occurrence times')

        return list_count_different_category_number


if __name__ == '__main__':
    interesting_word_list = ['pure', 'predictable', 'worthy', 'laughable', 'unnecessary']
    wired_word_list = ['good']
    typical_word_list = ['best', 'terrible', 'willing', 'marvelous']
    unexpected_word_list = ['unexpected', 'intelligent']
    confused_word_list = ['half', 'late']

    r_parser = ReviewParser()

    # r_parser.review_corpus_distribution_analysis(category_selector=1)
    # r_parser.score_all_adj_by_frequency_rates()
    r_parser.train_by_using_the_same_amount_of_rating_reviews()
    r_parser.score_all_adj_by_frequency_rates(combined=True)

    # r_parser.display_top_hit('ADJ', True, 500)
    # r_parser.display_top_hit('ADJ', False, 200)
    # r_parser.find_sample(10, 'good', 10)

    # r_parser.randomly_sentiment_analysis_testing(amount=1000, test_name='1000_times_random_test2')
    # r_parser.randomly_sentiment_analysis_testing(amount=120, test_name='100_times_random', discourse_parser=False)
    r_parser.randomly_sentiment_analysis_testing(amount=600, test_name='600_times_random_test',
                                                 discourse_parser=True, weighting_scheme=3)

    # # romantic different decent violent
    # list_words_frequency = []
    # word_list = 'decent'
    # for item in word_list.split(' '):
    #     list_words_frequency.append(r_parser.get_word_frequency_rate(item, 'ADJ'))
    #     # p1 = r_parser.get_word_scores(item)
    #     # n1 = r_parser.get_word_scores(item, True)
    #     p1 = r_parser.get_word_frequency_rate(item, 'ADJ')
    #     n1 = r_parser.get_word_frequency_rate(item, 'ADJ', True)
    #
    #     # pi = [p1, n1]
    #     # for p in pi:
    #     #     print '%s &' % item,
    #     #     index = 0
    #     #     p = p[0]
    #     #     for v in p['list']:
    #     #         index += 1
    #     #
    #     #         print '%.2f' % (float(v) * 1),
    #     #         if index % 10 != 0:
    #     #             print '&',
    #     #         else:
    #     #             print '\\\\'
    #
    # tools.display_word_frequency_distribution(list_words_frequency, False)
    # tools.display_word_frequency_distribution(tools.fit_curve(list_words_frequency))

    # # review.txt review4_7s.txt review5_1s.txt review6_3s.txt review7_1s.txt
    # file_name = 'r4s2'
    # rating = 2
    # text = codecs.open('../data/to_be_analysed/' + file_name, encoding='utf-8', mode='r').read()
    # list_result = r_parser.analyse_given_review(text)
    # print list_result
    # index = 0
    # for v in list_result:
    #     index += 1
    #     print '%.2f' % (float(v) * 1),
    #     if index % 10 != 0:
    #         print '&',
    #     else:
    #         print '\\\\'
    # print tools.compare_result_to_rating(list_result, rating)
    # list_format = [{'list': list_result, 'key_word': 'R', 'fitted': False, 'pos_type': ''}]
    #
    # tools.display_word_frequency_distribution(list_format, True)
    # # tools.display_word_frequency_distribution(tools.fit_curve(list_format), True)
