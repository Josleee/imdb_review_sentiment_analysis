from network_tools import service

if __name__ == '__main__':
    links = service.fetch_list()
    print len(service.fetch_reviews(links[0]))
