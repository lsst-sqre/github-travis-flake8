"""
Command Line Interface to clone some repositories.
"""
import argparse

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
