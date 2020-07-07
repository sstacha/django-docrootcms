#!/bin/bash
# simple script to install the app code to a mounted install directory
#   idea: we simply copy the app code to the install folder and if DOCROOT_UID then chown
# todo: figure out how to pass a non root id and call things like tee for setting stuff via sudo or something
#
# DOCROOTCMS_OWNERSHIP: if provided will be used to change the file ownerships

echo "working directory: $(pwd)"
echo "DOCROOTCMS_OWNERSHIP: $DOCROOTCMS_OWNERSHIP"


# determine if our current directory is already attached to git remote
cp -R /usr/src/app/. /usr/src/install/
# make sure our cache, data and images folders exist (they should if cloning properly but errors if not at startup)
mkdir -p cache
mkdir -p images
mkdir -p data
if [[ -z "$DOCROOTCMS_OWNERSHIP" ]]; then
    echo "No env DOCROOTCMS_OWNERSHIP.  Skipping permissions."
else
    echo "setting permissions to [$DOCROOTCMS_OWNERSHIP]"
    chown -R $DOCROOTCMS_OWNERSHIP /usr/src/install/
fi
