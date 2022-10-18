# Family-based fingerprinting
With this repository it is possible to actively or passively fingerprint a family-model. Here at first one can create a family-model with the `FFSM_diff` algorithm. This algorithm will create a Featured Finte State Machine were the features are the represented by the variant number. This model can be visualized by the `visualizer`.

To actually start fingerprinting, the `fingerprinter` can be used. Here the FFSM model is inputted together with the option of actively or passively fingerprinting. The fingerprinter will then output the set of possible variants.

