# coding=utf8
import sys
from browser import Browser
from common import LoginError

class BankLeumiAPI(object):
    def __init__(self, progress=lambda: None):
        self.browser = Browser(progress=progress)

    def login(self, username, password):
        self.browser.get('https://hb2.bankleumi.co.il/H/Login.html')
        self.browser.form('#login').submit(uid=username, password=password)
        if not self.browser.url.endswith('/InternalSite/Validate.asp'):
            raise LoginError('login error')
        self.browser.get('/eBanking/SSOLogin.aspx?SectorCheck=Override', allow_redirects=False)

    def get_statement(self, account, from_date, to_date):
        self.browser.get('/eBanking/Accounts/ExtendedActivity.aspx')
        data = {
            # FIXME: select the correct account
            # FIXME: date selection doesn't work
            'ddlAccounts$m_ddl'      : '1',
            'ddlTransactionType'     : '001',
            'ddlTransactionPeriod'   : '004', # between dates
            'dtFromDate$textBox'     : from_date.strftime('%d/%m/%y'),
            'dtToDate$textBox'       : to_date.strftime('%d/%m/%y'),
        }
        self.browser.form().submit(data)
        table = self.browser.table('.dataTable')
        yield table.headers[:6]
        for row in table.rows:
            yield row[:6]

if __name__ == '__main__':
    from datetime import datetime
    from cred import get_cred
    def progress():
        sys.stderr.write('.')
    api = BankLeumiAPI(progress=progress)
    api.login(get_cred('leumi_username'), get_cred('leumi_password'))
    for line in api.get_statement(None,datetime(2014,7,1),datetime(2014,9,1)):
        print ','.join(line)
