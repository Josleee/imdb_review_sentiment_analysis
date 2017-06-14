import json
from time import sleep

import requests
from bs4 import BeautifulSoup

headers = {
    'headers': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}


# Parse the page for a certain url
def get_page(url, sleep_time=0, try_times=3):
    for i in xrange(0, try_times):
        try:
            url = url.rstrip('\n')
            r = requests.get(url, headers=headers)
            if r.status_code != 200:
                sleep(sleep_time)
                continue
            html = r.text
            soup = BeautifulSoup(html, 'lxml')
            return soup
        except Exception as ex:
            print str(ex)
            sleep(sleep_time)
            continue


# This will grab the links of movie from movies chart
def grab_list():
    dict_links = {}
    base_url = 'http://www.imdb.com'
    # boxoffice can be change to 'top'
    url = base_url + '/chart/' + 'boxoffice'

    try:
        soup = get_page(url)
        titles = soup.select('.titleColumn a')
        for title in titles:
            print title.text
            dict_links[title.get_text()] = base_url + title['href']

    except Exception as ex:
        print str(ex)
    finally:
        return dict_links


# Get next review page link from exist link
def get_next_review_link(link):
    try:
        if 'reviews' in link:
            return link.split('start=')[0] + 'start=' + str(int(link.split('start=')[1]) + 10)
        else:
            return link.split('?')[0] + '/reviews?start=0'
    except Exception as ex:
        print str(ex)


# Parse info of an individual movie page
def parse_movie(url):
    title = '-'
    summary = '-'
    cast = []
    record = {}

    try:
        sleep(3)
        url = url.rstrip('\n')
        print('Processing..' + url)
        soup = get_page(url)
        title_section = soup.select('.title_wrapper > h1')
        summary_section = soup.select('.plot_summary .summary_text')
        cast_list = soup.select('.cast_list')

        if summary_section:
            summary = summary_section[0].text.strip()

        if title_section:
            title = title_section[0].text.strip()
        if cast_list:
            actors = cast_list[0].findAll('span', {'itemprop': 'name'})
            for actor in actors:
                cast.append(actor.text.strip())

            record = {'title': title, 'summary': summary, 'cast': cast}
    except Exception as ex:
        print str(ex)
    finally:
        return record


# Parse reviews from the a certain review page
def parse_review(url):
    try:
        sleep(3)

        soup = get_page(url)

        title_section = soup.select('.title_wrapper > h1')
        summary_section = soup.select('.plot_summary .summary_text')
        cast_list = soup.select('.cast_list')

        if summary_section:
            summary = summary_section[0].text.strip()

        if title_section:
            title = title_section[0].text.strip()
        if cast_list:
            actors = cast_list[0].findAll('span', {'itemprop': 'name'})
            for actor in actors:
                cast.append(actor.text.strip())

            record = {'title': title, 'summary': summary, 'cast': cast}

    except Exception as ex:
        print str(ex)
    finally:
        return record


if __name__ == '__main__':
    links = grab_list()
    movies = [get_next_review_link(l) for l in links.values()]
    print movies

    # movies = [parse_movie(l) for l in links]
    # # Write in a file
    # with open('top_movies.txt', 'a+') as f:
    #     f.write(json.dumps(movies))
    #
    # print('Movie Data Stored successfully')
