#!/bin/bash --login
set -e
conda activate hyp3-gamma
exec tini -g -- jupyter "$@"
