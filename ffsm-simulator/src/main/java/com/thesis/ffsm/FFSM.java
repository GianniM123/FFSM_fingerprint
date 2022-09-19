package com.thesis.ffsm;

import java.io.File;
import java.io.FileReader;
import java.util.Map;
import java.util.function.*;

import org.jgrapht.graph.DirectedPseudograph;
import org.jgrapht.nio.dot.DOTImporter;
import org.jgrapht.nio.Attribute;


public class FFSM extends DirectedPseudograph<ConditionalState,ConditionalEdge> {
    

    public FFSM(String file) {
        super(ConditionalEdge.class);
        readGraph(file);
    }

    private void readGraph(String file){
        DOTImporter<ConditionalState,ConditionalEdge> importGraph = new DOTImporter<>();
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

        File dotFile = new File(file);

        try {
            FileReader dotReader = new FileReader(dotFile);
            importGraph.importGraph(this, dotReader);
        } catch (Exception e) {
            System.out.println(e.getMessage());
        }
    }

}
