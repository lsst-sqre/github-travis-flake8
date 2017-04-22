#!/usr/bin/env python
"""
Command Line Interface to clone some repositories.
"""
from .base import get_parser, get_repos
from .travis import travis
from .protect import protect
from .update import clone


def main():
    parser = get_parser('Add TravisCI, protection and flake8 support.')
    parser.add_argument('-b', '--branch_name',
                        help='The branch name to use for clone and'
                        ' pull requests.')
    parser.add_argument('-c', '--clone', action='store_true',
                        help='Add default setup.cfg and .travis.yml')
    parser.add_argument('-p', '--protect', action='store_true',
                        help='Add default branch protection')
    parser.add_argument('-t', '--travis', action='store_true',
                        help='Enable Travis CI webhook for repository(ies).')
    parser.add_argument('-u', '--pull', action='store_true',
                        help='Create a GitHub pull request if there are'
                        ' clone changes.')
    args = parser.parse_args()
    repos = get_repos(args)
    for r in repos:
        if args.travis:
            travis(r, verbose=args.verbose)
        if args.clone:
            if not args.branch_name:
                raise Exception('A branch_name argument is required when'
                                ' using clone.')
            clone(r, args.branch_name, task='DM-9847',
                  pull=args.pull, verbose=args.verbose)
        if args.protect:
            protect(r, verbose=args.verbose)


if __name__ == "__main__":
    main()
