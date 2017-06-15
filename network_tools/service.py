import imdb_crawler
from IDMB


def fetch_reviews(url, fetch_number=0):
    """
    Fetch reviews of a movie.

    :param url: initial url
    :param fetch_number: reviews fetch number in total
    :return: reviews list
    """

    list_reviews = []

    while True:
        if 'reviews' not in url:
            url = imdb_crawler.get_next_review_link(url)

        list_partial_reviews = imdb_crawler.parse_review(url)
        if not list_partial_reviews:
            break
        if fetch_number != 0:
            if fetch_number <= len(list_reviews):
                break

        list_reviews.extend(list_partial_reviews)

    return list_reviews


def fetch_list():
    """
    Fetch list of hot movies.

    :return: movie links list
    """

    return imdb_crawler.grab_list()



