import git
from xml.dom import minidom

git_base_url = "https://android.googlesource.com/platform/"

def remote_exists(url):
    g = git.cmd.Git()
    try:
        refs = g.ls_remote(url).split('\n')
        if len(refs) > 0:
            return True
        else:
            return False
    except git.GitCommandError:
        return False

manifest_path = input("Manifest of repos to update: ")
manifest = minidom.parse(manifest_path)
repos = manifest.getElementsByTagName('project')
rom_path = input("Path of ROM's root folder: ")
if rom_path[-1] == "/":
    rom_path = rom_path[:-1]
repos_remote_to_merge = input("Name of remote in manifest of the repos to update: ")
repo_branch_name = input("Branch name of repos to update: ")
tag_to_merge = input("Tag to merge: ")

for repo in repos:
    if repo.attributes['remote'].value != repos_remote_to_merge:
        continue
    # Actual location of repo's folder
    repo_folder_path = rom_path + "/" + repo.attributes['path'].value
    # Path of repo defined in manifest
    repo_path = repo.attributes['path'].value
    print("")
    print("Working on " + repo_path)
    repo_url = git_base_url + repo_path
    repo_remote_exists = remote_exists(repo_url)
    if repo_remote_exists:
        print("Repo exists on " + git_base_url)
        repo = git.Repo(repo_folder_path)
        if repo.is_dirty():
            print("Unsaved changes detected, ignoring")
            continue
        elif repo.bare:
            print("Path is not repo, ignoring")
            continue
        if repo.head.is_detached or (repo.active_branch.name != repo_branch_name):
            if (repo_branch_name in repo.heads):
                repo.git.branch('-D', repo_branch_name)
            repo.git.checkout('HEAD', b=repo_branch_name)
        repo.git.fetch(repo_url, tag_to_merge)
        repo.git.merge("FETCH_HEAD", repo_branch_name)
        repo.git.push(repos_remote_to_merge, repo_branch_name)
    else:
        print("Repo doesn't exist on " + git_base_url)
