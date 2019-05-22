
from github3 import login
from config import GITHUB_API_TOKEN
from logger import pp, logger
from user import User

gh_client = login(token=GITHUB_API_TOKEN)

def get_pull_request(owner, repository, pull_request_number):
    pull_request = gh_client.pull_request(owner, repository, pull_request_number)
    owner = User(pull_request.user.login)
    setattr(pull_request, 'owner', owner)
    setattr(pull_request, 'number', pull_request_number)
    return pull_request


def get_review_comments(owner, repository, pull_request_number, review_id):
    pull_request = get_pull_request(owner, repository, pull_request_number)
    review_comments = []

    for review_comment in pull_request.review_comments():
        if review_comment.pull_request_review_id == review_id:
            review_comments.append(review_comment)

    return review_comments 

""" 
get combined status for a specific commit
see also https://developer.github.com/v3/repos/statuses/#get-the-combined-status-for-a-specific-ref
"""
def get_commit_status(owner, repository, commit_sha):
    statuses = gh_client.repository(owner, repository).commit(commit_sha).status().statuses
    return map(lambda shortStatus: shortStatus.state, statuses)
        
