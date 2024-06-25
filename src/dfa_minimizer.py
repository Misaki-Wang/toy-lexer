from .fsa import FSA

# 最小化DFA的类
class _Minimizer:
    # 最小化方法
    def minimize(self, dfa: FSA, final_sets):
        self.dfa = dfa
        self.final_sets = final_sets
        self.affect = [[list() for j in range(len(self.dfa.states))]
                       for i in range(len(self.dfa.states))]
        self.combinable = [[True] * len(self.dfa.states)
                           for i in range(len(self.dfa.states))]
        self.mark_uncombinable()  # 标记不可合并的状态对
        self.calculate_dependency()  # 计算依赖关系
        new_states, to_new_state = self.relabel()  # 重新标记状态
        return self.build_min_dfa(new_states, to_new_state)  # 构建最小化DFA

    # 标记不可合并的状态对
    def mark_uncombinable(self):
        final_states = set()
        for final_set in self.final_sets:
            final_states.update(final_set)
        nonfinal_states = set(range(len(self.dfa.states))) - final_states
        uncombinable_sets = list(self.final_sets)
        uncombinable_sets.append(nonfinal_states)

        for x in range(len(uncombinable_sets)):
            x_set = uncombinable_sets[x]
            for y in range(x + 1, len(uncombinable_sets)):
                y_set = uncombinable_sets[y]
                for x_elem in x_set:
                    for y_elem in y_set:
                        if x_elem > y_elem:
                            self.combinable[y_elem][x_elem] = False
                        else:
                            self.combinable[x_elem][y_elem] = False

    # 标记状态对为不可合并
    def mark(self, i, j):
        if self.combinable[i][j] is False:
            return

        self.combinable[i][j] = False
        for x, y in self.affect[i][j]:
            self.mark(x, y)

    # 处理状态对，检查其依赖关系
    def process_state(self, x, y):
        x_edges = dict([(t.val, t.dst) for t in self.dfa.states[x].edges])
        y_edges = dict([(t.val, t.dst) for t in self.dfa.states[y].edges])
        if x_edges.keys() != y_edges.keys():
            self.mark(x, y)
            return

        dependency = list()
        for val, x_edge in x_edges.items():
            x_dst = x_edges[val]
            y_dst = y_edges[val]
            if x_dst == y_dst:
                continue
            if x_dst > y_dst:
                x_dst, y_dst = y_dst, x_dst
            if self.combinable[x_dst][y_dst]:
                dependency.append((x_dst, y_dst))
            else:
                self.mark(x, y)
                return

        for x_dst, y_dst in dependency:
            self.affect[x_dst][y_dst].append((x, y))

    # 计算依赖关系
    def calculate_dependency(self):
        for i in range(len(self.dfa.states)):
            for j in range(i + 1, len(self.dfa.states)):
                self.process_state(i, j)

    # 重新标记状态
    def relabel(self):
        processed = [False] * len(self.dfa.states)
        to_new_state = [-1] * len(self.dfa.states)
        new_states = list()
        for i in range(len(self.dfa.states)):
            if processed[i]:
                continue
            processed[i] = True
            new_states.append({i})
            to_new_state[i] = len(new_states) - 1
            for j in range(i + 1, len(self.dfa.states)):
                if processed[j]:
                    continue
                if self.combinable[i][j]:
                    processed[j] = True
                    new_states[-1].add(j)
                    to_new_state[j] = len(new_states) - 1
        return new_states, to_new_state

    # 构建最小化的DFA
    def build_min_dfa(self, new_states, to_new_state):
        dfa = FSA()
        for i in range(len(new_states) - 1):
            dfa.add_state()

        new_final_sets = [set() for i in range(len(self.final_sets))]
        for src_idx, old_states in enumerate(new_states):
            # 标记新状态是否为终止状态
            for final_set_index, final_set in enumerate(self.final_sets):
                if old_states.issubset(final_set):
                    new_final_sets[final_set_index].add(src_idx)
                    dfa.add_final(src_idx)
            # 添加边
            for edge in self.dfa.states[tuple(old_states)[0]].edges:
                dfa.add_edge(src_idx, to_new_state[edge.dst], edge.val)

        return dfa, new_final_sets

# 最小化DFA的外部接口函数
def minimize(dfa: FSA, final_sets=None):
    if final_sets is None:
        return _Minimizer().minimize(dfa, (set(dfa.finals),))[0]
    return _Minimizer().minimize(dfa, final_sets)

# 主函数，用于从命令行解析正则表达式并进行NFA到DFA的转换和最小化
def main():
    import sys
    import regex
    import nfa_to_dfa
    from utils import get_dot_file_path

    # 从命令行参数解析正则表达式
    nfa = regex.parse(sys.argv[1])
    # 将NFA保存为DOT文件
    nfa_dot_path = get_dot_file_path('nfa.dot')
    nfa.dump(open(nfa_dot_path, 'w'))

    # 将NFA转换为DFA
    dfa = nfa_to_dfa.convert(nfa)
    # 将DFA保存为DOT文件
    dfa_dot_path = get_dot_file_path('dfa.dot')
    dfa.dump(open(dfa_dot_path, 'w'))

    # 最小化DFA
    mindfa = minimize(dfa)
    # 将最小化DFA保存为DOT文件
    mindfa_dot_path = get_dot_file_path('mindfa.dot')
    mindfa.dump(open(mindfa_dot_path, 'w'))


if __name__ == '__main__':
    main()

"""
Hopcroft DFA 最小化算法，其核心思想是通过合并等价状态来减少 DFA 的状态数量。

Hopcroft DFA 最小化算法
Hopcroft 算法是一种高效的 DFA 最小化算法，其时间复杂度为 
O(nlogn)，其中 n 是 DFA 的状态数。算法的核心是通过分割和细分状态集合来识别等价状态。
该算法的主要步骤包括：

初始分割：
    将所有状态分成终止状态和非终止状态两个集合。
    初始化一个工作列表，用于存储待处理的状态对。

细分集合：
    通过检查输入符号下的转换，将状态集合进一步细分。
    每次选择一个状态对，如果它们在某个输入符号下转移到不同的集合，则将其细分。

合并等价状态：
    根据细分后的状态集合，合并等价状态，并构建最小化后的 DFA。
"""