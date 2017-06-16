import re
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup

import config


def get_page(url):
    """
    Parse the page for a certain url.

    :param url:
    :return:
    """

    for i in xrange(0, config.try_times):
        try:
            url = url.rstrip('\n')
            r = requests.get(url, headers=config.headers)
            if r.status_code != 200:
                sleep(config.fail_wait_time)
                continue
            html = r.text
            soup = BeautifulSoup(html, 'lxml')
            return soup

        except Exception:
            traceback.print_exc()
            sleep(config.fail_wait_time)
            continue


def grab_list():
    """
    This will grab the links of movie from movies chart.

    :return:
    """

    dict_links = {}
    base_url = 'http://www.imdb.com'
    url = base_url + '/chart/' + config.chart_category[config.category_selector]

    for i in xrange(0, config.try_times):
        try:
            soup = get_page(url)
            titles = soup.select('.titleColumn a')
            for title in titles:
                dict_links[title.text] = base_url + title['href']

            return dict_links

        except Exception:
            traceback.print_exc()
            sleep(config.fail_wait_time)
            continue


def get_next_review_link(link):
    """
    Get next review page link from exist link

    :param link:
    :return:
    """

    try:
        if 'reviews' in link:
            return link.split('start=')[0] + 'start=' + str(int(link.split('start=')[1]) + 10)
        else:
            return link.split('?')[0].strip('/') + '/reviews?start=0'
    except Exception:
        traceback.print_exc()


def parse_movie(url):
    """
    Parse info of an individual movie page.

    :param url:
    :return:
    """

    title = '-'
    summary = '-'
    cast = []

    sleep(config.execute_interval_time)

    for i in xrange(0, config.try_times):
        try:
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

            return {'title': title, 'summary': summary, 'cast': cast}

        except Exception:
            traceback.print_exc()
            sleep(config.fail_wait_time)
            continue


def parse_review(url):
    """
    Parse reviews from the a certain review page.

    :param url:
    :return:
    """

    list_reviews = []

    sleep(config.execute_interval_time)

    for i in xrange(0, config.try_times):
        try:
            soup = get_page(url)

            list_summaries = soup.find_all("div", attrs={'id': 'tn15content'})[0] \
                .find_all('div', class_=None)
            list_comments = soup.select('div#tn15content > p')

            if list_comments:
                index = 0
                for summary in list_summaries:
                    title = summary.h2.text
                    if len(summary.select('> img')) != 0:
                        rating = int(summary.select('> img')[0].get('alt').split('/')[0])
                    else:
                        rating = -1
                    content = list_comments[index].getText(separator=' ').replace('\n', ' ').strip()
                    dict_review = {'title': title, 'rating': rating, 'content': content}
                    list_reviews.append(dict_review)
                    index += 1

            return list_reviews

        except Exception:
            traceback.print_exc()
            sleep(config.fail_wait_time)
            continue


def get_review_page_size(url):
    """
    Get review page size of a movie in total.

    :param url:
    :return:
    """

    sleep(config.execute_interval_time)

    for i in xrange(0, config.try_times):
        try:
            soup = get_page(url)

            page_size_info = soup.select('div#tn15content > table tr td')[0].text
            if 'Index' in page_size_info:
                return 1

            page_size = int(filter(None, re.split('[ :]+', page_size_info))[-1])

            return page_size

        except Exception:
            traceback.print_exc()
            sleep(config.fail_wait_time)
            continue


if __name__ == '__main__':
    links = grab_list()
    print [get_next_review_link(l) for l in links.values()]
    get_review_page_size('http://www.imdb.com/title/tt2316204/reviews?start=0')
