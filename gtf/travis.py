#!/usr/bin/env python
from codekit import codetools

from base import get_parser, get_repos, token


def travis(github_repo, verbose=False):
    success = codetools.enable_travisci(github_repo, token())
    if verbose:
        print('Travis CI webhook enabled for [{0}/{1}].'.format(
            github_repo.owner.login, github_repo.name))
    return success


def main():
    parser = get_parser('Enable TravisCI webhook for repository(ies).')
    args = parser.parse_args()
    repos = get_repos(args)
    for r in repos:
        travis(r, args.verbose)


if __name__ == '__main__':
    main()
