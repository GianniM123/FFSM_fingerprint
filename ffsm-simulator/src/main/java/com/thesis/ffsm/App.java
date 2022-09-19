package com.thesis.ffsm;

import java.io.File;
import java.io.FileReader;
import java.util.Map;
import java.util.function.*;

import org.jgrapht.graph.*;
import org.jgrapht.nio.dot.*;
import org.jgrapht.nio.Attribute;

public class App 
{
    public static void main( String[] args )
    {
        DOTImporter<ConditionalState,ConditionalEdge> importGraph = new DOTImporter<>();
        DirectedPseudograph<ConditionalState,ConditionalEdge> graph = new DirectedPseudograph<>(ConditionalEdge.class);
        BiFunction<String, Map<String, Attribute>,ConditionalState> factoryState = (name,attributes) -> 
        {
            Attribute attr = attributes.get("feature");
            String value = attr.getValue();
            String[] features = value.split("\\|");
            if (features[0].equals("True")){
                return new ConditionalState(name,new String[0]);
            }
            return new ConditionalState(name,features);
        };
        importGraph.setVertexWithAttributesFactory(factoryState);

        Function<Map<String, Attribute>, ConditionalEdge> factoryEdge = attributes -> 
        {
            Attribute attr = attributes.get("feature");
            String value = attr.getValue();
            String[] features = value.split("\\|");

            Attribute attrLabel = attributes.get("label");
            String label = attrLabel.getValue();
            return new ConditionalEdge(features,label);
        };
        importGraph.setEdgeWithAttributesFactory(factoryEdge);
        // File myObj = new File("../FFSM_diff/dot-files/bowling.dot");
        File myObj = new File("../FFSM_diff/algorithm/out.dot");
        try {
            FileReader myReader = new FileReader(myObj);
            importGraph.importGraph(graph, myReader);
            System.out.println(graph.edgeSet()); 
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }

    }

}
