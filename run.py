import sys
import os
import argparse
from src import regex, nfa_to_dfa, dfa_minimizer
from src.utils import get_dot_file_path, get_image_file_path, clear_directory, dump

# Ensure the res/dot and res/png directories exist
os.makedirs('res/dot', exist_ok=True)
os.makedirs('res/img', exist_ok=True)

def parse_args():
    parser = argparse.ArgumentParser(description='Process regular expressions and generate finite automata.')
    parser.add_argument('regex', type=str, help='The regular expression to parse')
    parser.add_argument('conversion', choices=['minidfa', 'dfa', 'nfa'], help='Type of conversion to perform')
    parser.add_argument('--dot', action='store_true', help='Generate DOT files')
    parser.add_argument('--png', action='store_true', help='Generate PNG files')
    return parser.parse_args()

def main():
    args = parse_args()
    
    # Clear the output directories
    clear_directory('res/dot')
    clear_directory('res/img')
    
    # Parse the regular expression into an NFA
    nfa = regex.parse(args.regex)
    # Print attributes for debugging
    # print(f"NFA attributes: {nfa.__dict__}")
    
    if args.conversion in ['minidfa', 'dfa', 'nfa']:
        # Save the NFA to a DOT file if requested
        if args.dot:
            nfa_dot_path = get_dot_file_path('nfa.dot')
            # nfa.dump(open(nfa_dot_path, 'w'))
            dump(nfa, nfa_dot_path)
        
        if args.conversion in ['minidfa', 'dfa']:
            # Convert the NFA to a DFA
            dfa = nfa_to_dfa.convert(nfa)
            
            # Save the DFA to a DOT file if requested
            if args.dot:
                dfa_dot_path = get_dot_file_path('dfa.dot')
                # dfa.dump(open(dfa_dot_path, 'w'))
                dump(dfa, dfa_dot_path)
            
            if args.conversion == 'minidfa':
                # Minimize the DFA
                mindfa = dfa_minimizer.minimize(dfa)
                
                # Save the minimized DFA to a DOT file if requested
                if args.dot:
                    mindfa_dot_path = get_dot_file_path('mindfa.dot')
                    # mindfa.dump(open(mindfa_dot_path, 'w'))
                    dump(mindfa, mindfa_dot_path)
        
        # Optionally convert DOT files to PNG files
        if args.png:
            for dot_file in os.listdir('res/dot'):
                if dot_file.endswith('.dot'):
                    dot_path = get_dot_file_path(dot_file)
                    png_path = get_image_file_path(dot_file.replace('.dot', '.png'))
                    os.system(f'dot -Tpng {dot_path} -o {png_path}')

if __name__ == "__main__":
    main()
