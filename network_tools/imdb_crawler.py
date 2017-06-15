import re
import traceback
from time import sleep

import requests
from bs4 import BeautifulSoup

import config


def get_page(url, sleep_time=config.interval_sleep_time, try_times=config.try_times):
    """
    Parse the page for a certain url.

    :param url:
    :param sleep_time:
    :param try_times:
    :return:
    """

    for i in xrange(0, try_times):
        try:
            url = url.rstrip('\n')
            r = requests.get(url, headers=config.headers)
            if r.status_code != 200:
                sleep(sleep_time)
                continue
            html = r.text
            soup = BeautifulSoup(html, 'lxml')
            return soup
        except Exception:
            traceback.print_exc()
            sleep(sleep_time)
            continue


def grab_list():
    """
    This will grab the links of movie from movies chart.

    :return:
    """

    dict_links = {}
    base_url = 'http://www.imdb.com'
    url = base_url + '/chart/' + config.grab_list_category

    try:
        soup = get_page(url)
        titles = soup.select('.titleColumn a')
        for title in titles:
            dict_links[title.text] = base_url + title['href']

    except Exception:
        traceback.print_exc()
    finally:
        return dict_links


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
            return link.split('?')[0] + '/reviews?start=0'
    except Exception:
        traceback.print_exc()


def parse_movie(url, sleep_time=config.interval_sleep_time):
    """
    Parse info of an individual movie page.

    :param url:
    :param sleep_time:
    :return:
    """

    record = {}
    title = '-'
    summary = '-'
    cast = []

    sleep(sleep_time)
    print('Processing..' + url)

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

        record = {'title': title, 'summary': summary, 'cast': cast}

    except Exception:
        traceback.print_exc()
    finally:
        return record


def parse_review(url, sleep_time=config.interval_sleep_time):
    """
    Parse reviews from the a certain review page.

    :param url:
    :param sleep_time:
    :return:
    """

    list_reviews = []

    sleep(sleep_time)

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

    except Exception:
        traceback.print_exc()
    finally:
        return list_reviews


def get_review_page_size(url, sleep_time=config.interval_sleep_time):
    """
    Get review page size of a movie in total.

    :param url:
    :param sleep_time:
    :return:
    """

    sleep(sleep_time)

    try:
        soup = get_page(url)

        page_size_info = soup.select('div#tn15content > table tr td')[0].text
        page_size = int(filter(None, re.split('[ :]+', page_size_info))[-1])

        return page_size

    except Exception:
        traceback.print_exc()
        return 0


if __name__ == '__main__':
    links = grab_list()
    print [get_next_review_link(l) for l in links.values()]
    get_review_page_size('http://www.imdb.com/title/tt2316204/reviews?start=0')
