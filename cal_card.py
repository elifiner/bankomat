#coding=utf8
import sys
from browser import Browser

import config

def progress():
    sys.stderr.write('.')


browser = Browser(progress=progress)
browser.get('https://services.cal-online.co.il/Card-Holders/SCREENS/AccountManagement/Login.aspx')
form = browser.form()
form.submit({
    'ctl00$FormAreaNoBorder$FormArea$lgnLogin$UserName': config.CAL_USERNAME,
    'ctl00$FormAreaNoBorder$FormArea$lgnLogin$Password': config.CAL_PASSWORD
})
if not browser.url.endswith('/AccountManagement/HomePage.aspx'):
    raise Exception('login error')

# WTF: to select a card, we need to navigate to appropriate CardDetails.aspx link
# which sets a cookie that affects which card is shown in Transactions.aspx
cards = {}
for a in browser.soup.select('a'):
    if a.get('href', '').startswith('CardDetails.aspx'):
        cards[a.parent.parent.get('id')] = a.get('href')

# select credit card
browser.get(cards['5924'])

browser.get('/Card-Holders/SCREENS/Transactions/Transactions.aspx')
form = browser.form()

form.submit({
    '__EVENTARGUMENT': 'NewRequest',
    '__EVENTTARGET': 'SubmitRequest',
    'ctl00$FormAreaNoBorder$FormArea$clndrDebitDateScope$HiddenField': '17', # FIXME: value from month selection <li>
    'ctl00$FormAreaNoBorder$FormArea$rdogrpSummaryReport': 'rdoAggregationNone',
    'ctl00$FormAreaNoBorder$FormArea$rdogrpTransactionType': 'rdoDebitDate',

    # those are fields we don't use in the form but they need values
    'ctl00$FormAreaNoBorder$FormArea$ctlDateScopeEnd$ctlDaysList$HiddenField': '1',
    'ctl00$FormAreaNoBorder$FormArea$ctlDateScopeEnd$ctlMonthYearList$HiddenField': '1',
    'ctl00$FormAreaNoBorder$FormArea$ctlDateScopeStart$ctlDaysList$HiddenField': '1',
    'ctl00$FormAreaNoBorder$FormArea$ctlDateScopeStart$ctlMonthYearList$HiddenField': '1',
})

table = browser.table('#ctlMainGrid')
print ','.join(table.headers)
for row in list(table.rows)[:-1]:
    print ','.join(row)