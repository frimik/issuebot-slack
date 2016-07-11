from jiraslacker import app
from flask import request, Response, jsonify
from config import SLACK_WEBHOOK_SECRET
from jiraslacker.slacker import JiraSlacker


@app.route('/slack/jira', methods=['POST'])
def inbound():
    if request.form.get('token') == SLACK_WEBHOOK_SECRET:
        channel = request.form.get('channel_name')
        username = request.form.get('user_name')
        text = request.form.get('text')
        inbound_message = username + " in " + channel + " says: " + text
        app.logger.info(inbound_message)
        app.logger.info(request.form)
        response = JiraSlacker.process(text)
        return jsonify(response)
    return Response(), 403


@app.route('/healthcheck', methods=['GET'])
def healthcheck():
    if request.headers.get('User-Agent').startswith('ELB'):
        return Response(), 200
    else:
        return Response(), 412
