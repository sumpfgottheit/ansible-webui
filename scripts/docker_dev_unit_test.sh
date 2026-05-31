#!/usr/bin/env bash

set -euo pipefail

cd "$(dirname "$0")/../docker"

if ! docker image ls | grep -q 'aw-dev-be'
then
  echo '### BUILDING aw-dev-be IMAGE ###'
  docker build -f Dockerfile_dev_backend -t aw-dev-be --network=host --no-cache --build-arg "UID=$(id -u)" ..
fi

echo '### RUNNING UNIT TESTS IN DOCKER ###'
docker run -it --rm --name aw-unit-test \
  --network=host \
  --volume "$(pwd)/..:/repo" \
  --entrypoint /entrypoint_unit_tests.sh \
  aw-dev-be "$@"
