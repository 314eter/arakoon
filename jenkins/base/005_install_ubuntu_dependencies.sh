#!/bin/bash -xue

sudo aptitude update || true

for PKG in libssl-dev \
 texlive texlive-latex-extra \
 git python-epydoc graphviz libsnappy-dev; do
    sudo aptitude install -yVDq $PKG
done
