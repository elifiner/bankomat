from flask import Flask
from jinja2 import Template
app = Flask(__name__)

from leumi import BankLeumiAPI
import config

TEMPLATE = '''
<style>
body { direction: rtl; }
table { border-collapse: collapse; }
td { padding: 5px; border: 1px solid #ccc; }
</style>
<body>
<table>
    {% for row in rows %}
    <tr>
        {% for cell in row[:6] %}
        <td>{{cell}}</td>
        {% endfor %}
    </tr>
    {% endfor %}
</table>
</body>
'''

@app.route('/api/bank_leumi/<account>')
def bank_leumi(account):
    api = BankLeumiAPI()
    api.login(config.LEUMI_USERNAME, config.LEUMI_PASSWORD)
    template = Template(TEMPLATE)
    rows = api.get_statement(None,None,None)
    return template.render(rows=rows)

if __name__ == "__main__":
    app.run(debug=True)