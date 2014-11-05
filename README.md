# github-notify

GitHub Issue Notifier

Sends an email alert based on matching a regex pattern in one of the following:

1. Issue/Pull Request Subject
1. Issue/Pull Request Body
1. Pull Request File Name
1. Issue Comments
1. Pull Request Comments
1. Pull Request Commit Messages

## Installing

1. `git clone https://github.com/sivel/github-notify.git`
1. `cd github-notify`
1. `pip install -r requirements.txt`
1. Create a `github-notify.yaml` configuration file as described below

## github-notify.yaml

This file can live at `./github-notify.yaml`, `~/.github-notify.yaml`, or `/etc/github-notify.yaml`

```yaml
---
github_client_id: 1ecad3b34f7b437db6d0
github_client_secret: 6689ba85bb024d1b97370c45f1316a16d08bba20
github_repository:
    - 'ansible/ansible'
    - 'ansible/ansible-modules-core'
    - 'ansible/ansible-modules-extras'

regex_pattern: 'rax|rackspace|openstack|nova'

mailgun_domain: example.mailgun.org
mailgun_api_key: "key-rj4-0pngm5bsbehryarfy1eg84hf0l6jf2"

email_from: no-reply@example.org
email_to:
  - person@example.org
  - robot@example.org
```

*The above values are dummy placeholder values and are not valid for use*

### GitHub credentials

You will need to [register an application](https://github.com/settings/applications/new)
to provide API access.  The Client ID and Secret will need to be populated as
shown in the above example.

## Running

It is recommended that you run `github-notify.py` via cron. The fewer pull requests and
issues that a project has the more frequently you can run the cron job. I'd recommend
starting with every 60 minutes (1 hour).
