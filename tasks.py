from fabric.api import *
import fabric.contrib.project as project
import os

# Local path configuration (can be absolute or relative to fabfile)
env.deploy_path = 'output'
env.content_path = 'content'

# Deployment
env.siteurl = 'iguananaut.net'
env.gh_account = 'iguananaut'
env.gh_repository = 'iguananaut.github.io'
env.gh_remote = 'live'
env.gh_remote_branch = 'master'
env.gh_token = os.environ.get('GH_TOKEN', '')

env.git_name = 'Erik M. Bray'
env.git_email = 'erik.m.bray+iguananaut@gmail.com'


def clean():
    if os.path.isdir(env.deploy_path):
        local('rm -rf {deploy_path}'.format(**env))
        local('mkdir {deploy_path}'.format(**env))


def build():
    if not os.path.exists(env.content_path):
        local('mkdir {content_path}'.format(**env))
    local('pelican -s pelicanconf/production.py')


def rebuild():
    clean()
    build()


def regenerate():
    local('pelican -r -s pelicanconf/production.py')


def serve():
    local('cd {deploy_path} && python -m SimpleHTTPServer'.format(**env))


def reserve():
    build()
    serve()


def preview():
    if not os.path.exists(env.content_path):
        local('mkdir {content_path}'.format(**env))
    local('pelican -s pelicanconf/development.py')


def travis_deploy():
    local('git remote add {gh_remote} '
          'https://{gh_account}:{gh_token}@github.com/{gh_account}/{gh_repository}.git'.format(**env))
    local('git config user.name {git_name!r}'.format(**env))
    local('git config user.email {git_email!r}'.format(**env))
    local('git checkout --orphan output')
    local('git rm -rf .')
    # Now add the output directory so that it won't be deleted, but
    # then clean up any files left over from the build (pyc files mainly)
    # TODO: Find a less round-about way of preparing the output branch
    local('git add {deploy_path}'.format(**env))
    local('git clean -dfx')
    local('git mv {deploy_path}/* .'.format(**env))
    local('rmdir {deploy_path}'.format(**env))
    local('touch .nojekyll')
    local('git add .nojekyll')

    # Add CNAME file for GitHub URL redirection
    local('echo {siteurl!r} >> CNAME'.format(**env))
    local('git add *')
    local('git commit -m "Generated from sources"')
    local('git push -f {gh_remote} output:{gh_remote_branch}'.format(**env))
