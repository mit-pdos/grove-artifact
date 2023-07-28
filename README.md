# Overview

This is the artifact corresponding to the SOSP'23 paper "Grove: a
Separation-Logic Library for Verifying Distributed Systems".

There are two parts:
1. several distributed systems components written in Go as well as a performance
evaluation of the key-value service GroveKV;
2. the Grove verification library and mechanized proofs for the distributed
systems components, including a proof that GroveKV is a crash-safe, linearizable
KV system.

The two parts (1) reproduce the performance evaluation results from section 6
and (2) check the mechanized proofs and that they correspond to the top-level
theorems described in section 4.4.

These parts live in their own git repos, both included here as git submodules:

* the `gokv` repo and submodule contains the Go implementations of the distributed
systems components as well as scripts for the performance evaluation of GroveKV.
* the `perennial` repo contains the Grove separation logic library and the
specs+proofs of the code in the `gokv` repo.

# Set up machines
This artifact, specifically the performance evaluation, is primarily meant to be
run on CloudLab, using this
[cloudlab profile](https://www.cloudlab.us/instantiate.php?profile=23d8454f-fa5d-11ed-b28b-e4434b2381fc&rerun_instance=73cfbf01-2bc4-11ee-9f39-e4434b2381fc)
There should be 8 nodes of type `d430` running `UBUNTU 20.04`.

Get a shell on `node4` via ssh.
On `node4`, run `git clone https://github.com/mit-pdos/grove-artifact` to
download a copy of the artifact to `~/grove-artifact`.
Then run
```
cd grove-artifact
git submodule update --init --recursive
```
to download the other repos.

## Running outside CloudLab
The proof part can be done on any machine, so long as the right version of Coq
is installed, as explained in the "Proofs" section.

The performance evaluation scripts in `gokv/simplepb/bench` are tailored for
CloudLab, and are only a starting point for running this eval on other hardware
setups, with some scripts being reusable and others needing changes.  The
scripts assume that there are 8 nodes with the same numbers of CPUs/cores as
`d430` machines, which can connect via `ssh` to each other with the names
`node0, ..., node7`. The `eval-setup.py` script assumes that the machines are
running Ubuntu 20.04 and installs various packages (e.g. Go and python). The
scripts should be adaptable to non-CloudLab setups if the nodes are running
Ubuntu or otherwise have the same packages installed. As a last note, only
experiment `e3.py` needs 8 machines (some for running clients), while the other
experiments can work with 5 machines.

# Proofs
Here are the steps for building/checking the proofs, including all of the
"top-level theorems" from 4.4 in the paper.

1. [**~15mins**] `./coq-setup.sh`  
This installs Coq 8.17.0.
Alternatively, if you have Coq 8.17 installed on your machine ([installation
instructions](https://coq.inria.fr/opam-using.html)), you can follow the rest of
the steps on your machine.
2. `cd perennial`
3. [**~30mins**]  
        ```
        make -j`nproc` src/program_proof/simplepb/apps/print_assumptions.vo
        ```
The top-level proof file `src/program_proof/simplepb/apps/print_assumptions.v`,
and this command builds it and all of its dependencies; this transitively covers
all the Grove proofs.  Building this file will print all the axioms that the
proof depends on, and if there were any incomplete parts of the proof, the
`Print Assumptions` command in the file would show them.
At the end, you should only see some standard Coq axioms that you can ignore 
(called `sig_forall_dec` and `functional_extensionality_dep`).

You can also confirm that the Go code is in sync with its formal model in Coq.
Install the `Goose` tool with `go get github.com/tchajed/goose/cmd/goose`.
Then, in the `perennial` directory, run `./etc/update-goose.py --compile  --gokv
../gokv`. In the `update-goose.py` script, you can see the list of the GroveKV
packages in lines 252-264, mostly contained under `simplepb`. You can try
changing a line of code in the `gokv` directory, and rerunning the
`update-goose.py` command and you should see a line change in
`perennial/external` directory, and the existing proof for that component will
likely no longer work.

## Reading the top-level theorems
Let's go through the list from section 4.4:

1. The `main` function is crash idempotent.
The Go function is `func kv_replica_main` in `gokv/simplepb/apps/closed/mains.go`.
The proof of crash idempotence is `Lemma wpr_kv_replica_main` in
`perennial/src/program_proof/simplepb/apps/closed_proof.v`.
More precisely, this theorem says:
given ownership of the resources listed in lines 86-90, it is safe to run
`kv_replica_main(fname, me)`, and restart if it stops running due to the machine
crashing.

2. It is always safe to `Reconfigure`.
The Go function is `func EnterNewConfig` in `gokv/simplepb/admin/admin.go`.
The proof for it is `Lemma wp_Reconfig` in
`perennial/src/program_proof/simplepb/admin_proof.v`.
This is a Hoare triple, written in Coq as `{{{ precondition }}} code {{{ postcondition }}}`.
This theorem has a precondition labelled `"#Hhost"`, which says that the servers
passed into it must be valid primary/backup servers.

3. `MakeClerk` correct initializes a clerk.
The Go function is `func MakeClerk` in `gokv/simplepb/apps/kvee/clerk.go`.
The proof for it is `Lemma wp_MakeClerk` in
`perennial/src/program_proof/simplepb/apps/kvee_proof.v`.
This theorem says: so long as `confHost` is indeed the config server for a
GroveKV system, calling `MakeClerk` results in ownership as postcondition.

4. `clerk.Put` and `clerk.Get` behave like a linearizable key-value map.
The Go functions are `Put` and `Get` in `gokv/simplepb/apps/kvee/clerk.go`.
The proof for them is `Lemma wp_Clerk__Put` and `Lemma wp_Clerk__Get` in
`perennial/src/program_proof/simplepb/apps/kvee_proof.v`.
The theorems are written in terms of a `kv_ptsto` ("key-value points-to") ghost
resource. The parameter `γkv` identifies a particular instance of GroveKV, since
there could be two separate copies running. 
The angle brackets `<<<` and `>>>` are notation for a "logically atomic" spec,
which is an encoding of linearizability in separation logic. As a first reading,
one can ignore the angle brackets and treat their contents as pre and
postconditions.

Finally, check that all of the theorems listed above are included in the
`print_assumptions.v` file, so building it checks all of them.

# Performance experiments

The performance experiments are designed to run on CloudLab, using the profile
linked above. The performance evaluatoin covers Figures 6, 7, 8 from the paper.

The times in bold preceding the steps approximate how long the step should take
for all the commands to finish. The active human time is entering in the few
commands directly listed here, so the overall evaluation should require little
active human time.

[**1 min**]
From your a machine which is able to ssh to all of the cloudlab nodes (e.g. your
laptop), run `./ssh-setup.py` to set up SSH between the nodes.
You will have to modify `ssh-setup.py` to include the list of hostnames for the
CloudLab machines you have access to, and provide your username in lines 9 and
10.

Get a shell on to `node4` of the CloudLab setup; the rest of the steps are to be
run on `node4`.
Make sure `grove-artifact` has been cloned in the home directory on `node4` (see
the "Set up machines" section).

[**15mins**]
Run `cd ~/grove-artifact/gokv/simplepb/bench` then run the script
`./eval-setup.py`. This will do a one-time setup of all the machines, such as
downloading Go and building the GroveKV benchmark program. Ignore the last line
of output about running `make test`; that's output from building `redis`.

[**3mins**]
Let's test that the evaluation is actually set up.
To start, disconnect from `node4` and reconnect over `ssh`; the `eval-setup.py`
script adds stuff to the shell environment, and reconnecting
will reliably make those changes take effect.
Next, we can run a relatively quick performance experiment.  The data for this
will appear in `~/gokv/simplepb/bench/data/reconfig/`, so make sure the
directory is empty to begin with (or doesn't exist).  To run the experiment run
```
cd ~/gokv/simplepb/ 
python -m bench.experiments.e2 -v
```
(still on `node4`).  At the end, there should see be data in the
`./bench/data/reconfig/`, specifically two files `reads.dat` and
`writes.dat`. These files get imported in the final figure in
`~/gokv/simplepb/bench/figure/`.

[**A few hours**]
Now, to run the full performance evaluation run the commands
```
cd ~/gokv/simplepb/bench 
./eval-run.py
```
You may want to run these commands after running `screen -S artifact` to start a
long-running screen session. If your SSH connection gets interrupted the
experiments will keep running, you can reconnect to that session with `screen -r`.

After getting this running, it may be helpful to read the notes about how the
experiments work. Corresponding to the three figures, there are 3 experiments.
The three experiment scripts (`e1.py, e2.py, e3.py` referenced by `eval-run.py`)
contain notes at the top that describe each experiment. The notes also say where
the raw data ends up, so you can delete those directories to make sure you get a
fresh run of an experiment.

[**1min**]
To build the figure, run
```
cd ~/gokv/simplepb/data
pdflatex p.tex
```
This outputs `p.pdf`, which you can download.
Compare the figure of `p.pdf` with the corresponding figures in the paper.
