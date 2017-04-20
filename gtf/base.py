#!/usr/bin/env python
"""
Command Line Interface to clone some repositories.
"""
import argparse
import os.path
import shutil

import git
from codekit import codetools


REPOS_DIR = '../repos'
gh = None


def get_gh():
    global gh
    if not gh:
        gh = codetools.login_github()
    return gh


def token():
    gh = get_gh()
    return gh.session.headers['Authorization'].split('token ')[1]


def add_file(git_repo, source, dest, file_name):
    if not os.path.exists(dest):
        shutil.copy(source, dest)
        git_repo.index.add([file_name])
        print('Add {0}'.format(file_name))
        return True

def update(git_repo, branch_name, clone_dir):
    """Add setup.cfg and .travis.yml if they don't exist."""
    changed = False
    source_setup_cfg = os.path.join('.', 'files', 'setup.cfg')
    source_travis_yml = os.path.join('.', 'files', '.travis.yml')
    dest_setup_cfg = os.path.join(clone_dir, 'setup.cfg')
    dest_travis_yml = os.path.join(clone_dir, '.travis.yml')
    ticket_branch = git_repo.create_head(branch_name)
    ticket_branch.checkout()
    changed = add_file(git_repo, source_setup_cfg, dest_setup_cfg, 'setup.cfg')
    changed = add_file(git_repo, source_travis_yml, dest_travis_yml, '.travis.yml') \
              or changed
    print("changed = " + str(changed))
    return changed


def pull_request(github_repo, branch_name):
    return github_repo.create_pull(
        title='[DM-9847] Add TravisCI and Flake8 configuration.',
        base='master',
        head=branch_name,
        body='Add setup.cfg and .travis.yml to support TravisCI and'
        ' Flake8 linting.')


def clone(github_repo, branch_name='master', pull=False):
    clone_dir = os.path.join(REPOS_DIR, github_repo.name)
    if not os.path.exists(clone_dir):
        git_repo = git.Repo.clone_from(github_repo.clone_url,
                                       clone_dir)
    else:
        git_repo = git.Repo(clone_dir)
    print('Cloned {0}/{1}'.format(github_repo.owner.login,
                                  github_repo.name))
    changed = update(git_repo, branch_name, clone_dir)
    if changed:
        commit_message = '[DM-9847] Add TravisCI and Flake8 configuration.'
        git_repo.index.commit(commit_message)
        print('Add commit: {0}'.format(commit_message))
        remote = git_repo.remote(name='origin')
        refspec = 'refs/heads/{br}:refs/heads/{br}'.format(br=branch_name)
        # Do I need config writer bit?
        remote.push(refspec=refspec, force=True)
        print(remote)
        print(git_repo.working_dir)
    if pull:
        pr = pull_request(github_repo, branch_name)
        print('Create pull request {0}'.format(pr))


def travisci(github_repo):
    codetools.enable_travisci(github_repo, token())


def protect(github_repo, branch_name='master'):
    branch = github_repo.branch(branch_name)
    if branch.protected:
        print('{0}/{1} is already protected.'.format(
            github_repo.owner.login, github_repo.name))
    else:
        codetools.protect(github_repo, branch_name)


def get_repos(args):
    gh = get_gh()
    repos = []
    if args.repo:
        repos.append(gh.repository(args.owner, args.repo))
    if args.repos:
        for repo_name in repos:
            repos.append(gh.repository(args.owner, repo_name))
    if args.file:
        for repo_name in open(args.file).read().split('\n'):
            if repo_name:
                repos.append(gh.repository(args.owner, repo_name))
    if not repos:
        Exception('A repository argument is required.')
    return repos


def get_parser(description):
    parser = argparse.ArgumentParser(
        description=description)
    parser.add_argument('-f', '--file',
                        help='The file with a line delimited list of'
                        ' repository names.')
    parser.add_argument('-o', '--owner',
                        help='The GitHub owner or organization of the'
                        ' repository(ies).')
    parser.add_argument('-r', '--repo',
                        help='The GitHub repository to apply to apply'
                        ' changes to.')
    parser.add_argument('-s', '--repos', nargs='+',
                        help='GitHub repositories to apply changes to.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Display additional information.')
    return parser


def main():
    parser = get_parser('Add TravisCI, protection and flake8 support.')
    args = parser.parse_args()
    if args.file:
        repo_urls = open(args.file).read()
    print(args)
    global gh
    gh = codetools.login_github()
    repos = get_repos(args)
    for r in repos:
        if args.travisci:
            travisci(r)
        if args.clone:
            if not args.branch_name:
                raise Exception('A branch_name argument is required when'
                                ' using clone.')
            clone(r, args.branch_name, args.pull)
        if args.protect:
            protect(r)


if __name__ == "__main__":
    main()
