import networkx as nx

from aalpy.automata import MealyMachine

RESET_IN = "RESET-SYS"
RESET_OUT = "epsilon"

def find_separating_sequence(fsm1 : MealyMachine, fsm2 : MealyMachine) -> list[str]:
    visited = set()
    to_explore = [(fsm1.initial_state, fsm2.initial_state, [])]
    alphabet = set(fsm1.get_input_alphabet()).intersection(set(fsm2.get_input_alphabet()))
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


def calculate_fingerpint_sequences(fsms : dict[MealyMachine,str]) -> list[list[str]]:
    partition = [set(fsms.keys())]
    sequences : list[list[str]] = []
    while len(partition) != len(fsms.keys()):
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
    graph = build_distinguishing_graph(sequences,fsms)
    return graph


def fresh_var(count : int):
    return "a" + str(count)

def build_distinguishing_graph(sequences : list[list[str]], machines : dict[MealyMachine,str]):
    counter = 1
    root = fresh_var(0)
    distinguishing_graph = nx.MultiDiGraph()
    distinguishing_graph.add_node(root, label=machines.keys())
    current_nodes = [root]
    for sequence in sequences:
        new_current_nodes = set()
        for current_node in current_nodes:
            output_dict : dict[MealyMachine, list[str]] = {}
            for machine in distinguishing_graph.nodes[current_node]["label"]:
                machine.reset_to_initial()
                for input in sequence:
                    output = machine.step(input)
                    if machine not in output_dict.keys():
                        output_dict[machine] = [output]
                    else:
                        output_dict[machine] = output_dict[machine] + [output]
        

            for machine, output in output_dict.items():
                current_selected_node = current_node
                for i in range(0,len(sequence)):
                    found = False
                    for edge in distinguishing_graph.out_edges(current_selected_node, data=True):
                        if edge[2]["label"] == sequence[i] + "/" + output[i]:
                            found = True
                            distinguishing_graph.nodes[edge[1]]["label"].add(machine)
                            current_selected_node = edge[1]
                            break
                    if not found:
                        new_node = fresh_var(counter)
                        counter = counter + 1
                        distinguishing_graph.add_node(new_node, label={machine})
                        distinguishing_graph.add_edge(current_selected_node,new_node, label=sequence[i] + "/" + output[i])
                        current_selected_node = new_node
                    
                    if i == (len(sequence)-1):
                        new_current_nodes.add(current_selected_node)
        
        
        current_nodes.clear()
        if sequence != sequences[-1]:
            for node in new_current_nodes:
                new_node = fresh_var(counter)
                counter = counter + 1
                distinguishing_graph.add_node(new_node, label=distinguishing_graph.nodes[node]["label"])
                distinguishing_graph.add_edge(node,new_node, label=RESET_IN + "/" + RESET_OUT)
                current_nodes.append(new_node)
    
    for node in distinguishing_graph.nodes(data = True):
        if distinguishing_graph.out_degree(node[0]) > 0:
            for edge in distinguishing_graph.out_edges(node[0], data=True):
                input, output = edge[2]["label"].split("/")
                node[1]["label"] = input
                edge[2]["label"] = output
        else:
            node[1]["label"] = machines[list(node[1]["label"])[0]]  

    nx.drawing.nx_agraph.write_dot(distinguishing_graph,"CDS.dot")
    return distinguishing_graph