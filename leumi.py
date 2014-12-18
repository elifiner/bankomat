# coding=utf8
import sys
from browser import Browser

import config

def progress():
    sys.stderr.write('.')

if __name__ == '__main__':
    browser = Browser(progress=progress)
    browser.get('https://hb2.bankleumi.co.il/H/Login.html')
    browser.page.form('#login').submit(uid=config.LEUMI_USERNAME, password=config.LEUMI_PASSWORD)
    browser.get('/eBanking/SSOLogin.aspx?SectorCheck=Override')
    browser.get('/eBanking/Accounts/ExtendedActivity.aspx')
    # FIXME: select account by account number
    # FIXME: get dates form parameters
    browser.page.form().submit({
        'ddlAccounts$m_ddl'      : '1',
        'ddlTransactionType'     : '001',
        'ddlTransactionPeriod'   : '004', 
        'dtFromDate$textBox'     : '01/08/14',
        'dtToDate$textBox'       : '01/10/14',
        'btnDisplayDates.x'      : 0,
        'btnDisplayDates.y'      : 0        
    })
    table = browser.page.table('.dataTable')
    print
    print ','.join(table.headers)
    for row in table.rows:
        print ','.join(row)
