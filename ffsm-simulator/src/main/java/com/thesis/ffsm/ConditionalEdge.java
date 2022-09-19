package com.thesis.ffsm;

import org.jgrapht.graph.*;

public class ConditionalEdge extends DefaultEdge {
    
    private String[] features;
    private String input;
    private String output;

    public ConditionalEdge(String[] aFeatures, String label){
        features = aFeatures;
        String[] inputOutput = label.split("/");
        input = inputOutput[0];
        output = inputOutput[1];
    }

    @Override
    public String toString()
    {
        String featureString = "";
        for (int i = 0; i < features.length; ++i) {
            featureString += features[i];
            if (i != (features.length-1)){
                featureString += ",";
            }
        }

        return "((" + getSource() + " : " + getTarget() + "), (" + input + " / " + output + "), features: " + featureString + ")";
    }
}
