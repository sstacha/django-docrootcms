#!/bin/bash
# todo: turn this into a command line utility I can use during development on many sites?
# simple script to deploy code based on environment variables
#   idea: we use a branch (or none=master) to develop with; we use a tag or the branch to deploy to a server
#
# DOCROOTCMS_GIT_URL: if provided will be used to get codebase from
# DOCROOTCMS_GIT_BRANCH: if provided will be used instaed of main (branch or tag)

echo "working directory: $(pwd)"
echo "git url: $DOCROOTCMS_GIT_URL"
echo "git branch: $DOCROOTCMS_GIT_BRANCH"


# make sure our cache, data and images folders exist (they should if cloning properly but errors if not at startup)
mkdir -p cache
mkdir -p images
mkdir -p data
# NOTE: removing pull since bound directories with ssh keys don't work here even for public repos
# determine if our current directory is already attached to git remote
#if [[ -d ".git" ]]; then
#    echo "found the git directory; doing a pull!"
#    git -c http.sslVerify=false pull
#else
    if [[ -z "$DOCROOTCMS_GIT_URL" ]]; then
        echo "No env DOCROOTCMS_GIT_URL.  Skipping clone."
    else
        echo "did not find the git directory; deleting, cloning!"
        # delete the existing folders from our instance
        echo "removing existing folder contents"
        rm -rf *
        rm -rf .[!.]* ..?*
        # NOTE: since we should only be doing this on a new install we are not messing with the db
        if [[ -z "$DOCROOTCMS_GIT_BRANCH" ]]; then
            echo "cloning folder contents from $DOCROOTCMS_GIT_URL"
            # attempt to clone the contents from the git repo passed
            git -c http.sslVerify=false clone "$DOCROOTCMS_GIT_URL" .        
        else
            echo "cloning folder contents from $DOCROOTCMS_GIT_URL branch/tag [$DOCROOTCMS_GIT_BRANCH]"
            # attempt to clone the contents from the git repo passed
            git -c http.sslVerify=false clone -b $DOCROOTCMS_GIT_BRANCH --single-branch "$DOCROOTCMS_GIT_URL" .
        fi
    fi
#fi
if [[ -z "$DOCROOTCMS_OWNERSHIP" ]]; then
    echo "No env DOCROOTCMS_OWNERSHIP.  Skipping permissions."
else
    echo "setting permissions to [$DOCROOTCMS_OWNERSHIP]"
    chown -R $DOCROOTCMS_OWNERSHIP /usr/src/app/
fi
