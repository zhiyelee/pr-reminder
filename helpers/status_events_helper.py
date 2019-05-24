from message import send_to_slack_user
from logger import logger, pp
from user import User
from lib.cache import cache
from gh_api import get_commit_status, get_pull_request
from tools import get_pull_request_string, timestamp_from_utc_string
from helpers.emojis import NAMES_EMOJI

def store_pr_map(cache_key, pr_id):
    return cache.set(cache_key, pr_id)

"""
cache_key: for pr and commit map, the key is `repo#repo_id:commit#commit_sha`
"""
def get_pr_id(cache_key):
    return cache.get(cache_key)

"""  
get the sha to pr_id map cache key
"""
def get_pr_cache_key(repo_id, head_sha):
    return 'repo#{0}:sha#{1}'.format(repo_id, head_sha) 

def on_pr_update(event):
    pull_request = event['pull_request']
    sha = pull_request['head']['sha']
    repo_id = event['repository']['id']
    cache_key = get_pr_cache_key(repo_id, sha)
    # store sha to pr id:url map
    # cache_value = '{0}##{1}'.format(pull_request['id'], pull_request['html_url'])
    store_pr_map(cache_key, pull_request['number'])

"""
status events handler
"""
def on_ci_status_update(event):
    commit_sha = event['sha']
    repo_id = event['repository']['id']
    cache_key = get_pr_cache_key(repo_id, commit_sha)
    pull_request_id = get_pr_id(cache_key)
    """ do nothing if there is no this device id, and log error """
    if pull_request_id is None:
        logger.error('No matching pull for key: %s', cache_key)
        return

    repo = event['repository']
    repo_owner = repo['owner']['login']
    repo_name = repo['name']
    status = get_ci_result(repo_owner, repo_name, commit_sha)

    """
    the pull_request object here is a github3.pulls.PullRequest instance which is different from
        the pull_request dict which get from the event object
    """
    pr = get_pull_request(repo_owner, repo_name, pull_request_id)
    send_ci_update_message(pr, status, event['updated_at'])

def get_ci_result(repo_owner, repo_name, commit_sha):
    """ get combined status of the commit """
    statuses = get_commit_status(repo_owner, repo_name, commit_sha)

    if len(statuses) == 0:
        return 'pending'
    
    """ if any item is pending, the whole status of pending """
    if 'pending' in statuses:
        return 'pending'

    """ if any item is failure, the whole status of failure """
    if 'failure' in statuses or 'error' in statuses:
        return 'failure'
    
    return 'success'

def send_ci_update_message(pr, status, ci_updated_at):
    # we can not notify when we don't know the slack id
    if pr.owner.slack_id is None:
        return

    pr_id = pr.number
    pr_title = pr.title
    pr_url = pr.html_url
    pull_str = get_pull_request_string(pr_url, pr_id, pr_title)
    message = 'Your PR {0} has CI update, check it out'.format(pull_str)

    attachment_meta_dict = {
        'success': {
            'text': 'CI checks succeed!{0}'.format(NAMES_EMOJI['passenger_ship']),
            'color': '#22BE57',
        },
        'failure': {
            'color': '#CF1833',
            'text': 'Sorry, CI checks failed for your PR {0}'.format(NAMES_EMOJI['upside_down_face']),
        } ,
    }
    attachment_meta = attachment_meta_dict[status]

    attachment_title = 'CI update for #{0}: {1}'.format(pr_id, pr_title)

    attachments = [{
        'fallback': attachment_title,
        'title': attachment_title,
        'title_link': pr_url,
        'color': attachment_meta['color'],
        'author_link': pr_url,
        'text': attachment_meta['text'],
        'footer': 'Pull Reminder',
        'ts': timestamp_from_utc_string(ci_updated_at),
        'mrkdwn_in': ['text'],
        'fields':[
            { 'title': 'State', 'value': status },
        ],
    }]

    logger.info('send an CI status notification to %s', pr.owner.slack_id)
    send_to_slack_user(message, '@' + pr.owner.slack_id, attachments)
