#!/usr/bin/env bash

set -euo pipefail

if [ ! -d '/repo/src/oxl_ansible_webui/' ]
then
  echo 'ERROR: Requires Repository-Root to be mounted as docker-volume to /repo/'
  exit 1
fi

cd /repo
PYTHONPATH='' python3 -m pytest "$@"
