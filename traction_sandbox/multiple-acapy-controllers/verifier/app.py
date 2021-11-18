from flask import Flask, jsonify, abort, request, make_response, current_app
import logging 

app = Flask(__name__)
app.logger.setLevel(logging.INFO)

TOPICS = ['connections']

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

@app.route("/log/topic/<topic>/", methods=['POST'])
def acapy_event_handler(topic):
    app.logger.info(f'topic={topic}')
    app.logger.debug(request)

    if topic in TOPICS:
        app.logger.info(f"HANDLE {topic} event")
    else:
        app.logger.info(f"IGNORE {topic} event")

    return make_response(jsonify({'success': True}), 200)