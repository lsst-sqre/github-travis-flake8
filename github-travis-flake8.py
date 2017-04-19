#!/usr/bin/env python
"""
Command Line Interface to clone some repositories.
"""
import argparse
import os.path
import shutil

import git
from codekit import codetools


REPOS_DIR = './repos'
gh = None


def token():
    if gh:
        return gh.session.headers['Authorization'].split('token ')[1]


def update(github_repo, git_repo, branch_name, clone_dir):
    changed = False
    dest_setup_cfg = os.path.join(clone_dir, 'files', 'setup.cfg')
    dest_travis_yml = os.path.join(clone_dir, 'files', '.travis.yml')
    ticket_branch = git_repo.create_head(branch_name)
    ticket_branch.checkout()
    if not os.path.exists(dest_travis_yml):
        source_travis_yml = os.path.join('.', '.travis.yml')
        shutil.copy(source_travis_yml, dest_travis_yml)
        changed = True
    else:
        print('.travis.yml already exists in {0}/{1}'.format(
            github_repo.owner.login, github_repo.name))
    if not os.path.exists(dest_setup_cfg):
        source_setup_cfg = os.path.join('.', 'setup.cfg')
        shutil.copy(source_setup_cfg, dest_setup_cfg)
        changed = True
    else:
        print('setup.cfg already exists in {0}/{1}'.format(
            github_repo.owner.login, github_repo.name))
    return changed


def clone(github_repo, branch_name='master'):
    clone_dir = os.path.join(REPOS_DIR, github_repo.name)
    if not os.path.exists(clone_dir):
        git_repo = git.Repo.clone_from(github_repo.clone_url,
                                       clone_dir)
    else:
        git_repo = git.Repo(clone_dir)
    print('Cloned {0}/{1}'.format(github_repo.owner.login,
                                  github_repo.name))
    changed = update(github_repo, git_repo, branch_name, clone_dir)
    if changed and git_repo.is_dirty():
        git_repo.index.commit('[DM-9847] Add setup.cfg.')
        remote = git_repo.remote(name='origin')
        refspec = 'refs/heads/{br}:refs/heads/{br}'.format(br=branch_name)
        # Do I need config writer bit?
        remote.push(refspec=refspec)
    else:
        print('setup.cfg already exist in {0}/{1}'.format(
            github_repo.owner.login, github_repo.name))


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


def main():
    parser = argparse.ArgumentParser(
        description='Add TravisCI, protection and flake8 support.')
    parser.add_argument('-b', '--branch_name',
                        help='The branch name to use for clone and'
                        ' pull requests.')
    parser.add_argument('-c', '--clone', action='store_true',
                        help='Add default setup.cfg and .travis.yml')
    parser.add_argument('-f', '--file',
                        help='The file with a line delimited list of'
                        ' repository names.')
    parser.add_argument('-o', '--owner',
                        help='The GitHub owner or organization of the'
                        ' repository(ies).')
    parser.add_argument('-p', '--protect', action='store_true',
                        help='Add default branch protection')
    parser.add_argument('-r', '--repo',
                        help='The GitHub repository to apply to apply'
                        ' changes to.')
    parser.add_argument('-s', '--repos', nargs='+',
                        help='GitHub repositories to apply changes to.')
    parser.add_argument('-t', '--travisci', action='store_true',
                        help='Enable TravisCI webhook for repository(ies).')
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
            clone(r, args.branch_name)
        if args.protect:
            protect(r)


if __name__ == "__main__":
    main()
