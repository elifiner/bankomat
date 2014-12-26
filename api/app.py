from flask import Flask, request, abort
from jinja2 import Template
app = Flask(__name__)

from scrape.leumi import BankLeumiAPI

TEMPLATE = '''
<style>
    body { direction: rtl; }
    table { border-collapse: collapse; }
    td { padding: 5px; border: 1px solid #ccc; }
</style>
<body>
<table>
    {%- for row in rows %}
    <tr>{% for cell in row[:6] %}<td>{{cell}}</td>{% endfor %}</tr>
    {%- endfor %}
</table>
</body>
'''

@app.route('/api/bank_leumi/<account>', methods=['GET', 'POST'])
def bank_leumi(account):
    username = request.values.get('username')
    password = request.values.get('password')
    if not username or not password:
        abort(400)
    api = BankLeumiAPI()
    api.login(username, password)
    template = Template(TEMPLATE)
    rows = api.get_statement(None,None,None)
    return template.render(rows=rows)

if __name__ == "__main__":
    app.run(debug=True)
