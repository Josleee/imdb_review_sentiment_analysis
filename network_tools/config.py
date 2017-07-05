headers = {
    'headers': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/57.0.2987.133 Safari/537.36'}

# Request send interval time
execute_interval_time = 0.1
# After failure wait time
fail_wait_time = 5
# After failure try times
try_times = 5

# Box Office, Most Popular Movies, Top Rated Movies, Top Rated English Movies, Lowest Rated Movies
chart_category = ['boxoffice', 'top', 'top-english-movies', 'moviemeter', 'bottom']
# 0 ~ 4 corresponding to the specific category above respectively
category_selector = 3


# get analysed filename
def get_tag_analysed():
    return 'analyzed_' + chart_category[category_selector]


# get category frequency rate trained filename
def get_fr_trained():
    return 'trained_' + chart_category[category_selector]


# get useful categories filename
def get_useful_charts():
    return [v for v in chart_category[:]]


def get_special_analysed():
    return 'analyzed_all'


def get_special_trained():
    return 'trained_all'
