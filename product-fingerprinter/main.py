import getopt
import sys
import os
import timeit
import networkx as nx

from aalpy.SULs.AutomataSUL import MealySUL
from aalpy.utils.FileHandler import load_automaton_from_file
from aalpy.automata import MealyMachine

from base.SeparatingSequence import calculate_fingerpint_sequences
from base.fingerprint import fingerprint_system


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
        names : dict[MealyMachine, str] = {}
        for path, _, files in os.walk(folder):
            if path == folder:
                for file in files:
                    p = os.path.join(path,file)
                    fsm = load_automaton_from_file(p,'mealy')
                    names[fsm] = file
 
        fsm = load_automaton_from_file(sut,'mealy')
        
        sul_fsm = MealySUL(fsm)

        begin_time = timeit.default_timer()
        distinguish_graph = calculate_fingerpint_sequences(names)
        end_time = timeit.default_timer()
        diff_time = end_time - begin_time
        print("calculation costs: ", diff_time, " seconds")

        nx.drawing.nx_agraph.write_dot(distinguish_graph,"sequence.dot")

        variant = fingerprint_system(sul_fsm,distinguish_graph)
        print("variant: ", variant)
                




if __name__ == "__main__":
    main()