
import yaml
from os.path import join, dirname
from logger import pp

stream = file(join(dirname(__file__), '..', 'config/user-map.yml'), 'r')
github_slack_ids = yaml.safe_load(stream)

class User(object):
     def __init__(self, github_id):
         pp.pprint(github_id)
         self.github_id = github_id
         self.slack_id = github_slack_ids.get(github_id, None)
