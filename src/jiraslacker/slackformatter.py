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
        for issue in self.issues:
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

    @staticmethod
    def object_to_message(obj):
        if isinstance(obj, list):
            return SlackFormatter.format_message("\n".join(obj))
        elif isinstance(obj, str):
            return SlackFormatter.format_message(obj)

    @staticmethod
    def format_message(text):
        _response_dict = {
            'response_type': 'ephemeral',
            'text': text,
        }
        return _response_dict
