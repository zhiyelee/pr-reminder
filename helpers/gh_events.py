from message import send_to_slack_user
from logger import logger, pp
from user import User
from gh_api import get_review_comments
from tools import get_pull_request_string, timestamp_from_utc_string
from status_events_helper import on_ci_status_update, on_pr_update, store_pr_map

""" 
event dispatcher
"""
def gh_event_handler(event_category, event):
    event_action = event.get('action')
    if event_category == 'status':
        on_ci_status_update(event)
    elif event_category == 'pull_request':
        if event_action in ['opened', 'synchronize']:
            on_pr_update(event)
    else:
        if event_action in ['review_requested', 'review_request_removed']:
            review_requested_handler(event)
        elif event_action == 'submitted':
            review_submitted_handler(event)
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

    pull_str = '<{0}|#{1}: {2}>'.format(pull_url, pull_number, pull_title)

    if event_action == 'review_requested':
        reminder_message = '<@{0}> requested you to review {1}'.format(sender_slack_id, pull_str)
    elif event_action == 'review_request_removed':
        reminder_message = 'You are removed as a reviewer for pull request {0}'.format(pull_str)

    send_to_slack_user(reminder_message, '@' + reviewer.slack_id)
    logger.info('remind message %s', reminder_message)

def review_submitted_handler(event):
    repo = event['repository']
    review = event['review']
    pull_request = event['pull_request']
    pull_request_owner = User(pull_request['user']['login'])

    # we can not notify when we don't know the slack id
    if pull_request_owner.slack_id is None:
        return

    """
    single response on review comment will generate a review with body `None`, which body is empty string for normal no
      message review submission. We don't want to send notifications for these replied, because there might be too much
    """
    if review['body'] is None:
        return

    reviewer = User(review['user']['login'])

    # get review comments asscociated with this reiview
    review_comments = get_review_comments(repo['owner']['login'], repo['name'], pull_request['number'], review['id'])

    pull_str = get_pull_request_string(pull_request['html_url'], pull_request['number'], pull_request['title'])
    reviewer_slack_id = reviewer.github_id if reviewer.slack_id is None else reviewer.slack_id
    review_url = review['html_url']

    message = 'Your PR {0} received new review from <@{1}>, check it out'.format(
        pull_str,
        reviewer_slack_id)

    message_color_map = {
        'commented': '#0084FA',
        'approved': '#22BE57',
        'changes_requested': '#CF1833',
    }
    message_color = message_color_map[review['state']]
    # uppercase first letter of each word, like `change_requested` to `Change Requested`
    pull_state = review['state'].replace('_', ' ').title()
    attachment_title = 'Review for #{0}: {1}'.format(pull_request['number'], pull_request['title'])

    attachments = [{
        'fallback': attachment_title,
        'title': attachment_title,
        'title_link': review_url,
        'author_name': reviewer_slack_id,
        'color': message_color,
        'author_link': review_url,
        'text': review.get('body', 'no message'),
        'footer': 'Pull Reminder',
        'ts': timestamp_from_utc_string(review['submitted_at']),
        'mrkdwn_in': ['text'],
        'fields':[
            { 'title': 'State', 'value': pull_state },
            { 'title': 'Comments Count', 'value': len(review_comments) },
        ],
    }]

    send_to_slack_user(message, '@' + pull_request_owner.slack_id, attachments)



