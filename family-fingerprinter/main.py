import getopt
import sys
import time
from aalpy.SULs.AutomataSUL import MealySUL
from aalpy.utils.FileHandler import load_automaton_from_file
from aalpy.automata import MealyMachine
import networkx as nx

from base.FFSM.FFSM import FFSM, RESET_OUT, RESET_IN
from base.fingerprint.passive.passive import trace_fingerprinting
from base.fingerprint.passive.filehandler import read_traces
from base.fingerprint.active.active import Simulator
from base.fingerprint.active.CADS import CADS
from base.fingerprint.active.CPDS import CPDS
from base.fingerprint.active.ShuLeeReset import ShuLeeReset
from base.fingerprint.active.ConfigurationDistinguishingSequence import ConfigurationDistinguishingSequence


def reset_when_sink(fsm : MealyMachine):
    for state in fsm.states:
        is_sink = True
        for out_state in state.transitions.values():
            if out_state != state:
                is_sink = False
                break
        if is_sink:
            state.transitions[RESET_IN] = fsm.initial_state
            state.output_fun[RESET_IN] = RESET_OUT



def main():
    active_mode = None
    ffsm_file = None
    file = None
    mode = None
    sequence_file = None
    try:
        arguments = getopt.getopt(sys.argv[1:],"p:f:a:",["passive=", "FFSM=", "active=", "preset", "adaptive", "shulee", "sequence="])
        for current_arg, current_val in arguments[0]:
            if current_arg in ("-p", "--passive"):
                if active_mode == None:
                    active_mode = False
                    file = current_val
                else:
                    raise Exception("Already in active mode, please select active OR passive mode")
            elif current_arg in ("-f", "--FFSM"):
                ffsm_file = current_val
            elif current_arg in ("--adaptive"):
                mode = 0
            elif current_arg in ("--preset"):
                mode = 1
            elif current_arg in ("--shulee"):
                mode = 2
            elif current_arg in ("--sequence"):
                sequence_file = current_val
            elif current_arg in ("-a", "--active"):
                if active_mode == None:
                    active_mode = True
                    file = current_val
                else:
                   raise Exception("Already in passive mode, please select active OR passive mode")       
    except getopt.error as err:
        print(str(err))
        return
    if ffsm_file == None and sequence_file == None:
        print("Please give a FFSM reference model or a sequence model")
        return
    elif active_mode == False:
        ffsm = FFSM.from_file(ffsm_file)
        traces = read_traces(file)
        possible_variants = trace_fingerprinting(ffsm, traces)
        print("variant: ", possible_variants)
    elif active_mode == True and mode is not None:
        ds : ConfigurationDistinguishingSequence = None
        ffsm_alphabet : set[str] = None
        if ffsm_file is not None:
            ffsm = FFSM.from_file(ffsm_file)
            ffsm.reset_when_sink()
            ffsm_alphabet = ffsm.alphabet
            ffsm.reset_to_initial_state()
            ffsm.make_input_complete()

            begin_time = None 
            if mode == 0:
                begin_time = time.time()
                ds = CADS(ffsm=ffsm)
            elif mode == 1:
                begin_time = time.time()
                ds = CPDS(ffsm=ffsm)
            elif mode == 2:
                begin_time = time.time()
                ds = ShuLeeReset(ffsm=ffsm)
            end_time = time.time()
            diff_time = (end_time - begin_time)
            print("calculation costs: ", diff_time, " seconds")
            if ds.exists:
                nx.drawing.nx_agraph.write_dot(ds.seperating_sequence,"CDS.dot")
            else:
                sys.exit("cDS does not exists")
        else:
            if mode == 0:
                ds = CADS.from_file(sequence_file)
            elif mode == 1:
                ds = CPDS.from_file(sequence_file)
            elif mode == 2:
                ds = ShuLeeReset.from_file(sequence_file)
            for node in ds.seperating_sequence.nodes.data():
                if ds.seperating_sequence.out_degree(node[0]) > 0:
                    ffsm_alphabet.add(node[1]["label"])

                
        fsm = load_automaton_from_file(file,'mealy')
        reset_when_sink(fsm)        
        missing_alphabet = ffsm_alphabet.difference(set(fsm.get_input_alphabet()))

        for a in missing_alphabet: #for the non exisiting alphabet add a self loop on the initial state, make_input_complete() will do the rest
            fsm.initial_state.transitions[a] = fsm.initial_state
            fsm.initial_state.output_fun[a] = 'epsilon'
        
        fsm.make_input_complete()

        sul_fsm = MealySUL(fsm)
        sim = Simulator(ds)
        possible_variants = sim.fingerprint_system(sul_fsm)
        print("variant: ", possible_variants)



if __name__ == "__main__":
    main()