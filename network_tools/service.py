import math

import imdb_crawler
from utilities import progressbar


def fetch_reviews(url, fetch_number=0):
    """
    Fetch reviews of a movie.

    :param url: initial url
    :param fetch_number: reviews fetch number in total
    :return: reviews list
    """

    list_reviews = []

    if 'reviews' not in url:
        url = imdb_crawler.get_next_review_link(url)

    if fetch_number == 0:
        # TODO: fix bug, if url is not the first page of review, we should first calculate the current page number
        total_page_number = imdb_crawler.get_review_page_size(url)
    else:
        total_page_number = int(math.ceil(fetch_number / 10.0))

    while True:
        list_partial_reviews = imdb_crawler.parse_review(url)
        if not list_partial_reviews:
            break
        if fetch_number != 0:
            if fetch_number <= len(list_reviews):
                break

        list_reviews.extend(list_partial_reviews)
        progressbar.print_progress(int(math.ceil(len(list_reviews) / 10.0)), total_page_number,
                                   'Progress:', 'Complete', 1, 50)
        url = imdb_crawler.get_next_review_link(url)

    return list_reviews


def fetch_list():
    """
    Fetch list of hot movies.

    :return: movie links list
    """

    return imdb_crawler.grab_list()
