#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright 2014 Matt Martz
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import re
import json
import yaml
import requests

from github import Github


def get_config():
    config_files = (
        './github-notify.yaml',
        os.path.expanduser('~/.github-notify.yaml'),
        '/etc/github-notify.yaml'
    )
    for config_file in config_files:
        try:
            with open(os.path.realpath(config_file)) as f:
                config = yaml.load(f)
        except:
            pass
        else:
            return config

    raise SystemExit('Config file not found at: %s' % ', '.join(config_files))


def alert(config, item, known, repo):
    if repo not in known:
        known[repo] = []
    known[repo].append(item.number)
    return requests.post(
        'https://api.mailgun.net/v2/%s/messages' % config['mailgun_domain'],
        auth=('api', config['mailgun_api_key']),
        data={
            'from': config['email_from'],
            'to': config['email_to'],
            'subject': config.get('email_subject', 'ALERT: New GitHub Issue'),
            'text': ('URL: %s\nTitle: %s\nUser: %s' %
                     (item.html_url, item.title, item.user.login))
        }
    )


def scan_github_issues(config):
    pattern = re.compile(config['regex_pattern'], flags=re.I)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open('github-notify.json') as f:
            known = json.load(f)
    except IOError, ValueError:
        known = {}

    g = Github(client_id=config['github_client_id'],
               client_secret=config['github_client_secret'],
               per_page=100)

    if not isinstance(config['github_repository'], list):
        repos = [config['github_repository']]
    else:
        repos = config['github_repository']

    for repo_name in repos:
        repo = g.get_repo(repo_name)

        for pull in repo.get_pulls():
            if pull.number in known.get(repo_name, []):
                continue

            try:
                if pattern.search(pull.title):
                    alert(config, pull, known, repo_name)
                    continue
            except TypeError:
                pass

            try:
                if pattern.search(pull.body):
                    alert(config, pull, known, repo_name)
                    continue
            except TypeError:
                pass

            for pull_file in pull.get_files():
                if pattern.search(pull_file.filename):
                    alert(config, pull, known, repo_name)
                    break

            for comment in pull.get_comments():
                try:
                    if pattern.search(comment.body):
                        alert(config, pull, known, repo_name)
                        break
                except TypeError:
                    pass

            for commit in pull.get_commits():
                try:
                    if pattern.search(commit.commit.message):
                        alert(config, pull, known, repo_name)
                        break
                except TypeError:
                    pass

            for comment in pull.get_issue_comments():
                try:
                    if pattern.search(comment.body):
                        alert(config, pull, known, repo_name)
                        break
                except TypeError:
                    pass

        for issue in repo.get_issues():
            if issue.number in known.get(repo_name, []):
                continue

            if issue.pull_request is not None:
                continue

            try:
                if pattern.search(issue.title):
                    alert(config, issue, known, repo_name)
                    continue
            except TypeError:
                pass

            try:
                if pattern.search(issue.body):
                    alert(config, issue, known, repo_name)
                    continue
            except TypeError:
                pass

            for comment in issue.get_comments():
                try:
                    if pattern.search(comment.body):
                        alert(config, issue, known, repo_name)
                        break
                except TypeError:
                    pass

    try:
        with open('github-notify.json', 'w+') as f:
            json.dump(known, f, indent=4, sort_keys=True)
    except (IOError, ValueError):
        pass


def main():
    scan_github_issues(get_config())


if __name__ == '__main__':
    main()
