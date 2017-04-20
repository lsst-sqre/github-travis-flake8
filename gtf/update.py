#!/usr/bin/env python
import os.path
import shutil

from codekit import codetools
import git

from base import get_parser, get_repos, REPOS_DIR

def add_file(git_repo, source, dest, file_name):
    if not os.path.exists(dest):
        shutil.copy(source, dest)
        git_repo.index.add([file_name])
        return True

def update(git_repo, branch_name, clone_dir):
    """Add setup.cfg and .travis.yml if they don't exist."""
    changed = False
    source_setup_cfg = os.path.join('..', 'files', 'setup.cfg')
    source_travis_yml = os.path.join('..', 'files', '.travis.yml')
    dest_setup_cfg = os.path.join(clone_dir, 'setup.cfg')
    dest_travis_yml = os.path.join(clone_dir, '.travis.yml')
    ticket_branch = git_repo.create_head(branch_name)
    ticket_branch.checkout()
    changed = add_file(git_repo, source_setup_cfg, dest_setup_cfg, 'setup.cfg')
    changed = add_file(git_repo, source_travis_yml, dest_travis_yml,
                       '.travis.yml') or changed
    return changed


def pull_request(github_repo, branch_name):
    return github_repo.create_pull(
        title='[DM-9847] Add TravisCI and Flake8 configuration.',
        base='master',
        head=branch_name,
        body='Add setup.cfg and .travis.yml to support TravisCI and'
        ' Flake8 linting.')


def clone(github_repo, branch_name='master', task=None, pull=False,
          verbose=False):
    clone_dir = os.path.join(REPOS_DIR, github_repo.name)
    if not os.path.exists(clone_dir):
        git_repo = git.Repo.clone_from(github_repo.clone_url,
                                       clone_dir)
    else:
        git_repo = git.Repo(clone_dir)
    if verbose:
        print('Cloned [{0}/{1}]'.format(github_repo.owner.login,
                                      github_repo.name))
    changed = update(git_repo, branch_name, clone_dir)
    if changed:
        commit_message = '[DM-9847] Add TravisCI and Flake8 configuration.'
        git_repo.index.commit(commit_message)
        if verbose:
            print('Add commit: {0}'.format(commit_message))
        remote = git_repo.remote(name='origin')
        refspec = 'refs/heads/{br}:refs/heads/{br}'.format(br=branch_name)
        # Do I need config writer bit?
        remote.push(refspec=refspec, force=True)
        print(remote)
        print(git_repo.working_dir)
    if pull:
        pr = pull_request(github_repo, branch_name)
        if verbose:
            print('Create pull request {0}'.format(pr))


def main():
    parser = get_parser('Create a branch and update GitHub repository(ies).')
    parser.add_argument('-b', '--branch_name', required=True,
                        help='The branch name to use for clone and'
                        ' pull requests.')
    # parser.add_argument('-c', '--clone', action='store_true',
    #                     help='Add default setup.cfg and .travis.yml')
    parser.add_argument('-u', '--pull', action='store_true',
                        help='Create a GitHub pull request if there are'
                        ' clone changes.')
    args = parser.parse_args()
    repos = get_repos(args)
    for r in repos:
        clone(r, args.branch_name, 'DM-9847', args.pull, args.verbose)


if __name__ == '__main__':
    main()
