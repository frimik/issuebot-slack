from gevent import monkey; monkey.patch_all()

from flask import Flask
from jiraslacker.models import db, JiraServer
from jiraslacker.app import FlaskApp

def main():
    app = FlaskApp(__name__)
    with app.app_context():
        db.init_app(app)
        jira = JiraServer('https://jira.atlassian.com')

        jira.cache_project_keys()
        projects = jira.projects()

        keys = sorted([project.key for project in projects])
        print(keys)


#    issue = jira.issue('UO-53')
#
#    import re
#    ea_comments = [
#        comment for comment in issue.fields.comment.comments
#        if re.search(r'@ea.com$', comment.author.emailAddress)]
#
#    click.echo(ea_comments)


if __name__ == "__main__":
    main()
