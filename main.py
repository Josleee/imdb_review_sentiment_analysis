from network_tools import service
from utilities import caching

if __name__ == '__main__':
    links = service.fetch_list()
    data = service.fetch_reviews(links['The Mummy'])
    # data = service.fetch_reviews(links['The Mummy'], 100)

    caching.dump_to_file(data)

    data = caching.read_from_file()
    for d in data:
        print d['title']
