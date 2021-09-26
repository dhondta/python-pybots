#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Bot client dedicated to Git repository recovery.

"""
import os
import re
import zlib
from subprocess import check_output, Popen, PIPE
from tinyscript.helpers import b, ensure_str, execute, u

from ...core.protocols.http import HTTPBot


__all__ = ["GitRecoveryBot"]

FOLDERS = [
    "branches",
    "hooks",
    "info",
    "logs",
    "logs/refs",
    "logs/refs/heads",
    "logs/refs/remotes",
    "logs/refs/remotes/origin",
    "objects",
    "refs",
    "refs/heads",
    "refs/remotes",
    "refs/remotes/origin",
]
KNOWN_FILES = [
    "HEAD",
    "FETCH_HEAD",
    "ORIG_HEAD",
    "config",
    "description",
    "COMMIT_EDITMSG",
    "index",
    "packed-refs",
    "smartgit.config",
    "hooks/applypatch-msg",
    "hooks/commit-msg",
    "hooks/update",
    "hooks/post-update",
    "hooks/pre-applypatch",
    "hooks/pre-commit",
    "hooks/prepare-commit-msg",
    "hooks/pre-push",
    "hooks/pre-rebase",
    "info/exclude",
    "logs/HEAD",
    "logs/refs/heads/{{branch}}",
    "logs/refs/remotes/origin/HEAD",
    "logs/refs/remotes/origin/{{branch}}",
    "refs/heads/{{branch}}",
    "refs/remotes/origin/HEAD",
    "refs/remotes/origin/{{branch}}",
]


class GitRecoveryBot(HTTPBot):
    """
    GitRecoveryBot class for recovering a Git repository from a given URL.
    
    Example:
    
        >>> from pybots import GitRecoveryBot
        >>> with GitRecoveryBot("http://www.example.com/git/repo/") as bot:
            bot.checkout()
    """
    def __init__(self, *args, **kwargs):
        super(GitRecoveryBot, self).__init__(*args, **kwargs)
        self.commits = []
        self.files = []
        # check if git is installed
        try:
            execute("git --version")
            self.__git_installed = True
        except OSError:
            self.__git_installed = False
            self.logger.warning("Git not installed, some functions won't work")
        # prepare the folder structure
        if not os.path.exists(".git"):
            os.makedirs(".git")
        for f in FOLDERS:
            f = os.path.join(".git", f)
            if not os.path.exists(f):
                os.makedirs(f)
    
    def __checkout_branch(self, branch):
        """
        Checkout the given branch.
        
        :param branch: branch name
        """
        cmd = "git checkout {}".format(branch)
        self.logger.debug("Trying '{}'".format(cmd))
        out, err = execute(cmd)
        if b("error:") in err or b("fatal:") in err:
            self.__extract_commits(out, err)
            self.__last_cmd = cmd
            self.__checkout_branch(branch)
        else:
            for l in out.split(b('\n')):
                if len(l) > 0 and not l.startswith(b("Already on")):
                    fp = ensure_str(l).split('\t')[-1]
                    if fp not in self.files:
                        self.files.append(fp)
            for fp in self.files:
                self.__recover_source(self.__get_revision(fp), fp)
            self.logger.info("Checkout:\n" + ensure_str(out))

    
    def __extract_commits(self, *outputs):
        """
        Extract commits from a given output.

        :param outputs: output texts, e.g. the content of .git/logs/HEAD
        :return:        list of found hashes
        """
        hashes = []
        for output in outputs:
            for sha1 in re.findall(r"[0-9a-f]{40}", str(output), re.I):
                if sha1 not in self.commits:
                    self.__fetch_file(sha1, True)
                hashes.append(sha1)
        return hashes
    
    def __fetch_file(self, fp, commit=False, skip=True):
        """
        Fetch .git files.

        :param fp:     file path (without prepended ".git")
        :param commit: whether the file is a commit or not
        :param skip:   whether the file should be re-downloaded
        """
        if commit:
            if fp.strip("0") == "":  # occurs when reading a list of commit ;
                return               # the first hash has only zeros
            sha1 = fp
            fp = "objects/{}/{}".format(fp[:2], fp[2:])
        dest = os.path.join(".git/", fp)
        if skip and os.path.exists(dest):
            self.logger.debug("{} skipped".format(fp))
            return
        if commit:
            self.logger.debug("Fetching commit {}".format(sha1))
        else:
            self.logger.debug("Fetching file {}".format(fp))
        # check if the file exists with a HEAD request
        reqp = self._parsed.path + "/.git/" + fp
        self.head(reqp)
        if self.response.status_code == 200:
            if commit:
                self.commits.append(sha1)
                try:
                    os.makedirs(os.path.dirname(dest))
                except OSError:
                    pass
            # if the file exists, retrieve it
            self.retrieve(reqp, dest)
            self.logger.debug(fp)
            if commit:
                try:  # decompress and read the downloaded commit object
                    with open(dest, 'rb') as f:
                        self.__extract_commits(zlib.decompress(f.read()))
                except:
                    self.logger.warning("Parsing '{}' failed".format(fp))
        elif self.response.status_code == 403:
            self.logger.warning(fp)
    
    def __fetch_commits(self, branch):
        """
        Fetching commits from known files.
        """
        try:
            with open(".git/logs/HEAD") as f:
                self.__extract_commits(f.read())
        except IOError:
            self.logger.warning("Could not extract commits from logs/HEAD")
        try:
            with open(".git/refs/heads/%s" % branch) as f:
                self.__fetch_file(f.read().strip(), True)
        except IOError:
            self.logger.warning("Could not extract commits from refs/heads/%s" % branch)
    
    def __fetch_files(self, branch):
        """
        Fetch known files.
        """
        for fp in KNOWN_FILES:
            fp = fp.replace("{{branch}}", branch)
            if not os.path.exists(os.path.join(".git/", fp)):
                self.__fetch_file(fp)
    
    def __get_revision(self, fp):
        """
        Git file revision list retrieval function. This uses file's revision
         list to download missing commits.
        
        :param fp: file path
        """
        # find the last commit that altered the given file
        cmd = 'git rev-list -n 1 HEAD -- {}'.format(fp)
        self.logger.debug("Executing '{}'".format(cmd))
        out, err = execute(cmd)
        try:
            return self.__extract_commits(out)[-1]
        except IndexError:
            return
    
    def __recover_source(self, sha1, fp):
        """
        Git file recovery function. This uses file's revision list and then
         checks it out in order to get the last version of the file.

        :param fp: file path
        """
        if not self.__git_installed:
            return
        cmd = 'git checkout {} -- {}'.format(sha1, fp)
        self.logger.debug("Executing '{}'".format(cmd))
        out, err = execute(cmd)
        if b("unable to read") in err:
            self.__extract_commits(err)
            self.__recover_source(sha1, fp)
        else:
            self.logger.info("Successfully recovered {}".format(fp))
    
    def __valid_branch(self, branch):
        """
        Validate if a given branch name exists.
        
        :param branch: branch name
        """
        self.head(self._parsed.path + "/.git/refs/heads/" + branch)
        return self.response.status_code == 200
    
    def checkout(self, branch="main"):
        """
        Git respository file enumeration function.

        :param branch: repository branch to be enumerated
        """
        if not self.__git_installed or not self.__valid_branch(branch):
            return
        # retrieve existing .git files and commits
        self.__fetch_files(branch)
        self.__fetch_commits(branch)
        # now try to checkout and recursively download files
        self.__checkout_branch(branch)

