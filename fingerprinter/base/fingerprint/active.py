from aalpy.SULs.AutomataSUL import MealySUL
from base.FFSM import FFSM


class Simulator:
    
    def __init__(self, ffsm : FFSM) -> None:
        self.ffsm = ffsm


    def fingerprint_system(self, sul : MealySUL) -> str:
        pass

