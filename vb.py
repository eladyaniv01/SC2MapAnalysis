import re
import subprocess

__author__ = "Elad Yaniv"
import click


@click.group(help='Commands marked with (LIVE) require SC launch and windows environment.')
def vb():
    pass


def parse_setup():
    with open("setup.py", 'r') as f:
        setup_parsed = f.read()
    return setup_parsed


def update_setup(new_version):
    setup_parsed = parse_setup()
    old_version_regex = r"(\d*[.]\d*[.]\d*)"
    old_version = re.findall(old_version_regex, setup_parsed)[0]
    setup_updated = setup_parsed.replace(old_version, new_version)
    with open('setup.py', 'w') as f:
        f.write(setup_updated)

    import os
    curdir = os.getcwd()
    click.echo(click.style(curdir + '\\standard-version', fg='blue'))
    subprocess.check_call('git fetch', shell=True)
    subprocess.check_call('git pull', shell=True)
    subprocess.check_call(f'standard-version --release-as {new_version}', shell=True)
    subprocess.check_call('git push --follow-tags origin', shell=True)


@vb.command(help='print setup.py')
def printsetup():
    setup_parsed = parse_setup()
    click.echo(click.style(setup_parsed, fg='blue'))


@vb.command(help='Get current version')
def gv():
    import re
    setup_parsed = parse_setup()
    old_version_regex = r"(\d*[.]\d*[.]\d*)"
    old_version = re.findall(old_version_regex, setup_parsed)[0]
    click.echo(click.style(old_version, fg='green'))


@vb.command(help='Bump Minor')
def bumpminor():
    setup_parsed = parse_setup()
    old_version_regex = r"(\d*[.]\d*[.]\d*)"
    old_version = re.findall(old_version_regex, setup_parsed)[0]
    minor = re.findall(r"([.]\d*)", old_version)[-1]
    minor = minor.replace('.', '')
    click.echo(f"Current Version: " + click.style(old_version, fg='green'))
    click.echo(f"Minor Found: " + click.style(minor, fg='green'))
    bump = str(int(minor) + 1)
    click.echo(f"Bumping to : " + click.style(bump, fg='blue'))
    new_version = str(old_version).replace(minor, bump)
    click.echo(f"Updated Version: " + click.style(new_version, fg='red'))
    update_setup(new_version)


if __name__ == '__main__':
    vb(prog_name='python -m vb')
