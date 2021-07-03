import re
import urllib3
from time import perf_counter
from requests_html import HTMLSession
from models import Show, EpisodeNews

urllib3.disable_warnings()


class MeijumiParser(object):

    def extract_all_shows(self, res):
        """
        Extract all show links from a response of a page
        :param res: 
        """
        html = res.html.html
        links = re.findall(u'(https://www.meijumi.net/(?:\d+)\.html', html)
        return links

    def parse_show_info(self, res):
        """
        Extract the show information from a response of a show page
        :param res: 
        """
        show = Show()

        content = res.html.find('.single-content')[0].html

        # get the title
        # title = re.findall(
        #     u'《(.+?)》', res.html.find('h1.entry-title')[0].html)[0]
        show.name = re.findall(
            u'《(.+?(?:第(?:.+?)季)?)》', res.html.find('h1.entry-title')[0].html
        )[0]

        # get the original title
        original_name = re.findall(
            u'英文全名(.+?)(?:\s*?\(\d{4}\))', content
            # u'英文全名(.+?)(?:\sSeason\s\d{1,2})?(?:\s\s\(\d{4}\))', content
        )
        show.original_name = original_name[0] if original_name != [] else ''

        # get the img url
        show.img = re.findall(u'<img.+?src="(.+?)".+?>', content)[0]

        # output = {
        #     'name': title,
        #     'original_name': original_name,
        #     'img': img,
        #     # 'season': season
        # }

        return show

    def parse_show_episode_info(self, res):
        """
        Extract episode information from a response of a show page
        Return format: [
            [ # a block
                [ # a line/episode
                    {
                        name: str
                        url: str | None
                        passcode: str | None
                    }
                ]
            ]
        ]
        """
        def parse_item(i, item):
            # (url, name, passcode)
            link = re.findall(
                u'<a href="(.+?)"[^>]+?>(.+?)</a>(?:\s+(?:密码：)??(.{4}))?', item)

            if not link:
                temp_link = item.replace('<br>', '').replace(
                    '<br/>', '').replace('</p>', '')
                temp_link = {
                    'url': '',
                    'name': '',
                    'passcode': ''
                }
            else:
                link = list(link[0])
                temp_link = {
                    'url': link[0],
                    'name': link[1],
                    'passcode': link[2]
                }

            if i == 0:
                e_name = re.findall(u'S\d{2}E\d{2}', line)[0]
                if temp_link['name'][:6] != e_name:
                    temp_link['name'] = e_name + '.' + temp_link['name']
            return link

        def parse_line(line):
            items_1 = re.split(u'\s\|\s', line)
            items_2 = re.split(u'\s\s', line)
            if len(items_1) == 1 and len(items_2) != 1:
                line = items_2
            else:
                line = items_1
            items = []
            for i, item in enumerate(line):
                items.append(parse_item(i, item))
            return items

        output = []

        # find and parse all p tag (all blocks)
        p_list = res.html.find('.single-content')[0].find('p')
        for p in p_list:
            p = p.html
            # if 'FIX字幕侠高清资源' in p:
            #     lines = re.findall(u'((?:<a.+?>)?S\d{2}E\d{2}.+?(?:</p>|<br>|<br/>))', p)

            block_output = []

            # find all episode lines
            lines = re.findall(
                u'((?:<a.+?>)?S\d{2}E\d{2}.+?(?:</p>|<br>|<br/>))', p)

            # if no episode lines are found, skip the block
            if lines == []:
                continue

            # parse line by line
            for line in lines:
                block_output.append(parse_line(line))

            output.append(block_output)

        return output


class MeijumiAPI(object):

    BASE_URL = "https://www.meijumi.net/"
    NEWS_URL = 'https://www.meijumi.net/news/'

    def __init__(self) -> None:
        self.session = HTMLSession()
        self.parser = MeijumiParser()

    def get_news(self):
        print("Updating episode news...")

        # send the request
        tic = perf_counter()
        res = self.session.get(self.NEWS_URL, verify=False)
        print(f"Get page in {perf_counter() - tic:0.4f} seconds")

        # parse the response
        output = []
        result = res.html.find('.news100')
        for i, line in enumerate(result):
            spans = line.find('span')
            episode_news = EpisodeNews(
                show=spans[0].text,
                url=spans[0].find('a')[0].attrs['href'],
                episode=spans[1].text,
                date=spans[3].text
            )
            # 'category': spans[2].text,
            output.append(episode_news)
        return output

    def get_sitemap(self):
        # send the request
        tic = perf_counter()
        res = self.session.get(self.BASE_URL, verify=False)
        print(f"Get page in {perf_counter() - tic:0.4f} seconds")

        output = []
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
            output.append({
                'title': a.text,
                'url': a.get('href'),
                'children': sub_menu_data
            })
        return output

    def get_page_shows(self, url):
        """
        Get all show links of a page. Return a list of Show object.
        """
        tic = perf_counter()
        res = self.session.get(self.BASE_URL, verify=False)
        print(f"Get page in {perf_counter() - tic:0.4f} seconds")

        links = self.parser.extract_all_shows(res)
        return links

    def get_show_by_id(self, show_id):
        show = Show()
        show.meijumi_id = show_id
        url = show.url
        return self.get_show(url)

    def get_show(self, url):
        """
         - send and get the html of the show page
         - parse the page to get show information
         - parse the page to get episode information
        Parameters: must provide either a Show object or an url
        """
        print("\nTrying to get show url: " + url)

        # send the request
        tic = perf_counter()
        res = self.session.get(url, verify=False)
        print(f"Get page in {perf_counter() - tic:0.4f} seconds")

        # parse and extract information
        show = self.parser.parse_show_info(res)
        show.url = url
        episode_info = self.parser.parse_show_episode_info(res)

        return (show, episode_info)
