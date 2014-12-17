import os
import sys
import requests
from bs4 import BeautifulSoup

class Browser(object):
    def __init__(self, progress=lambda: None):
        self.session = requests.Session()
        self.progress = progress
        self.hooks = dict(response=lambda r, *a, **k: self.progress())

    # def print_url(self, r, *args, **kwargs):
        

    def get(self, url):
        return Page(self, self.session.get(url, hooks=self.hooks))

    def post(self, url, data):
        return Page(self, self.session.post(url))

class Page(object):
    def __init__(self, browser, response):
        self.response = response
        self.soup = BeautifulSoup(self.response.content)

    def preview(self):
        with open('temp.html', 'w') as f:
            f.write(self.response.content)
        os.system('open temp.html')

    def forms(self, selector=''):
        return [Form(self, f) for f in self.soup.select('form' + selector)]

    def form(self, selector=''):
        return self.forms(selector)[0]

class Form(object):
    def __init__(self, browser, soup):
        self.soup = soup

    @property
    def action(self):
        return self.soup.get('action')

    def __repr__(self):
        return 'Form<%s>' % self.action

if __name__ == '__main__':
    def progress():
        sys.stderr.write('.')
    br = Browser(progress=progress)
    login = br.get('https://hb2.bankleumi.co.il/H/Login.html')
    print login.forms()
    print login.form('#login').soup