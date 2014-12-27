from flask import Flask, request, abort, render_template, redirect, url_for
app = Flask(__name__)

from api.leumi import BankLeumiAPI
from api.common import LoginError

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

        if service == 'bank_leumi':
            return redirect(url_for('bank_leumi',
                account=account, 
                username=username, 
                password=password
            ))

        abort(400)

@app.route('/api/bank/leumi', methods=['GET', 'POST'])
def bank_leumi():
    account = request.values.get('account')
    username = request.values.get('username')
    password = request.values.get('password')
    if not (username and password and account):
        abort(400)
    api = BankLeumiAPI()
    try:
        api.login(username, password)
    except LoginError:
        abort(403)
    rows = api.get_statement(None,None,None)
    return render_template('statement.html', rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
