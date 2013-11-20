from fabric.api import *
import fabric.contrib.project as project
import os

# Local path configuration (can be absolute or relative to fabfile)
env.deploy_path = 'output'

# Deployment
env.gh_account = 'iguananaut'
env.gh_repository = 'iguananaut.github.io'
env.gh_remote = 'live'
env.gh_remote_branch = 'staging'
env.gh_token = os.environ.get('GH_TOKEN', '')

env.git_name = 'Erik M. Bray'
env.git_email = 'erik.m.bray+iguananaut@gmail.com'


def clean():
    if os.path.isdir(env.deploy_path):
        local('rm -rf {deploy_path}'.format(**env))
        local('mkdir {deploy_path}'.format(**env))


def build():
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
    local('pelican -s pelicanconf/development.py')


def travis_deploy():
    local('git remote add {gh_remote} '
          'https://{gh_account}:{gh_token}@github.com/{gh_account}/{gh_repository}.git')
    local('git config user.name {git_name}')
    local('git config user.email {git_email}')
    local('git checkout --orphan {gh_remote_branch}')
    local('git rm -rf .')
    local('mv {deploy_path}/* .')
    local('rmdir {deploy_path}')
    local('touch .nojekyll')
    local('git add .nojekyll')
    local('git add *')
    local('git commit -m "Generated from sourcse"')
    local('git push -f {gh_remote} {gh_remote_branch}')
