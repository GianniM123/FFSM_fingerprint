# FFSM_diff

## Folder structure
- `algorithm` contains the FFSM_diff algorithm

## Dependencies
<ul>
<li> <a href="https://pysmt.readthedocs.io/en/latest/"> pySMT </a> </li>
<li> <a href="https://networkx.org/"> NetworkX </a> </li>
<li> <a href="https://scipy.org/"> scipy </a> </li>
<li> scikit-umfpack </li>
</ul>

## NetworkX
Install the latest release:
```
$ pip install networkx[default]
```

## pySMT
Install the latest version of pySMT by:
```
$ pip install pysmt
```
After that the SMT-solvers can be installed by:
```
$ pysmt-install --all
```

The solvers are saved in ~/.smt_solvers

### Linux Ubuntu 20.04
CVC4 directory was not correctly named, renaming the directory fixed it.

### Windows 10
On Windows not every SMT solver can be installed, some give errors.\
The SMT-solvers that work on my machine:
<ul>
<li> msat </li>
<li> z3 </li>
</ul>

