package com.thesis.checker;

import net.automatalib.automata.transducers.impl.FastMealy;
import net.automatalib.automata.transducers.impl.compact.CompactMealy;
import net.automatalib.automata.transducers.impl.compact.CompactMealyTransition;
import net.automatalib.graphs.base.compact.CompactEdge;
import net.automatalib.graphs.base.compact.CompactGraph;
import net.automatalib.serialization.dot.DOTGraphParser;

import java.io.File;
import java.io.FileInputStream;
import java.io.InputStream;
import java.lang.reflect.Array;
import java.util.ArrayList;
import java.util.*;
import java.util.function.Function;
import java.util.function.Supplier; 
import net.automatalib.util.automata.Automata;
import net.automatalib.words.impl.FastAlphabet;
import net.automatalib.words.impl.ListAlphabet;
/**
 * Hello world!
 *
 */
public class App 
{

    public static CompactMealy<String,String> toMealy(CompactGraph<String,String> compactGraph, ListAlphabet<String> inputs){
        CompactMealy<String,String> mealy = new CompactMealy<>(inputs);

        int initial_state = -1;
        for (int node : compactGraph.getNodes()){
            for (CompactEdge<String> edge : compactGraph.getOutgoingEdges(node)){
                if (edge.getProperty() == null){
                    for(int i = 0; i < edge.getTarget(); ++i){
                        mealy.addState();
                    }
                    initial_state = mealy.addInitialState();
                }
            }
            if (initial_state != -1){
                break;
            }
        }
        int diff_states = compactGraph.getNodes().size() - mealy.getStates().size();
        for (int i = 0; i < diff_states; ++i){
            mealy.addState();
        }

        for (int node : compactGraph.getNodes()){
            for (CompactEdge<String> edge : compactGraph.getOutgoingEdges(node)){
                if (edge.getProperty() != null){
                    String[] label = edge.getProperty().split("/");
                    mealy.addTransition(node, label[0], edge.getTarget(), label[1]);
                }
            }
        }
        return mealy;
    }
    public static void main( String[] args )
    {
        ArrayList<String> inputs = new ArrayList<String>();
        
        Function<Map<String,String>,String> parseFunction = map ->{ 
            if(map.get("label") != null){
                String input = map.get("label").split("/")[0];
                if (!inputs.contains(input)){
                    inputs.add(input);
                }
            } 
            return map.get("label");
        };

        CompactGraph<String,String> graph1 = new CompactGraph<>();
        CompactGraph<String,String> graph2 = new CompactGraph<>();
        Supplier<CompactGraph<String,String>> supGraph1 = () -> graph1;
        Supplier<CompactGraph<String,String>> supGraph2 = () -> graph2;  
        DOTGraphParser<String,String,CompactGraph<String,String>> parser1 = new DOTGraphParser<>(supGraph1,parseFunction,parseFunction);
        DOTGraphParser<String,String,CompactGraph<String,String>> parser2 = new DOTGraphParser<>(supGraph2,parseFunction,parseFunction);
        File file_1 = new File(args[0]);
        File file_2 = new File(args[1]);
        try {
            CompactGraph<String,String> machine1 = parser1.readModel(file_1);
            CompactGraph<String,String> machine2 = parser2.readModel(file_2);
            ListAlphabet<String> alphabet = new ListAlphabet<String>(inputs);
            CompactMealy<String,String> mealy1 = toMealy(machine1, alphabet);
            CompactMealy<String,String> mealy2 = toMealy(machine2, alphabet);
            boolean equiv = Automata.testEquivalence(mealy1, mealy2, inputs);
            System.out.println(equiv);
        } catch (Exception e) {
            System.out.println(e);
        }
        
    }


}
