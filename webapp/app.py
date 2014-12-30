from flask import Flask, request, abort, render_template, redirect, url_for
app = Flask(__name__)

from api.leumi import BankLeumiAPI
from api.leumi_card import LeumiCardAPI
from api.common import LoginError

from crypt import encrypt_dict, decrypt_dict

SECRET = '0123456789abcdef' # 16/32/64 chars

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        account = request.form.get('account')
        service = request.form.get('service')

        if not (username and password and account):
            abort(400)
        
        creds = encrypt_dict(dict(username=username, password=password), SECRET)

        if service == 'bank_leumi':
            return redirect(url_for('bank_leumi', account=account, creds=creds))

        if service == 'leumi_card':
            return redirect(url_for('leumi_card', account=account, creds=creds))

        abort(400)

@app.route('/api/bank/leumi', methods=['GET', 'POST'])
def bank_leumi():
    creds = decrypt_dict(request.values.get('creds'), SECRET)
    account = request.values.get('account')
    username = creds.get('username')
    password = creds.get('password')
    if not (username and password and account):
        abort(400)
    api = BankLeumiAPI()
    try:
        api.login(username, password)
    except LoginError:
        abort(403)
    rows = api.get_statement(None,None,None)
    return render_template('statement.html', rows=rows)

@app.route('/api/cc/leumi_card', methods=['GET', 'POST'])
def leumi_card():
    creds = decrypt_dict(request.values.get('creds'), SECRET)
    account = request.values.get('account')
    username = creds.get('username')
    password = creds.get('password')
    if not (username and password and account):
        abort(400)
    api = LeumiCardAPI()
    try:
        api.login(username, password)
    except LoginError:
        abort(403)
    rows = api.get_statement(None,None)
    return render_template('statement.html', rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
