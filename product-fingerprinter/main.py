import getopt
import sys
import os
from datetime import datetime

from aalpy.SULs.AutomataSUL import MealySUL
from aalpy.utils.FileHandler import load_automaton_from_file
from aalpy.automata import MealyMachine

from base.SeparatingSequence import calculate_fingerpint_sequences
from base.fingerprint import fingerprint_system

def complete_fsm(fsm : MealyMachine, alphabet : set[str]):
    for a in alphabet.difference(set(fsm.get_input_alphabet())): #for the non exisiting alphabet add a self loop on the initial state, make_input_complete() will do the rest
        fsm.initial_state.transitions[a] = fsm.initial_state
        fsm.initial_state.output_fun[a] = 'epsilon'

    fsm.make_input_complete()


def main():
    folder = None
    sut = None
    try:
        arguments = getopt.getopt(sys.argv[1:],"f:s:",["folder=", "sut="])
        for current_arg, current_val in arguments[0]:
            if current_arg in ("-f", "--folder"):
                folder = current_val
            elif current_arg in ("-s", "--sut"):
                sut = current_val
    except getopt.error as err:
        print(str(err))
        return
    
    if folder is not None and sut is not None:
        fsms : list[MealyMachine] = []
        names : list[tuple[str,MealyMachine]]= []
        alphabet = set()
        for path, _, files in os.walk(folder):
            if path == folder:
                for file in files:
                    p = os.path.join(path,file)
                    fsm = load_automaton_from_file(p,'mealy')
                    names.append((file,fsm))
                    fsms.append(fsm)
                    alphabet = alphabet.union(set(fsm.get_input_alphabet()))

        for fsm in fsms:
            complete_fsm(fsm,alphabet)
        
        fsm = load_automaton_from_file(sut,'mealy')
        complete_fsm(fsm,alphabet)
        
        sul_fsm = MealySUL(fsm)

        begin_time = datetime.now()
        sequences = calculate_fingerpint_sequences(fsms)
        end_time = datetime.now()
        diff_time = (end_time - begin_time).total_seconds()
        print("calculation costs: ", diff_time, " seconds")

        variant = fingerprint_system(sul_fsm,fsms,sequences)
        for file, fsm in names:
            if variant == fsm:
                print("variant: ", file)
                




if __name__ == "__main__":
    main()