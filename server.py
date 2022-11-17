import sys
import json
from HySQL import HySQL
from flask import Flask, request

server = Flask(__name__)
@server.route('/')
def index():
    if request.args.get('query') == None:
        return f'Please input the query with http \'?query=\' param.<br />For more info please go to <a href="https://github.com/91d906h4/HySQL" target="_blank">GitHub</a>.'
    else:
        try:
            # Query :
            # SELECT * FROM city WHERE CountryCode != 'AFG' ORDER BY Population, ID DESC LIMIT 10
            # 
            # Just replace all space with URL encode %20
            # /?query=SELECT%20*%20FROM%20city%20WHERE%20CountryCode%20!=%20%27AFG%27%20ORDER%20BY%20Population,%20ID%20DESC%20LIMIT%2010
            query = request.args.get('query') 
            result = HySQL(query).excute(view=False)
            return result
        except Exception as e:
            return json.dumps({
                "Status": False,
                "Info": str(e)
            })

@server.errorhandler(500)
def error(e):
    return json.dumps({
        "Status": False,
        "Info": str(e)
    })

# Run python ./server.py <port> to start database server
if len(sys.argv) < 2: port = 8000
else: port = sys.argv[1]
server.run(port=port)
