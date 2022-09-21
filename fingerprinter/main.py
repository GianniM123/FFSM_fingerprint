from base.FFSM.FFSM import FFSM
from base.fingerprint.passive import trace_fingerprinting
from base.fingerprint.filehandler import read_traces
from getopt import getopt
import sys


def main():
    active_mode = None
    ffsm_file = None
    traces_file = None
    try:
        arguments = getopt(sys.argv[1:],"pf:t:",["passive", "FFSM=", "traces="])
        for current_arg, current_val in arguments[0]:
            if current_arg in ("-p", "--passive"):
                active_mode = False
            elif current_arg in ("-f", "--FFSM"):
                ffsm_file = current_val
            elif current_arg in ("-t", "--traces"):
                traces_file = current_val
    except getopt.error as err:
        print(str(err))
        return
    if active_mode == False and ffsm_file is not None and traces_file is not None:
        ffsm = FFSM.from_file(ffsm_file)
        traces = read_traces(traces_file)
        features = trace_fingerprinting(ffsm, traces)
        print(features)




if __name__ == "__main__":
    main()