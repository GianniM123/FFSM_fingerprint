from copy import deepcopy

from aalpy.SULs.AutomataSUL import MealySUL
from base.fingerprint.active.CPDS import CPDS


class Simulator:
    
    def __init__(self, pds : CPDS) -> None:
        self.pds = pds

      
    def _pds_fingerprint(self, sul : MealySUL) -> set[str]:
        self.total_queries = []
        if self.pds.pds is not None:
            pds = deepcopy(self.pds.pds) #list[tuple[set[str],list[tuple[str,str]]]]
            for input, _ in self.pds.pds[0][1]:
                output = sul.step(input)
                self.total_queries.append((input,output))
                to_remove = []
                for i in range(0,len(pds)):
                    iin, out = pds[i][1].pop(0)
                    if input != iin or out != str(output):
                        to_remove.append(pds[i])
                for i in to_remove:
                    pds.remove(i)
            return pds[0][0]

        else:
            return set()


    def fingerprint_system(self, sul : MealySUL) -> set[str]:
        # features = self._do_random_input(self.hdt.root,sul)
        features = self._pds_fingerprint(sul)
        print(self.total_queries)
        return features


