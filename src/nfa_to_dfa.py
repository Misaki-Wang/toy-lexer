from .fsa import FSA
from collections import defaultdict

# NFA到DFA的转换类
class _NFAToDFA:
    # 转换方法
    def convert(self, nfa: FSA, final_sets=None):
        self.nfa = nfa
        self.closure_array = self.init_closure()  # 初始化闭包数组
        set_graph = self.nfa_to_dfa_set_graph()  # 构建DFA集合图
        return self.dfa_set_graph_to_dfa(set_graph, final_sets)  # 将集合图转换为DFA

    # 初始化闭包数组
    def init_closure(self):
        result = [{i} for i in range(len(self.nfa.states))]  # 初始每个状态的闭包仅包含其自身
        changed = True
        while changed:
            changed = False
            for i in range(len(self.nfa.states)):
                closure = set(result[i])
                for edge in self.nfa.states[i].edges:
                    if edge.val == 0:  # 处理epsilon边
                        closure.update(result[edge.dst])
                if closure != result[i]:
                    result[i] = closure
                    changed = True
        return result

    # 获取状态集合的闭包
    def closure(self, states):
        if hasattr(states, '__next__'):
            result = set()
            for state in states:
                result |= self.closure_array[state]
            return result
        else:
            return self.closure_array[states]

    # 获取目标状态集合
    def get_dst_sets(self, src_states):
        result = defaultdict(set)  # result[val] = dst_states
        for state in src_states:
            for edge in self.nfa.states[state].edges:
                if edge.val != 0:
                    result[edge.val].update(self.closure(edge.dst))
        return result

    # 构建DFA的集合图
    def nfa_to_dfa_set_graph(self):
        set_graph = dict()  # set_graph[src_set][val] = dst_set

        set_new = {frozenset(self.closure(0))}
        while set_new:
            set_proc = set_new.pop()
            dst_sets = self.get_dst_sets(set_proc)
            set_graph[set_proc] = dst_sets
            for dst_set in dst_sets.values():
                frozen_dst_set = frozenset(dst_set)
                if frozen_dst_set not in set_graph:
                    set_new.add(frozen_dst_set)
        return set_graph

    # 调试用，打印集合图
    # def debug_print_set_graph(self, set_graph):
    #     for src, edges in set_graph.items():
    #         for val, dst in edges.items():
    #             print(set(src), val, set(dst))

    # 将集合图转换为DFA
    def dfa_set_graph_to_dfa(self, set_graph, final_sets):
        dfa = FSA()

        # 给集合打标签，确定DFA中的final_sets
        set_label = dict()
        new_final_sets = [set() for i in range(len(final_sets))]
        for index, state in enumerate(set_graph):
            for final_set_index, final_set in enumerate(final_sets):
                in_final = final_set.intersection(state)
                if len(in_final) == 0:
                    if 0 in state:
                        set_label[state] = 0
                    else:
                        set_label[state] = dfa.add_state()
                else:
                    if 0 in state:
                        set_label[state] = 0
                        dfa.add_final(0)
                        new_final_sets[final_set_index].add(0)
                    else:
                        new_state = dfa.add_final_state()
                        set_label[state] = new_state
                        new_final_sets[final_set_index].add(new_state)
                    # 高优先级的终止状态集已找到
                    break

        # 添加边
        for src_state_set, src_state in set_graph.items():
            for val, dst_state_set in src_state.items():
                src_label = set_label[frozenset(src_state_set)]
                dst_label = set_label[frozenset(dst_state_set)]
                dfa.add_edge(src_label, dst_label, val)

        return dfa, new_final_sets

# 外部接口函数，将NFA转换为DFA
def convert(nfa: FSA, final_sets=None):
    if final_sets is None:
        return _NFAToDFA().convert(nfa, (set(nfa.finals),))[0]
    return _NFAToDFA().convert(nfa, final_sets)

# 主函数，用于从命令行解析正则表达式并进行NFA到DFA的转换
def main():
    import sys
    import regex
    from utils import get_dot_file_path
    nfa = regex.parse(sys.argv[1])
    # 将NFA保存为DOT文件
    nfa_dot_path = get_dot_file_path('nfa.dot')
    nfa.dump(open(nfa_dot_path, 'w'))

    # 将NFA转换为DFA
    dfa = convert(nfa)
    # 将DFA保存为DOT文件
    dfa_dot_path = get_dot_file_path('dfa.dot')
    dfa.dump(open(dfa_dot_path, 'w'))

if __name__ == '__main__':
    main()

"""
基于经典的子集构造法（Subset Construction），也称为 Powerset Construction。通过构造新的状态和转换，
使每个 NFA 的状态集合对应 DFA 的一个状态，从而实现转换。

闭包计算（ε-Closure）：
    计算每个状态及其通过 ε 边（epsilon 边）能够到达的所有状态的集合。
    这一步确保 DFA 能够处理 NFA 中的 ε 转换。

状态转换（Transition）：
    对于每个新的 DFA 状态（由 NFA 状态的集合组成），计算它在每个输入符号下的转换。
    通过跟踪这些转换，构建 DFA 的状态和边。

处理终止状态（Final States）：
    如果 NFA 的任何终止状态包含在某个 DFA 状态中，则将该 DFA 状态标记为终止状态。

init_closure 遍历每个状态，计算其 epsilon 闭包，
    并不断更新直到所有状态的闭包都不再变化。
    
closure 获取一个状态集合的闭包，即通过 epsilon 边可以到达的所有状态。

get_dst_sets 计算从一个状态集合出发，通过特定字符到达的目标状态集合。

nfa_to_dfa_set_graph 构建状态集合图，表示从一个状态集合到另一个状态集合的转换关系。

dfa_set_graph_to_dfa 将状态集合图转换为实际的 DFA，包括打标签、标记终止状态、添加边等步骤。
"""