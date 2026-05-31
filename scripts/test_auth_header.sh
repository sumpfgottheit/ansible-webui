#!/usr/bin/env bash

set -e

cd "$(dirname "$0")/.."

echo ''
echo 'INTEGRATION TESTS AUTH HEADER'
echo ''

export AW_AUTH='header'
export AW_REMOTE_USER_HEADER='HTTP_REMOTE_USER'

source ./scripts/test_base.sh

if ! python3 test/integration/auth/header.py
then
  failure
fi

success
