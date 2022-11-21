from aalpy.automata import MealyMachine

def find_separating_sequence(fsm1 : MealyMachine, fsm2 : MealyMachine) -> list[str]:
    visited = set()
    to_explore = [(fsm1.initial_state, fsm2.initial_state, [])]
    alphabet = fsm1.get_input_alphabet()
    while to_explore:
        (curr_s1, curr_s2, prefix) = to_explore.pop(0)
        visited.add((curr_s1, curr_s2))
        for i in alphabet:
            o1 = fsm1.output_step(curr_s1, i)
            o2 = fsm2.output_step(curr_s2, i)
            new_prefix = prefix + [i]
            if o1 != o2:
                return new_prefix
            else:
                next_s1 = curr_s1.transitions[i]
                next_s2 = curr_s2.transitions[i]
                if (next_s1, next_s2) not in visited:
                    to_explore.append((next_s1, next_s2, new_prefix))
    
    raise SystemExit('Distinguishing sequence could not be computed.')


def calculate_fingerpint_sequences(fsms : list[MealyMachine]) -> list[list[str]]:
    partition = [set(fsms)]
    sequences : list[list[str]] = []
    while len(partition) != len(fsms):
        for part in partition:
            if len(part) > 1:
                list_set = list(part)
                fsm1 = list_set[0]
                fsm2 = list_set[1]
                try:
                    seq = find_separating_sequence(fsm1,fsm2)
                    sequences.append(seq)
                    break     
                except Exception as e:
                    raise SystemExit('Could not distinguish the given machines.')
        new_partition = []
        
        for fsm_set in partition:
            if len(fsm_set) == 1:
                new_partition.append(fsm_set)
            else:
                split_dict : dict[str,set] = {}
                need_to_add = set()
                for f in fsm_set:
                    try:
                        output_seq = f.compute_output_seq(f.initial_state,sequences[-1])
                        output = str(output_seq[0])
                        for i in range(1,len(output_seq)):
                            output = output + " " + str(output_seq[i])
                        if output in split_dict.keys():
                            split_dict[output].add(f)
                        else:
                            split_dict[output] = {f}
                    except:
                        #input not defined for fsm
                        need_to_add.add(f)
                for add in need_to_add:
                    for key in split_dict.keys():
                        split_dict[key].add(add)

                for new_part in split_dict.values():
                    new_partition.append(new_part)
        
        partition = new_partition
    return sequences
                
