# Fingerprinter
The fingerprinter always requires at least a FFSM model, this must be provided by the `-f` option.

## Needed packages
The following pip packages are needed to run the fingerpinter:
 - networkx[default]
 - pydot
 - pygraphviz
 - aalpy
 - flamapy
 - flamapy-sat

## Active
To actively fingerprint a system the `-a` option must be given with a path to a Finite State Machine representation of a system.

```
python3 main.py -f <path/to/ffsm.dot> -a <path/to/fsm.dot>
```


## Passive
To passively fingerprint a system the `-p` option must be given with a path to a file which contains a set of traces.

```
python3 main.py -f <path/to/ffsm.dot> -p <path/to/traces.txt>
```