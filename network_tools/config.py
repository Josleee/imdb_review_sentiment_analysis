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
chart_category = ['boxoffice', 'moviemeter', 'top', 'top-english-movies', 'bottom']
# 0 ~ 4 corresponding to the specific category above respectively
category_selector = 0


# tags
def get_tag_analyzed():
    return 'analyzed_' + chart_category[category_selector]


# frequency rate
def get_fr_analyzed():
    return 'trained_' + chart_category[category_selector]
