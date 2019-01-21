pr-reminder
===================

    Posts slack notifications for pull request events, include review_requested,
    review submitted etc.


Installation
------------

.. code:: bash

    # for development
    $ virtualenv --no-site-packages env
    $ source env/bin/activate
    $ pip install -r requirements
    $ pip install -e .

Usage
-----

pr-reminder is configured using environment variables:

Required
~~~~~~~~

-  ``SLACK_API_TOKEN``
-  ``GITHUB_API_TOKEN``
-  ``ORGANIZATION``: The GitHub organization you want pull request
   reminders for.

Optional
~~~~~~~~

-  ``IGNORE_WORDS``: A comma-separated list of words that will cause a pull request to be ignored.

-  ``IGNORE_LABELS``: A comma-separated list of labels that will cause a pull request to be ignored.

-  ``REPOSITORIES``: A comma-separated list of repository names to check, where all other repositories in the organization are ignored. All repositories are checked by default.

-  ``USERNAMES``: A comma-separated list of GitHub usernames to filter pull requests by, where all other users are ignored. All users in the organization are included by default.

-  ``SLACK_CHANNEL``: The Slack channel you want the reminders to be posted in, defaults to #general.

Example
~~~~~~~

.. code:: bash

    $ ORGANIZATION="orgname" REPOSITORIES='repo_name' SLACK_API_TOKEN="token" GITHUB_API_TOKEN="token" IGNORE_LABELS="wip,tbd" pr-reminder
