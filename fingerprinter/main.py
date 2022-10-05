from base.FFSM.FFSM import FFSM
from base.fingerprint.passive import trace_fingerprinting
from base.fingerprint.filehandler import read_traces
from getopt import getopt
from aalpy.utils.FileHandler import load_automaton_from_file
from aalpy.SULs.AutomataSUL import MealySUL
import sys


def main():
    active_mode = None
    ffsm_file = None
    file = None
    try:
        arguments = getopt(sys.argv[1:],"p:f:a:",["passive=", "FFSM=", "active="])
        for current_arg, current_val in arguments[0]:
            if current_arg in ("-p", "--passive"):
                if active_mode == None:
                    active_mode = False
                    file = current_val
                else:
                    raise Exception("Already in active mode, please select active OR passive mode")
            elif current_arg in ("-f", "--FFSM"):
                ffsm_file = current_val
            elif current_arg in ("-a", "--active"):
                if active_mode == None:
                    active_mode = True
                    file = current_val
                else:
                   raise Exception("Already in passive mode, please select active OR passive mode")       
    except getopt.error as err:
        print(str(err))
        return
    if ffsm_file == None:
        print("Please give a FFSM reference model")
        return
    elif active_mode == False:
        ffsm = FFSM.from_file(ffsm_file)
        traces = read_traces(file)
        features = trace_fingerprinting(ffsm, traces)
        print(features)
    elif active_mode == True:
        ffsm = FFSM.from_file(ffsm_file)
        fsm = load_automaton_from_file(file,'mealy')
        sul_fsm = MealySUL(fsm)
        output = ffsm.step("Pause ", [])
        print(output)
        output = ffsm.step("Pause ", ["bowling"])
        print(output)



if __name__ == "__main__":
    main()