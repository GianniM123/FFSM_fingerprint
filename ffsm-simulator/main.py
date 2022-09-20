from FFSM.FFSM import FFSM
from passive import trace_fingerprinting

ffsm = FFSM.from_file("../FFSM_diff/algorithm/out.dot")

trace_fingerprinting(ffsm, [("Start ", " 1"), ("Exit ", " 1")])