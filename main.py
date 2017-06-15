from network_tools import imdb_crawler

if __name__ == '__main__':
    links = imdb_crawler.grab_list()
    movies = [imdb_crawler.get_next_review_link(l) for l in links.values()]
    print imdb_crawler.parse_review(movies[0], 1)
    print imdb_crawler.parse_review('http://www.imdb.com/title/tt2316204/reviews?start=10000', 1)


    # movies = [parse_movie(l) for l in links]
    # # Write in a file
    # with open('top_movies.txt', 'a+') as f:
    #     f.write(json.dumps(movies))
    #
    # print('Movie Data Stored successfully')
