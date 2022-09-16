package com.thesis.ffsm;


public class ConditionalState {

    private String name;
    private String[] features;

    public ConditionalState(String aName, String[] aFeatures) {
        name = aName;
        features = aFeatures;
    }
    

    @Override
    public String toString()
    {
        String returnString ="(" + name + ", features: ";
        for (int i = 0; i < features.length; ++i) {
            returnString += features[i];
            if (i != (features.length-1)){
                returnString += ",";
            }
        }
        returnString += ")";
        return returnString ;
    }
}
