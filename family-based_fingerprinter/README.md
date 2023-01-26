# Fingerprinter
The fingerprinter always requires at least an FFSM model, this must be provided by the `-f` option.

## Needed packages
The following pip packages are needed to run the fingerpinter:
 - networkx[default]
 - pydot
 - pygraphviz
 - aalpy

## Active
To actively fingerprint a system the `-a` option must be given with a path to a Finite State Machine representation of a system. Also the option of a `preset`, `adaptive` or `shulee` can be set by using the corrosponding `--adaptive`,  `--preset` or `--shulee` flags.

```
python3 main.py -f <path/to/ffsm.dot> -a <path/to/fsm.dot> --<adaptive,preset,shulee>
```
By default, a `CDS.dot` is created. In this dot-file the fingerprinting tree can be found.

## Passive
To passively fingerprint a system the `-p` option must be given with a path to a file which contains a set of traces.

```
python3 main.py -f <path/to/ffsm.dot> -p <path/to/traces.txt>
```