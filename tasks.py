from invoke import task
import os

# Local path configuration (can be absolute or relative to fabfile)
deploy_path = 'output'
content_path = 'content'

# Deployment
siteurl = 'iguananaut.net'
gh_account = 'iguananaut'
gh_repository = 'iguananaut.github.io'
gh_remote = 'live'
gh_remote_branch = 'master'
gh_token = os.environ.get('GH_TOKEN', '')

git_name = 'Erik M. Bray'
git_email = 'erik.m.bray+iguananaut@gmail.com'


@task
def clean(c):
    if os.path.isdir(deploy_path):
        c.run(f'rm -rf {deploy_path}')
        c.run(f'mkdir {deploy_path}')


@task
def build(c):
    if not os.path.exists(content_path):
        c.run(f'mkdir {content_path}')
    c.run('pelican -s pelicanconf/production.py')


@task
def rebuild(c):
    clean()
    build()


@task
def regenerate(c):
    c.run('pelican -r -s pelicanconf/production.py')


@task
def serve(c, port=8000):
    c.run(f'cd {deploy_path} && python -m http.server {port}', pty=True)


@task
def reserve(c):
    build(c)
    serve(c)


@task
def preview(c):
    if not os.path.exists(content_path):
        c.run(f'mkdir {content_path}')
    c.run('pelican -s pelicanconf/development.py')


@task
def travis_deploy(c):
    c.run(f'git remote add {gh_remote} '
          f'https://{gh_account}:{gh_token}@github.com/{gh_account}/{gh_repository}.git')
    c.run(f'git config user.name {git_name!r}')
    c.run(f'git config user.email {git_email!r}')
    c.run('git checkout --orphan output')
    c.run('git rm -rf .')
    # Now add the output directory so that it won't be deleted, but
    # then clean up any files left over from the build (pyc files mainly)
    # TODO: Find a less round-about way of preparing the output branch
    c.run(f'git add {deploy_path}')
    c.run('git clean -dfx')
    c.run(f'git mv {deploy_path}/* .')
    c.run(f'rmdir {deploy_path}')
    c.run('touch .nojekyll')
    c.run('git add .nojekyll')

    # Add CNAME file for GitHub URL redirection
    c.run(f'echo {siteurl!r} >> CNAME')
    c.run('git add *')
    c.run('git commit -m "Generated from sources"')
    c.run(f'git push -f {gh_remote} output:{gh_remote_branch}')
