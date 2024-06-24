from copy import deepcopy

# 边类，表示从一个状态到另一个状态的转换
class Edge:
    def __init__(self, dst, val):
        self.val = val  # 边的值
        self.dst = dst  # 目标状态

# 状态类，表示有限状态自动机中的一个状态
class State:
    def __init__(self):
        self.edges = list()  # 边的列表

# 有限状态自动机类
class FSA:
    def __init__(self):
        self.finals = list()  # 终止状态的索引列表
        self.states = [State()]  # 状态的列表，初始包含一个状态

    # 添加一个终止状态
    def add_final(self, index):
        self.finals.append(index)

    # 添加一个新状态，并返回其索引
    def add_state(self) -> int:
        self.states.append(State())
        return len(self.states) - 1

    # 添加一个新的终止状态，并返回其索引
    def add_final_state(self) -> int:
        state = self.add_state()
        self.add_final(state)
        return state

    # 添加一条边，从src状态到dst状态，边的值为val
    def add_edge(self, src, dst, val):
        self.states[src].edges.append(Edge(dst, val))

    # 添加一条epsilon边（值为0），从src状态到dst状态
    def add_edge_epsilon(self, src, dst):
        self.add_edge(src, dst, 0)

    # 合并另一个FSA到当前FSA，返回偏移量
    def combine(self, fsa) -> int:
        offset = len(self.states)  # 当前状态数量作为偏移量
        tmpfsa = fsa.duplicate()  # 复制要合并的FSA
        for state in tmpfsa.states:
            for edge in state.edges:
                edge.dst += offset  # 更新目标状态的索引
        for idx in range(len(tmpfsa.finals)):
            tmpfsa.finals[idx] += offset  # 更新终止状态的索引
        self.states.extend(tmpfsa.states)  # 扩展状态列表
        self.finals.extend(tmpfsa.finals)  # 扩展终止状态列表
        return offset

    # 复制当前的FSA，返回一个深拷贝
    def duplicate(self):
        return deepcopy(self)

    # 将FSA的结构输出到文件，格式为Graphviz的dot文件
    def dump(self, f):
        f.write('digraph {\n')
        for final in self.finals:
            f.write('\t' + str(final) + '[shape="box"]\n')  # 输出终止状态

        for state_index, state in enumerate(self.states):
            for edge in state.edges:
                disp = '(eps)' if edge.val == 0 else edge.val  # 边的标签
                f.write('\t' + str(state_index) + ' -> ' + str(edge.dst)
                        + ' [label="' + disp + '"];\n')  # 输出状态和边
        f.write('}\n')

    # 从正则表达式构建FSA
    def from_regex(regex: str):
        from regex import parse  # 导入正则表达式解析模块
        from nfa_to_dfa import convert  # 导入NFA到DFA的转换模块
        return convert(parse(regex))  # 解析正则表达式并转换为FSA
