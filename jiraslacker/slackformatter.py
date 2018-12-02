import logging

logger = logging.getLogger(__name__)


class SlackFormatter(object):

    """Formats Slack response messages"""

    def __init__(self, issues=[], response_type="ephemeral", detailed=False):
        """TODO: to be defined1. """
        self.issues = issues
        self.response_type = response_type
        self.detailed = detailed

    def format_response(self):
        """Format a Slack response message for JIRA details"""
        _response_dict = {
            'response_type': self.response_type,
            'text': self.format_issues(),
        }
        return _response_dict

    def format_issues(self):
        _formatted_issues = []
        # Looks nicer if issues are returned sorted by key.
        for issue in sorted(self.issues, key=lambda i:  i.key):
            _formatted_issues.append(self.format_issue(
                issue, detailed=self.detailed)
            )

        return "\n".join(_formatted_issues)

    @classmethod
    def format_issue(cls, issue, detailed=False):
        if detailed:
            return 'Not implemented'
        else:
            return '*{0}* ({1}): `{2}` {3} - {4}'.format(
                issue.key, issue.fields.issuetype, issue.fields.status,
                issue.fields.summary, issue.permalink())
