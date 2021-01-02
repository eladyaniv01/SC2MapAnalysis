import os
import re
import shutil
import subprocess
from pathlib import Path

__author__ = "Elad Yaniv"
import click


def recursive_overwrite(src, dest, ignore=None):
    if os.path.isdir(src):
        if not os.path.isdir(dest):
            os.makedirs(dest)
        files = os.listdir(src)
        if ignore is not None:
            ignored = ignore(src, files)
        else:
            ignored = set()
        for f in files:
            if f not in ignored:
                recursive_overwrite(os.path.join(src, f),
                                    os.path.join(dest, f),
                                    ignore)
    else:
        shutil.copyfile(src, dest)


@click.group(help='Commands marked with (LIVE) require SC launch and windows environment.')
def vb():
    pass

def update_readme_to_sphinx():
    return
    import re
    with open(".nojekyll", "w") as f:
        f.close()
    with open("docs/.nojekyll", "w") as f:
        f.close()
    regex = r"([#]\s)([A-Z]\w+)(\s?\n)"
    subst = "\\2\\n---------------\\n"
    with open("README.md", 'r') as f:
        r_parsed = f.read()
    title = "# QuickWalkThrough\n============"
    r_parsed = r_parsed.replace("# SC2MapAnalysis", title)
    r_parsed = r_parsed.replace('=', '-')
    r_result = re.sub(regex, subst, r_parsed, 0, re.MULTILINE)
    with open("README.md", 'w') as f:
        f.write(r_result)

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
    subprocess.check_call('git add setup.py', shell=True)
    subprocess.check_call('git commit -m "bump setup.py"', shell=True)
    subprocess.check_call(f'standard-version --release-as {new_version}', shell=True)
    # subprocess.check_call('git push --follow-tags origin', shell=True)


@vb.command(help='sphinx make for gh pages')
def makedocs():
    # click.echo(click.style("Updating README.MD", fg='blue'))
    # update_readme_to_sphinx()
    p = Path()
    path = p.joinpath('docs').absolute()
    click.echo(click.style(f"calling {path}//make github", fg='green'))
    subprocess.check_call(f'{path}//make github', shell=True)
    click.echo(click.style("Copying Folder", fg='blue'))
    fp = os.path.join(os.getcwd(), 'docs', 'docs', 'BUILD', 'html')
    tp = os.path.join(os.getcwd(), 'docs')
    recursive_overwrite(src=fp, dest=tp)
    pat = os.path.join(os.getcwd(), 'docs', '_sources')
    count = 0
    for root, dir, files in os.walk(pat):
        for f in files:
            if '.rst.' in f:
                newname = f.replace('.rst', '')
                try:
                    os.rename(f, newname)
                except:
                    count += 1
    click.echo(click.style(f"Count {count}", fg='blue'))

@vb.command(help='add, commit , push')
def pushdocs():
    # click.echo(click.style("Updating README.MD", fg='blue'))
    # update_readme_to_sphinx()

    subprocess.check_call('git add docs --all -f', shell=True)
    subprocess.check_call('git commit -m \"docs update\" ', shell=True)
    subprocess.check_call('git push', shell=True)

@vb.command(help='print setup.py')
def printsetup():
    setup_parsed = parse_setup()
    click.echo(click.style(setup_parsed, fg='blue'))


@vb.command(help='MonkeyType apply on list-modules')
@click.option('--apply/--no-apply', default=False)
def mt(apply):
    click.echo(click.style("This could take a few seconds", fg='blue'))
    encoded_modules = subprocess.check_output("monkeytype list-modules", shell=True)
    list_modules = encoded_modules.decode().split('\r\n')
    to_exclude = {'mocksetup', 'sc2pathlibp'}
    if apply:
        for m in list_modules:
            if [x for x in to_exclude if x in m] == []:
                click.echo(click.style(f"Applying on {m}", fg='green'))
                subprocess.check_call(f'monkeytype apply {m}', shell=True)




@vb.command(help='Get current version')
def gv():
    import re
    setup_parsed = parse_setup()
    old_version_regex = r"(\d*[.]\d*[.]\d*)"
    old_version = re.findall(old_version_regex, setup_parsed)[0]
    click.echo(click.style(old_version, fg='green'))
    click.echo("Running git describe")
    subprocess.check_call('git describe')


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


@vb.command(help='Custom git log command for last N days')
@click.argument('days')
def gh(days):
    click.echo(
            click.style("Showing last ", fg='blue') + click.style(days, fg='green') + click.style(" days summary",
                                                                                                  fg='blue'))
    subprocess.check_call('git fetch', shell=True)
    subprocess.check_call(f'git log --oneline --decorate --graph --all -{days}', shell=True)

if __name__ == '__main__':
    vb(prog_name='python -m vb')
