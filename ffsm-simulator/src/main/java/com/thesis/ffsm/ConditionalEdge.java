package com.thesis.ffsm;

import org.jgrapht.graph.*;

public class ConditionalEdge extends DefaultEdge {
    
    private String[] features;

    public ConditionalEdge(String[] aFeatures){
        features = aFeatures;
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

        return "(" + getSource() + " : " + getTarget() + ", features: " + featureString + ")";
    }
}
