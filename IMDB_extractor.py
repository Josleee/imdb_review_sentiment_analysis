import json
from time import sleep

import requests
from bs4 import BeautifulSoup

headers = {
    'headers': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'}


# This will grab the links of movie from movies chart
def grab_list():
    links = []
    try:
        base_url = 'http://www.imdb.com'
        # url = base_url + '/chart/top'
        url = base_url + '/chart/boxoffice'
        r = requests.get(url, headers=headers)
        html = None
        if r.status_code != 200:
            return None
        html = r.text
        soup = BeautifulSoup(html, 'lxml')
        titles = soup.select('.titleColumn a')
        for title in titles:
            links.append(base_url + title['href'])
    except Exception as ex:
        print(str(ex))
    finally:
        return links


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
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            return None

        html = r.text
        soup = BeautifulSoup(html, 'lxml')
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
        print(str(ex))
    finally:
        return record


if __name__ == '__main__':
    links = grab_list()
    print links

    movies = [parse_movie(l) for l in links]
    # Write in a file
    with open('top_movies.txt', 'a+') as f:
        f.write(json.dumps(movies))

    print('Movie Data Stored successfully')
