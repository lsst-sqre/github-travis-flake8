#!/usr/bin/env python
from codekit import codetools

from base import get_parser, get_repos


def protect(github_repo, branch_name='master', verbose=False):
    branch = github_repo.branch(branch_name)
    if branch.protected:
        if verbose:
            print('[{0}/{1}] ({2}) branch is already protected.'.format(
                github_repo.owner.login, github_repo.name,
                branch_name))
    else:
        codetools.protect(github_repo, branch_name)
        if verbose:
            print('[{0}/{1}] ({2}) branch is protected.'.format(
                github_repo.owner.login, github_repo.name,
                branch_name))


if __name__ == '__main__':
    parser = get_parser('Enable TravisCI webhook for repository(ies).')
    parser.add_argument('-b', '--branch_name', default='master',
                        help='The branch name to protect. Defaults'
                        ' to master.')
    args = parser.parse_args()
    for r in get_repos(args):
        protect(r, args.branch_name, args.verbose)
