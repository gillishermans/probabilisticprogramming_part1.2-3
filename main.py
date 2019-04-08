from problog.program import PrologString
from problog.formula import LogicFormula, LogicDAG
from problog.logic import Term
from problog.ddnnf_formula import DDNNF
from problog.cnf_formula import CNF
from problog.tasks import sample
from problog import get_evaluatable
import random

class Fact:
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name

    def query(self):
        return "query("+self.name+"). "

p_without_evidence = PrologString("""
increaseOsteoblasts :- calcium.
0.5::\+increaseOsteoblasts :- calcium, bispho.
reduceOsteoclasts :- bispho.
1.0::\+reduceOsteoclasts :- calcium , bispho.
osteoprosis :- initialOsteoprosis.
0.85::\+osteoprosis :- reduceOsteoclasts.   % Bisphosphonates
0.15::\+osteoprosis :- increaseOsteoblasts. % Calcium
% Prior probabilities
0.5::calcium. 0.5::bispho. 0.5::initialOsteoprosis.
% Query probability of effect
query(osteoprosis).
query(calcium).
query(bispho).
query(initialOsteoprosis).
""")

p_clean = """
increaseOsteoblasts :- calcium.
0.5::\+increaseOsteoblasts :- calcium, bispho.
reduceOsteoclasts :- bispho.
1.0::\+reduceOsteoclasts :- calcium , bispho.
osteoprosis :- initialOsteoprosis.
0.85::\+osteoprosis :- reduceOsteoclasts.   % Bisphosphonates
0.15::\+osteoprosis :- increaseOsteoblasts. % Calcium
% Prior probabilities
0.5::calcium. 0.5::bispho. 0.5::initialOsteoprosis.
"""

def create_interpretations(p, n):
        result = sample.sample(p, n, format='dict')
        resultNew  = []
        for i in range(n):
                interpr = next(result)
                toRemove = []
                for j in interpr:
                        if random.uniform(0, 1) <= 0.3:
                                toRemove.append(j)
                for j in toRemove:
                        dict.pop(interpr, j)
                resultNew.append(interpr)
        return resultNew

def probability(fact,interpretation):
        problog = p_clean+evidence(fact,interpretation)+fact.query()
        query = PrologString(problog)
        eval = get_evaluatable().create_from(query).evaluate()
        for key,val in eval.items():
                return val

def evidence(fact,interpretation):
        add = ""
        for j in interpretation:
                s = Term.__str__(j)
                if s != fact.name:
                        s2 = bool.__str__(dict.get(interpretation, j)).lower()
                        add = add + "evidence("+s+","+s2+"). "
        return add

def estimate_parameters(n):
        interpretations = create_interpretations(p_without_evidence, n)

        #create list of facts
        facts = []
        facts.append(Fact("bispho"))
        facts.append(Fact("calcium"))
        facts.append(Fact("initialOsteoprosis"))
        facts.append(Fact("osteoprosis"))
        facts.append(Fact("reduceOsteoclasts"))
        facts.append(Fact("increaseOsteoblasts"))
        for fact in facts:
                pn = 0
                for interpr in interpretations:
                        pn = pn + probability(fact,interpr) #probability of fact after interpr
                pn = pn/n
                print(fact.name)
                print(pn)

#From https://dtai.cs.kuleuven.be/problog/tutorial/advanced/01_python_interface.html
def main():
        p = PrologString("""
        increaseOsteoblasts :- calcium.
        0.5::\+increaseOsteoblasts :- calcium, bispho.
        reduceOsteoclasts :- bispho.
        1.0::\+reduceOsteoclasts :- calcium , bispho.
        osteoprosis :- initialOsteoprosis.
        0.85::\+osteoprosis :- reduceOsteoclasts.   % Bisphosphonates
        0.15::\+osteoprosis :- increaseOsteoblasts. % Calcium
        % Prior probabilities
        0.5::calcium. 0.5::bispho. 0.5::initialOsteoprosis.
        % Query probability of effect
        evidence(initialOsteoprosis, true).
        evidence(calcium, true).
        evidence(bispho, false).
        query(osteoprosis).
        """)

        #1.3: Create the CNF of the problog
        lf = LogicFormula.create_from(p,avoid_name_clash=True, keep_order=True, label_all=True)  # ground the program
        print("Ground program")
        print(LogicFormula.to_prolog(lf))
        dag = LogicDAG.create_from(lf,avoid_name_clash=True, keep_order=True, label_all=True)  # break cycles in the ground program
        cnf = CNF.create_from(dag)  # convert to CNF
        print(CNF.to_dimacs(cnf))
        ddnnf = DDNNF.create_from(cnf)  # compile CNF to ddnnf
        test = DDNNF.get_weights(ddnnf)
        print(test)
        print(ddnnf.evaluate())

        #3.1: Create 4 interpretations
        print("--Create 4 interpretations--")
        interpretations = create_interpretations(p_without_evidence, 4)
        for i in interpretations: print(i)

        #3.2: Create 100, 1000, 10000 interpretations and estimate p_n
        print("--Estimate parameters--")
        estimate_parameters(100)
        #estimate_parameters(1000)
        #estimate_parameters(10000)

if __name__ == '__main__':
        main()



