from sys import version_info
from requests_html import HTMLSession
import time
import re
import datetime
from pprint import pprint
from bs4 import BeautifulSoup as bs


def get_wrapper(url):
    def decorator(func):
        def inner(client, *args, **kwargs):
            tic = time.perf_counter()
            res = client.get(url, verify=False)
            func(res, *args, **kwargs)
            toc = time.perf_counter()
            print(f"Finish parsing in {toc - tic:0.4f} seconds")
        return inner
    return decorator


def extract_meijumi_id(url):
    return re.findall(u'https://www.meijumi.net/(\d+)\.html', url)[0]


def construct_meijumi_show_url(show_id):
    return u'https://www.meijumi.net/{}.html'.format(show_id)

# @get_wrapper("https://www.meijumi.net/news/")


def get_news100(client):
    url = "https://www.meijumi.net/news/"
    res = client.get(url, verify=False)
    print(f"Got url {url}")
    tic = time.perf_counter()
    result = res.html.find('.news100')
    output = []
    for i, line in enumerate(result):
        spans = line.find('span')
        output.append({
            'show': spans[0].text,
            'url': spans[0].find('a')[0].attrs['href'],
            'episode': spans[1].text,
            # 'category': spans[2].text,
            'date': spans[3].text,
            # 'date': datetime.datetime.strptime(spans[3].text, '%Y-%m-%d').date()
        })
    toc = time.perf_counter()
    print(f"Finish parsing in {toc - tic:0.4f} seconds")
    return output


def get_sitemap(client):
    url = "https://www.meijumi.net/"
    res = client.get(url, verify=False)
    tic = time.perf_counter()
    nav = res.html.find('#site-nav > div > ul', first=True)
    for li in nav.element:
        sub_menu = li.find('ul')
        sub_menu_data = []
        if sub_menu != None:
            for sub_li in sub_menu.findall('li'):
                sub_a = sub_li.find('a')
                sub_menu_data.append({
                    'title': sub_a.text,
                    'url': sub_a.get('href')
                })
        a = li.find('a')
        yield {
            'title': a.text,
            'url': a.get('href'),
            'children': sub_menu_data
        }
    toc = time.perf_counter()
    print(f"Finish parsing in {toc - tic:0.4f} seconds")


def get_meiju(client, id):
    def get_playlist(html):
        soup = bs(html, 'html.parser')
        line_list = [item for item in soup.children if str(
            item) != '\n' and (item.name and item.name != 'span')]
        result = []
        temp = []
        for item in line_list:
            if item.name and item.name == 'br' and temp != []:
                result.append(temp)
                temp = []
            else:
                if type(item) == NavigableString:
                    item_text = str(item).strip()
                    if str(item) != '|':
                        temp.append(item_text)
                else:
                    temp.append(item)
            line_list.remove(item)
        result.append(line_list)

        for line in result:
            line_dict = {}
            for item in line:
                if type(item) == NavigableString:
                    line_dict[str(item)] = None
                else:
                    line_dict[item.text.strip()] = {
                        'title': item.text.strip(),
                        'url': item['href'],
                    }

    def parse_text(text):
        text = text.replace('\xa0', '')
        text = text.replace('•', '')
        text = text.replace(':', '')
        text = text.replace(' ', '')
        return text

    url = 'https://www.meijumi.net/%s.html' % id
    res = client.get(url, verify=False)
    print(f"Got url {url}")
    soup = bs(res.html.html, 'html.parser')
    table = res.html.find('tbody')[0].element
    detail_data = {}
    for line in table:
        key = parse_text(line[0].xpath('string()'))
        value = parse_text(line[1].xpath('string()'))
        detail_data[key] = value
    img = res.html.xpath(
        '/html/body/div[1]/div[1]/div[2]/main/article/div[3]/div[1]/p[1]/img')[0].attrs.get('src')
    for ad in soup.select('.google-auto-placed'):
        ad.decompose()
    return {
        'detail': detail_data,
        'img': img,
        'playplist_html': ''
    }


def main():
    client = HTMLSession()

    # result = get_news100(client)
    # result = get_sitemap(client)
    result = get_meiju(client, '32173')

    # tic = time.perf_counter()
    # result = list(result)
    # toc = time.perf_counter()
    # print(f"Finish converting to list in {toc - tic:0.4f} seconds")
    pprint(result)

    # result = sorted(result, key=lambda x: x['time'], reverse=True)
    # pprint([f"{line['index']}  {line['time']}" for line in result])


if __name__ == '__main__':
    main()
