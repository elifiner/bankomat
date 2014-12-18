import os
import requests
from urlparse import urljoin
from bs4 import BeautifulSoup

DEFAULT_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'

class Browser(object):
    def __init__(self, user_agent=DEFAULT_AGENT, progress=lambda: None):
        self.session = requests.Session()
        self.session.headers.update({'user-agent':user_agent})
        self.progress = progress
        self.hooks = dict(response=lambda r, *a, **k: self.progress())
        self.page = None

    def get(self, url):
        if self.page:
            url = urljoin(self.page.url, url)
        self.page = Page(self, self.session.get(url, hooks=self.hooks))
        return self.page

    def post(self, url, data):
        if self.page:
            url = urljoin(self.page.url, url)
        self.page = Page(self, self.session.post(url, data=data, hooks=self.hooks))
        return self.page

class Page(object):
    def __init__(self, browser, response):
        self.browser = browser
        self.response = response
        self.soup = BeautifulSoup(self.response.text)

    def preview(self):
        with open('temp.html', 'w') as f:
            f.write(str(self.soup))
        os.system('open temp.html')

    def forms(self, selector=''):
        return [Form(self, f) for f in self.soup.select('form' + selector)]

    def form(self, selector=''):
        return self.forms(selector)[0]

    def links(self, selector='', text=''):
        links = [Link(self, f) for f in self.soup.select('a' + selector)]
        if text:
            links = [l for l in links if text in l.text]
        return links

    def link(self, selector='', text=''):
        return self.links(selector, text)[0]

    def tables(self, selector=''):
        return [Table(self, f) for f in self.soup.select('table' + selector)]

    def table(self, selector=''):
        return self.tables(selector)[0]

    @property
    def url(self):
        return self.response.url

    @property
    def text(self):
        return self.response.text

    @property
    def status(self):
        return self.response.status_code

class Form(object):
    def __init__(self, page, soup):
        self.page = page
        self.soup = soup

    def submit(self, values=None, **kw):
        fields = self.get_defaults()
        fields.update(values or {})
        fields.update(kw)
        action = urljoin(self.page.url, self.soup.get('action'))
        return self.page.browser.post(action, fields)

    def get_defaults(self):
        fields = {}

        enabled = lambda el:  el.get('disabled') != 'disabled'
        selected = lambda el:  el.get('selected') != 'selected'

        # get default values for input fields
        for el in self.soup.select('input') + self.soup.select('textarea'):
            if el.get('name') and enabled(el):
                fields[el.get('name')] = el.get('value') or ''

        # get default values for select fields
        for el in self.soup.select('select'):
            if el.get('name') and enabled(el):
                for option in el.select('option'):
                    if selected(option):
                        fields[el.get('name')] = option.get('value').strip()
                        break

        return fields

    def __repr__(self):
        return 'Form<name=%s;id=%s>' % (self.soup.get('name'),self.soup.get('id'))

class Link(object):
    def __init__(self, page, soup):
        self.page = page
        self.soup = soup

    @property
    def text(self):
        return self.soup.string or ''

    @property
    def url(self):
        return urljoin(self.page.url, self.soup.get('href'))

    def __repr__(self):
        return 'Link<%s:%s>' % (self.text, self.url)

class Table(object):
    def __init__(self, page, soup):
        self.page = page
        self.soup = soup

    @property
    def headers(self):
        tr = self.soup.select('tr')[0]
        ths = tr.select('th')
        if ths:
            return [soup2text(th) for th in ths]
        return []

    @property
    def rows(self):
        for tr in self.soup.select('tr'):
            tds = tr.select('td')
            if tds:
                yield [soup2text(td) for td in tds]

    def __repr__(self):
        return 'Table<%d rows>' % len(self.soup.select('tr'))
 
def soup2text(soup):
    return ' '.join(soup.stripped_strings)
