import time

from network_tools import config
from network_tools import service
from utilities import caching


def scrape_films_by_config_settings():
    """
    Scrape films' reviews and save them to local data file.

    """

    dict_reviews = {}

    links = service.fetch_list()
    for key, value in links.iteritems():
        print 'Scraping reviews of movie "' + key + '".'
        dict_reviews[key] = service.fetch_reviews(value)

    caching.dump_to_file(dict_reviews, config.chart_category[config.category_selector])


def get_films_from_file_by_config_settings():
    """
    Get film reviews cache from local file

    :return: dict of film name + reviews
    """

    dict_reviews = caching.read_from_file(config.chart_category[config.category_selector])
    return dict_reviews


if __name__ == '__main__':
    t1 = time.time()
    # scrape_films_by_config_settings()
    t2 = time.time()

    for data in get_films_from_file_by_config_settings().values():
        for review in data:
            print review['title']
    t3 = time.time()

    print 'Scraping time spent: %ds, reading time spent: %ds' % ((t2 - t1), (t3 - t2))
