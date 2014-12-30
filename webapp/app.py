from flask import Flask, request, abort, render_template, redirect, url_for
app = Flask(__name__)

from api.leumi import BankLeumiAPI
from api.leumi_card import LeumiCardAPI
from api.common import LoginError

from crypt import encrypt_dict, decrypt_dict

from datetime import datetime

SECRET = '0123456789abcdef' # 16/32/64 chars

def abort_if_missing(*args):
    for arg in args:
        if not request.values.get(arg):
            print 'no ' + arg
            abort(400)

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        abort_if_missing('username', 'password', 'account', 'from_date', 'to_date')
        
        creds = encrypt_dict(SECRET, dict(
            username=request.form['username'], 
            password=request.form['password']
        ))

        return redirect(url_for(request.form['service'], 
            account=request.form['account'],
            from_date=request.form['from_date'],
            to_date=request.form['to_date'],
            creds=creds
        ))

@app.route('/api/bank/leumi', methods=['GET', 'POST'])
def bank_leumi():
    return do_api(BankLeumiAPI)

@app.route('/api/cc/leumi_card', methods=['GET', 'POST'])
def leumi_card():
    return do_api(LeumiCardAPI)

def do_api(api_class):
    abort_if_missing('creds', 'account', 'from_date', 'to_date')
    creds = decrypt_dict(SECRET, request.values.get('creds'))
    account = request.values['account']
    from_date = datetime.strptime(request.values['from_date'], '%d/%m/%Y')
    to_date = datetime.strptime(request.values['to_date'], '%d/%m/%Y')
    api = api_class()
    try:
        api.login(creds['username'], creds['password'])
    except LoginError:
        abort(403)
    rows = api.get_statement(account, from_date, to_date)
    return render_template('statement.html', rows=rows)

if __name__ == "__main__":
    app.config['TRAP_HTTP_EXCEPTIONS'] = True
    app.run(debug=True)
