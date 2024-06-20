import unittest
from src.fsa import State, Edge, FSA
from src.regex import parse
from src.nfa_to_dfa import convert as nfa_to_dfa_convert
from src.dfa_minimizer import minimize as dfa_minimizer
import os

class TestFSA(unittest.TestCase):
    
    def test_state_initialization(self):
        state = State()
        self.assertEqual(state.edges, [])
    
    def test_edge_initialization(self):
        edge = Edge(1, 'a')
        self.assertEqual(edge.dst, 1)
        self.assertEqual(edge.val, 'a')
    
    def test_fsa_add_state(self):
        fsa = FSA()
        initial_state_count = len(fsa.states)
        fsa.add_state()
        self.assertEqual(len(fsa.states), initial_state_count + 1)
    
    def test_fsa_add_final_state(self):
        fsa = FSA()
        initial_state_count = len(fsa.states)
        initial_final_count = len(fsa.finals)
        fsa.add_final_state()
        self.assertEqual(len(fsa.states), initial_state_count + 1)
        self.assertEqual(len(fsa.finals), initial_final_count + 1)
    
    def test_fsa_add_edge(self):
        fsa = FSA()
        src = fsa.add_state()
        dst = fsa.add_state()
        fsa.add_edge(src, dst, 'a')
        self.assertEqual(fsa.states[src].edges[0].dst, dst)
        self.assertEqual(fsa.states[src].edges[0].val, 'a')
    
    def test_fsa_combine(self):
        fsa1 = FSA()
        state1 = fsa1.add_state()
        fsa1.add_final(state1)
        
        fsa2 = FSA()
        state2 = fsa2.add_state()
        fsa2.add_final(state2)
        
        initial_state_count = len(fsa1.states)
        fsa1.combine(fsa2)
        
        self.assertEqual(len(fsa1.states), initial_state_count + len(fsa2.states))
        self.assertEqual(len(fsa1.finals), 2)


class TestRegex(unittest.TestCase):

    def test_regex_parse(self):
        regex_str = 'ab'
        nfa = parse(regex_str)
        self.assertIsInstance(nfa, FSA)
        self.assertGreater(len(nfa.states), 0)

class TestNFAtoDFA(unittest.TestCase):

    def test_nfa_to_dfa(self):
        regex_str = 'ab'
        nfa = parse(regex_str)
        dfa = nfa_to_dfa_convert(nfa)
        self.assertIsInstance(dfa, FSA)
        self.assertGreater(len(dfa.states), 0)

class TestDFAMinimizer(unittest.TestCase):

    def test_dfa_minimizer(self):
        regex_str = 'ab'
        nfa = parse(regex_str)
        dfa = nfa_to_dfa_convert(nfa)
        minimized_dfa = dfa_minimizer(dfa)
        self.assertIsInstance(minimized_dfa, FSA)
        self.assertGreater(len(minimized_dfa.states), 0)
        self.assertLessEqual(len(minimized_dfa.states), len(dfa.states))

if __name__ == '__main__':
    unittest.main()
