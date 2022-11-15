from aalpy.SULs.AutomataSUL import MealySUL
from aalpy.automata import MealyMachine


def fingerprint_system(sut : MealySUL, fsms : list[MealyMachine], sequences : list[list[str]]) -> MealyMachine:
    for sequence in sequences:
        sut.pre()
        output = str(sut.step(sequence[0]))
        for i in range(1,len(sequence)):
            output = output + " " + str(sut.step(sequence[i]))
        new_fsms = []
        for fsm in fsms:
            output_seq = fsm.compute_output_seq(fsm.initial_state,sequence)
            output_candidate = str(output_seq[0])
            for i in range(1,len(output_seq)):
                output_candidate = output_candidate + " " + str(output_seq[i])
            if output_candidate == output:
                new_fsms.append(fsm)
        fsms = new_fsms
        sut.post()
    if len(fsms) == 1:
        return fsms[0]
    else:
        raise SystemExit('Unable to fingerprint the system')

