
from github3 import login
from config import GITHUB_API_TOKEN
from logger import pp, logger

gh_client = login(token=GITHUB_API_TOKEN)

def get_pull_request(owner, repository, pull_request_number):
    return gh_client.pull_request(owner, repository, pull_request_number)

def get_review_comments(owner, repository, pull_request_number, review_id):
    pull_request = get_pull_request(owner, repository, pull_request_number)
    review_comments = []

    for review_comment in pull_request.review_comments():
        if review_comment.pull_request_review_id == review_id:
            review_comments.append(review_comment)

    return review_comments 

