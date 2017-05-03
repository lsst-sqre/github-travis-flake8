# sqre-gtf

[![Build Status](https://travis-ci.org/lsst-sqre/sqre-gtf.svg?branch=master)](https://travis-ci.org/lsst-sqre/sqre-gtf)

Github TravisCI and Flake8 and update automation for LSST DM SQuaRE.

## Installation

`sqre-gtf` runs on Python 2.7, 3.5 and 3.6. You can install it with

```
pip install sqre-gtf
```

This will also install dependencies: `sqre-github3.py`, `GitPython`, `sqre-pytravisci` and `sqre-codekit`.

## Use

`sqre-gtf` provides command line interfaces to use Github, TravisCI and Flake8.

* `github-protect` - Enable LSST DM's default Github branch protection.

* `github-travis` - Enable TravisCI webhook for repository(ies).

* `github-update` - Create a branch and update GitHub repository(ies).

* `github-protect-travis` - Add Github branch protection, TravisCI webhooks and flake8 support through one script.

The following is an example that adds Github branch protection, enables TravisCI then creates a commit and pull request with a .travis.yml and setup.cfg that runs flake8. This example is for [lsst.utils](https://github.com/lsst/utils).

```
github-protect --owner lsst -repo utils --branch_name master
github-travis --owner lsst --repo utils
github-update --owner lsst --repo utils --task stack -branch_name tickets/DM-5637 --commit_message "[DM-5637] Add .travis.yml and setup.cfg to run flake8." --pull --pull_message "[DM-5637] Add .travis.yml and setup.cfg to run flake8."
```

## LICENSE

See the [LICENSE file](/LICENSE).