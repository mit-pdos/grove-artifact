#!/usr/bin/env bash

sudo add-apt-repository -y ppa:avsm/ppa
sudo apt update
sudo apt install -y opam libgmp-dev

opam init --auto-setup --bare
opam switch -j4 create 5.0.0
eval $(opam env)
opam pin -y -j4 add coq 8.17.0
