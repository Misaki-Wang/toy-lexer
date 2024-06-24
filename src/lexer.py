from .fsa import FSA

# 词法分析器工厂类，用于根据给定的规则列表构建 DFA
class LexerFactory:
    def __init__(self, rule_list):
        self._build_dfa(rule_list)  # 初始化时构建 DFA

    # 根据规则列表构建 DFA
    def _build_dfa(self, rule_list):
        nfa = FSA()  # 创建一个新的 NFA
        nfa_final_sets = list()  # 用于存储每个正则表达式的终止状态集合
        
        # 遍历规则列表，构建对应的 NFA 并合并到一个总的 NFA 中
        for regex, category in rule_list:
            regex_nfa = FSA.from_regex(regex)  # 将正则表达式转换为 NFA
            last_pos = len(nfa.finals)  # 记录当前 NFA 的终止状态数量
            new_start = nfa.combine(regex_nfa)  # 合并新构建的 NFA
            nfa.add_edge_epsilon(0, new_start)  # 添加 epsilon 边连接新 NFA 的起始状态
            nfa_final_sets.append(set(nfa.finals[last_pos:]))  # 记录新 NFA 的终止状态集合

        from nfa_to_dfa import convert
        dfa, dfa_final_sets = convert(nfa, nfa_final_sets)  # 将 NFA 转换为 DFA

        from dfa_minimizer import minimize
        dfa, dfa_final_sets = minimize(dfa, dfa_final_sets)  # 最小化 DFA

        # 将基于边的状态转换转换为基于值的状态转换
        transitions = [dict() for i in range(len(dfa.states))]
        for src_index, state in enumerate(dfa.states):
            src_transition = transitions[src_index]
            for edge in state.edges:
                src_transition[edge.val] = edge.dst
        self._transitions = transitions  # 保存状态转换

        # 建立状态到对应类别的映射
        final_mapping = [None] * len(dfa.states)
        for index, final_set in enumerate(dfa_final_sets):
            for state in final_set:
                final_mapping[state] = rule_list[index][1]
        self._final_mapping = final_mapping  # 保存状态到类别的映射

    # 创建词法分析器实例
    def create_lexer(self, buf: str):
        return Lexer(self._transitions, self._final_mapping, buf)

# 词法分析器类，用于分析输入的字符串
class Lexer:
    def __init__(self, transitions: list, final_mapping: list, buf: str):
        self._transitions = transitions  # 状态转换表
        self._final_mapping = final_mapping  # 状态到类别的映射
        self.reset(buf)  # 初始化输入缓冲区

    # 重置词法分析器
    def reset(self, buf: str):
        self._buf = buf  # 输入缓冲区
        self._pos = 0  # 当前读取位置
        self._len = len(buf)  # 输入缓冲区长度

    # 获取下一个词法单元
    def next(self):
        state = 0  # 初始状态
        success_pos = self._pos  # 成功匹配的位置
        success_category = None  # 成功匹配的类别
        for pos in range(self._pos, self._len):
            val = self._buf[pos]
            if val in self._transitions[state]:
                state = self._transitions[state][val]
                if self._final_mapping[state] is not None:
                    success_pos = pos + 1
                    success_category = self._final_mapping[state]
            else:
                break

        string = self._buf[self._pos:success_pos]  # 匹配到的字符串
        self._pos = success_pos  # 更新当前位置
        return success_category, string  # 返回匹配的类别和字符串

# 主函数，用于测试词法分析器
def main():
    import sys
    rules = (('ab|ac', 'KEYWORD'), ('[a-c]+', 'IDENT'), (' +', 'SPACE'))
    lexer_factory = LexerFactory(rules)  # 创建词法分析器工厂
    lexer = lexer_factory.create_lexer(sys.argv[1])  # 创建词法分析器实例
    while True:
        cat, string = lexer.next()  # 获取下一个词法单元
        print(cat, repr(string))  # 打印词法单元类别和对应的字符串
        if not cat:
            return  # 如果没有匹配的类别，则退出

if __name__ == '__main__':
    main()
