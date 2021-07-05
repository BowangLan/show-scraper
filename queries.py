
def valid_shows(shows):
    return filter(lambda item: item.name and item.last_update, shows)


def get_latest_news(news):
    return news


def search_show_name(shows, keyword):
    return filter(lambda item: keyword in item.name, valid_shows(shows))
