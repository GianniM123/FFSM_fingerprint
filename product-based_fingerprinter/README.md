# Product-based fingerprinter

## Needed packages
The following pip packages are needed to run the fingerpinter:
 - networkx[default]
 - pydot
 - pygraphviz
 - aalpy

## Usage
The fingerprinter always requires at least a folder with FSM modles, this must be provided by the `-f` option. The system which needs to be fingerprinted needs to be given via the `-s` option.

```
python3 main.py -f <path/to/ffsm.dot> -s <path/to/fsm.dot> 
```

By default, a `sequence.dot` is created. In this dot-file the fingerprinting tree can be found.