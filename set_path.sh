#!/bin/bash

AMBERITY_DIR=$(dirname $(readlink -f "${BASH_SOURCE[0]}"))

export AMBERITY_DIR
export PATH=$AMBERITY_DIR:$PATH
export PATH=$AMBERITY_DIR/utilities:$PATH
