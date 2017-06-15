import math

from network_tools import service

if __name__ == '__main__':
    links = service.fetch_list()
    service.fetch_reviews(links['The Mummy'])
    # service.fetch_reviews(links['The Mummy'], 100)
