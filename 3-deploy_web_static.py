#!/usr/bin/python3
"""
Fabric script based on the file 2-do_deploy_web_static.py that creates and
distributes an archive to the web servers

execute: fab -f 3-deploy_web_static.py deploy -i ~/.ssh/id_rsa -u ubuntu
"""

from fabric.api import env, local, put, run
from datetime import datetime
from os.path import exists, isdir
import os


env.hosts = ['34.239.254.111', '35.153.66.238']


def do_pack():
    """
    Creates a compressed archive of the web_static directory
    """
    now = datetime.now().strftime("%Y%m%d%H%M%S")
    local("mkdir -p versions")
    result = local("tar -czvf versions/web_static_{}.tgz web_static".
                   format(now))
    if result.failed:
        print("Error: Failed to create the archive.")
        return None
    elif result.return_code != 0:
        print("Error: Non-zero return code from tar command.")
        return None
    else:
        archive_path = "versions/web_static_{}.tgz".format(now)
        print("web_static packed: {} -> {} Bytes".format(archive_path, os.path.
              getsize(archive_path)))
        return archive_path


def do_deploy(archive_path):
    """distributes an archive to the web servers"""
    if exists(archive_path) is False:
        return False

    try:
        file_name = archive_path.split("/")[-1]
        no_ext = file_name.split(".")[0]
        path = "/data/web_static/releases/"
        put(archive_path, '/tmp/')
        run(f'mkdir -p {path}{no_ext}/')
        run(f'tar -xzf /tmp/{file_name} -C {path}{no_ext}/')
        run(f'rm /tmp/{file_name}')
        run(f'mv {path}{no_ext}/web_static/* {path}{no_ext}/')
        run(f'rm -rf {path}{no_ext}/web_static')
        run(f'rm -rf /data/web_static/current')
        run(f'ln -s {path}{no_ext}/ /data/web_static/current')
        return True
    except FileNotFoundError:
        print("File not found.")
        return False


def deploy():
    """creates and distributes an archive to the web servers"""
    archive_path = do_pack()
    if archive_path is None:
        return False
    return do_deploy(archive_path)
