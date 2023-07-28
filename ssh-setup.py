#!/usr/bin/env python3
from os import system as do

# This setups up the CloudLab machines with some SSH keys to have so they can
# SSH to each other.

# TO RUN THIS:
# nodes = [ "pc712.emulab.net", ... ] and "upamanyu" with your username.
nodes = [ f"node{j}" for j in range(8) ]
username = "upamanyu"
for n in nodes:
    do(f"ssh -o StrictHostKeyChecking=no {n} 'echo setting up {n}'")
    do(f"""ssh {username}@{n} <<ENDSSH
/usr/bin/geni-get key > ~/.ssh/id_rsa ;
chmod 600 ~/.ssh/id_rsa ;
ssh-keygen -y -f ~/.ssh/id_rsa > ~/.ssh/id_rsa.pub ;
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys ;
chmod 644 ~/.ssh/authorized_keys
ENDSSH
    """)
