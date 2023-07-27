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
This artifact is meant to be run on CloudLab, using this
[cloudlab profile](https://www.cloudlab.us/instantiate.php?profile=23d8454f-fa5d-11ed-b28b-e4434b2381fc&rerun_instance=73cfbf01-2bc4-11ee-9f39-e4434b2381fc)
There should be 8 nodes of type `d430` running `UBUNTU 20.04`.

Get a shell on `node4` via ssh.
On `node4`, run `git clone ...` to download a copy of the artifact to `~/grove-artifact`.

# Proofs

1. [**SLOW**] `./coq-setup.sh`  
This installs Coq 8.17.0.
If you have Coq 8.17 installed on your machine ([installation
instructions](https://coq.inria.fr/opam-using.html)), you can follow the rest of
the steps on your machine.
2. `cd perennial`
3. [**SLOW**]  
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

Optionally, confirm that the Go code is in sync with its formal model in Coq.
Install the `Goose` tool with `go get github.com/tchajed/goose/cmd/goose`.
Then, in the `perennial` directory, run `./etc/update-goose.py --compile  --gokv
../gokv`.

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
linked above.

Get a shell on to `node4`, e.g .`ssh node4`.
Make sure `grove-artifact` has been cloned in the home directory on `node4`.
Then, from inside the `grove_artifact` directory on `node4`, run:
[**VERY SLOW**]
```
./performance-eval.py
```

The script that actually runs the experiment is `gokv/simplepb/bench/eval-run.py`.
The rest of `performance-eval.py` sets up the machines to run the experiments
and at the end generates a pdf with the figures.
The scripts for experiments are in `gokv/simplepb/bench/experiments/e1.py`,
`.../e2.py`, and `.../e3.py`. They each have a comment at the top describing how
they work.

## Manual instructions (e.g. to run a single experiment)
Connect to `node4` in the cluster via `ssh node4` or similar.
After getting a shell at the home directory of the cloudlab machine, run `git
clone ...` to download a copy of the artifact to `~/grove-artifact`.
Then run the commands
```
cd grove-artifact
git submodule update --init --recursive
```
