import flask
import json
import controller

# Flask setup
app = flask.Flask(__name__)
app.config["DEBUG"] = True


@app.route('/', methods=['GET'])
def home():
    return json.dumps({'foo': 'bar'})


@app.route('/alert', methods=['POST'])
def alert():
    irl.write()
    return json.dumps({'alert': 'test'})


app.run()
