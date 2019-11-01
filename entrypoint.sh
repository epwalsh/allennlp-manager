#!/bin/bash

# Exit script if any commands fail.
set -e
set -o pipefail

echo "Current commit: ${COMMITHASH}"

# Execute the arguments to this script as commands themselves.
exec "$@"
