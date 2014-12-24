import sys
from browser import Browser, soup2text
import config

class LeumiCardAPI(object):
    def __init__(self, progress=lambda: None):
        self.browser = Browser(progress=progress)

    def login(self, username, password):
        self.browser = Browser(progress=progress)
        self.browser.get('https://online.leumi-card.co.il/Anonymous/Login/CardHoldersLogin.aspx')
        form = self.browser.form("#loginform")
        form.submit(username=username, password=password)
        if not self.browser.url.endswith('/Registred/HomePage.aspx'):
            raise Exception('login error')

    def get_statement(self, card_number, from_date, to_date):
        #FIXME: use parameters when getting data (convert dates to months)
        #FIXME: get foreign transactions as well (TableType='ForeignTransactions')
        params = dict(
            PrintType='TransactionsTable',
            CardIndex='0',
            TableType='NisTransactions',
            ActionType='MonthCharge',
            FilterParam='AllTranactions',
            CycleDate='201412',
            FromDate='',
            ToDate='',
            SortDirection='Ascending',
            SortParam='PaymentDate',
            NextBillingCycleDate='',
            LastStatementDate='',
        )
        self.browser.get('/Popups/Print.aspx', params=params)
        table = self.browser.table()
        yield table.headers

        # can't use browser.table since we only need some rows
        for tr in table.soup.select('tr'):
            if tr.get('id', '').startswith('tbl1_lvTransactions_trRegular'):
                tds = tr.select('td')
                cells = [soup2text(td) for td in tds]
                yield cells

if __name__ == '__main__':
    def progress():
        sys.stderr.write('.')
    api = LeumiCardAPI(progress=progress)
    api.login(config.LEUMICARD_USERNAME, config.LEUMICARD_PASSWORD)
    for line in api.get_statement(None,None,None):
        print ','.join(line)
