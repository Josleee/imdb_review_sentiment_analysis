from network_tools import service
from utilities import caching


def cache_top_10_hot_films():
    """
    Fetch top 10 films' reviews and same them to local data file.

    """

    dict_reviews = {}

    links = service.fetch_list()
    for key, value in links.iteritems():
        print 'Scraping reviews of movie "' + key + '".'
        dict_reviews[key] = service.fetch_reviews(value)

    caching.dump_to_file(dict_reviews, 'top10')


def get_top_10_hot_films_from_file():
    """
    Get top 10 hot films from local file

    :return: film name + reviews dict
    """

    dict_reviews = caching.read_from_file('top10')
    return dict_reviews


if __name__ == '__main__':
    # cache_top_10_hot_films()
    for data in get_top_10_hot_films_from_file().values():
        for review in data:
            print review['title']
