from message import send_to_slack_user
from logger import logger, pp
from user import User

def gh_event_handler(event):
    event_action = event['action']
    if event_action == 'review_requested' or event_action == 'review_request_removed':
        review_requested_handler(event)
    else:
        logger.info('I am else of gh_event_handler')

"""
review_requested and review_request_removed events handle
"""
def review_requested_handler(event):
    event_action = event['action']
    pull_request = event['pull_request']

    # requested or removed reviewer
    reviewer = User(event['requested_reviewer']['login'])

    # we cannot send notification when there is no slack_id to notify
    if reviewer.slack_id is None:
        return

    sender_user = User(event['sender']['login'])
    # if slack_id is not available, use github_id instead
    sender_slack_id = sender_user.github_id if sender_user.slack_id is None else sender_user.slack_id

    # pull request meta data
    pull_number = pull_request['number']
    pull_url = pull_request['html_url']
    pull_title = pull_request['title']

    pull_str = '<{2}|#{0}: {1}>'.format(pull_number, pull_title, pull_url)

    if event_action == 'review_requested':
        reminder_message = '<@{0}> requested you to review {1}'.format(sender_slack_id, pull_str)
    elif event_action == 'review_request_removed':
        reminder_message = 'You are removed as a reviewer for pull request {0}'.format(pull_str)

    send_to_slack_user(reminder_message, '@' + reviewer.slack_id)
    logger.info('remind message %s', reminder_message)

