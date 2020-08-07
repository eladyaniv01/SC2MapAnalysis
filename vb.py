import re
import subprocess

import click


@click.group(help='Commands marked with (LIVE) require SC launch and windows environment.')
def vb():
    pass


__author__ = "Elad Yaniv"


def parse_setup():
    with open("setup.py", 'r') as f:
        setup_parsed = f.read()
    return setup_parsed


def update_setup(new_version):
    setup_parsed = parse_setup()
    old_version_regex = r"(\d*[.]\d*[.]\d*)"
    # result = re.sub(old_version_regex, new_version, setup_parsed, 0, re.MULTILINE)
    old_version = re.findall(old_version_regex, setup_parsed)[0]
    setup_updated = setup_parsed.replace(old_version, new_version)
    with open('setup.py', 'w') as f:
        f.write(setup_updated)
    # subprocess.call(['standard-version', '--update'])
    import os
    curdir = os.getcwd()
    click.echo(click.style(curdir + '\\standard-version', fg='blue'))
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
    # result = re.sub(old_version_regex, new_version, setup_parsed, 0, re.MULTILINE)
    old_version = re.findall(old_version_regex, setup_parsed)[0]
    click.echo(click.style(old_version, fg='green'))


@vb.command(help='Bump Minor')
def bumpminor():
    setup_parsed = parse_setup()
    old_version_regex = r"(\d*[.]\d*[.]\d*)"
    # result = re.sub(old_version_regex, new_version, setup_parsed, 0, re.MULTILINE)
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


# @vb.command(help='(LIVE) Make data snapshot for map, which can be used in mock objects later')
# def snapshot():
#     from .tests.snapshot import save_map_from_bwapi
#     save_map_from_bwapi()
#
#
# @vb.command(help='(LIVE) Check map buildtiles')
# def buildable_test():
#     from .tests.buildable import detect_bads
#     detect_bads()
#
#
# @vb.command(help='Make better output for buildable_test result')
# def buildable_refine():
#     from .mapanalyzer.tests.buildable import refine
#     refine('output.txt')
#
#
# @vb.command(help='Find & render best places for bases using map snapshot')
# @click.argument('maphash')
# def findbases(maphash):
#     from .resources import BaseFinder
#     from .metrics import MapMetrics
#     from .tests.mocks import PybroodMock
#     from .tests.render import render_map
#
#     pybrood = PybroodMock(maphash)
#     mm = MapMetrics.from_pybrood(pybrood)
#     valid_bases = BaseFinder(pybrood.game, mm)()
#     render_map(pybrood.game, mm, valid_bases)
#
#
# @vb.command(help='Find & render v2')
# @click.argument('maphash')
# def findbases2(maphash):
#     from .tests.floods import v2
#     v2(maphash)
#
#
# @vb.command(help='Node merging algorithm')
# @click.argument('maphash')
# def nodemerge(maphash):
#     from .tests.floods import node_merge
#     node_merge(maphash)
#
#
# @vb.command(help='Find choke points')
# @click.argument('maphash')
# def chokes(maphash):
#     from .tests.floods import chokes
#     chokes(maphash)


if __name__ == '__main__':
    vb(prog_name='python -m vb')

# new_version = ''  # new version
#
# old_version_regex = r"(\"\d*[.]\d*[.]\d*\")"
# result = re.sub(old_version_regex, new_version, setup_parsed, 0, re.MULTILINE)
# click.echo("{}, {}".format(greeting, name))
#
# @main.command()
# @click.argument('query')
# def search(query):
#     """This search and return results corresponding to the given query from Google Books"""
#     url_format = 'https://www.googleapis.com/books/v1/volumes'
#     query = "+".join(query.split())
#
#     query_params = {
#         'q': query
#     }
#
#     response = requests.get(url_format, params=query_params)
#
#     click.echo(response.json()['items'])
#
# @main.command()
# @click.argument('id')
# def get(id):
#     """This return a particular book from the given id on Google Books"""
#     url_format = 'https://www.googleapis.com/books/v1/volumes/{}'
#     click.echo(id)
#
#     response = requests.get(url_format.format(id))
#
#     click.echo(response.json())
#
#
# if __name__ == "__main__":
#     main()
# import re
#
# import click
#
#
#
