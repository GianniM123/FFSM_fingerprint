package com.thesis.ffsm;

public class App 
{
    public static void main( String[] args )
    {
        if (args.length >= 1){
            FFSM ffsm = new FFSM(args[0]);
            System.out.println(ffsm.toString());
        }


    }

}
