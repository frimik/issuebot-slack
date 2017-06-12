from gevent import monkey;

monkey.patch_all()  # noqa
from flask import request, Response, jsonify
from .app import app
from .slacker import JiraSlacker

SLACK_WEBHOOK_SECRET = 'secret'


@app.route('/slack/jira', methods=['POST'])
def inbound():
    if request.form.get('token') != SLACK_WEBHOOK_SECRET:
        return Response(), 403

    channel = request.form.get('channel_name')
    username = request.form.get('user_name')
    text = request.form.get('text')
    inbound_message = username + " in " + channel + " says: " + text
    app.logger.info(inbound_message)
    app.logger.info(request.form)
    response = JiraSlacker.process_request(request)
    return jsonify(response)


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    if request.headers.get('User-Agent').startswith('ELB'):
        return Response(), 200
    else:
        return Response(), 412
