from .fsa import FSA
# simple: char | range | '(' regexp ')'
#
# repeating: simple '*' 
#          | simple '+'
#          | simple '?'
#          | simple
#
# sequence: repeating
#         | repeating sequence
#
# regexp: sequence '|' regexp
#       | sequence

# 解析器类，用于将正则表达式解析为有限状态自动机（FSA）
class _Parser:
    FORBIDDEN_CHAR = "+*?|()[]"  # 禁止直接使用的字符

    # 解析正则表达式入口方法
    def parse(self, regex: str):
        self.pos = 0  # 当前解析位置
        self.regex = regex  # 正则表达式字符串
        self.maxpos = len(self.regex)  # 正则表达式的最大位置
        return self.parse_regexp()  # 解析正则表达式

    # 查看当前字符
    def peek(self):
        if self.pos < len(self.regex):
            return self.regex[self.pos]
        return chr(0)

    # 解析字符
    def parse_char(self):
        if self.peek() in self.FORBIDDEN_CHAR:
            raise SyntaxError("Unexpected symbol " + self.peek())

        char = self.regex[self.pos]
        if char == '\\':  # 处理转义字符
            char = {'r': '\r', 'n': '\n', 'v': '\v'}.get(
                self.regex[self.pos + 1], self.regex[self.pos + 1])
            self.pos += 1

        self.pos += 1
        return char

    # 解析字符范围
    def parse_range(self):
        if self.regex[self.pos] != '[':
            return None
        self.pos += 1

        fsa = FSA()
        final = fsa.add_final_state()

        while self.pos < self.maxpos:
            if self.peek() == ']':
                self.pos += 1
                return fsa
            char = self.parse_char()
            if self.peek() == '-':  # 处理字符范围
                self.parse_char()
                next_char = self.parse_char()
                if ord(next_char) >= ord(char):
                    for i in range(ord(char), ord(next_char) + 1):
                        fsa.add_edge(0, final, chr(i))
            else:
                fsa.add_edge(0, final, char)
        raise SyntaxError("Missing ]")

    # 解析简单表达式
    def parse_simple(self):
        # 处理 '(' regexp ')'
        if self.peek() == '(':
            pos = self.pos
            self.pos += 1
            if self.peek() == ')':
                self.pos += 1
            else:
                fsa = self.parse_regexp()
                if fsa:
                    if self.peek() != ')':
                        raise SyntaxError("Missing )")
                    else:
                        self.pos += 1
                        return fsa
                else:
                    self.pos = pos

        # 处理字符范围
        fsa = self.parse_range()
        if fsa:
            return fsa

        # 处理单个字符
        fsa = FSA()
        final = fsa.add_final_state()
        fsa.add_edge(0, final, self.parse_char())
        return fsa

    # 解析重复表达式
    def parse_repeating(self):
        subfsa = self.parse_simple()
        fsa = subfsa.duplicate()
        if self.peek() in "*?":
            fsa.add_edge_epsilon(0, fsa.finals[0])
        if self.peek() in "*+":
            fsa.add_edge_epsilon(fsa.finals[0], 0)
        if self.peek() in "*+?":
            self.pos += 1
        return fsa

    # 解析序列
    def parse_sequence(self):
        fsa = None
        while self.pos < self.maxpos:
            if self.peek() in '|)':
                return fsa
            subfsa = self.parse_repeating()
            if fsa:
                subfsa_begin = fsa.combine(subfsa)
                subfsa_end = fsa.finals.pop()
                fsa.add_edge_epsilon(fsa.finals[0], subfsa_begin)
                fsa.finals[0] = subfsa_end
            else:
                fsa = subfsa
        return fsa

    # 解析正则表达式
    def parse_regexp(self):
        fsa = FSA()
        final = fsa.add_final_state()

        while self.pos < self.maxpos:
            subfsa = self.parse_sequence()
            if subfsa is None:
                continue
            subfsa_begin = fsa.combine(subfsa)
            subfsa_end = fsa.finals.pop()
            fsa.add_edge_epsilon(0, subfsa_begin)
            fsa.add_edge_epsilon(subfsa_end, final)

            if self.peek() == '|':
                self.pos += 1
                continue
            if (self.peek() == chr(0) or    # chr(0) == NULL
                self.peek() in self.FORBIDDEN_CHAR):
                return fsa


        return fsa

# 外部接口函数，解析正则表达式并返回FSA
def parse(regex: str) -> FSA:
    parser = _Parser()
    return parser.parse(regex)

# 主函数，用于从命令行解析正则表达式并生成对应的FSA
def main():
    import sys
    from utils import get_dot_file_path
    fsa = parse(sys.argv[1])
    
    fsa_dot_path = get_dot_file_path('regex.dot')
    fsa.dump(open(fsa_dot_path, 'w'))

if __name__ == '__main__':
    main()

"""
递归下降解析（Recursive Descent Parsing）
递归下降解析是一种自顶向下的解析方法，广泛用于解析上下文无关文法。它使用一组递归函数来处理每个非终结符，并根据输入字符调用相应的函数，以实现整个输入串的解析。

具体实现

分解正则表达式的各个组成部分：
    简单表达式（simple）：包括单个字符、字符范围和括号中的子表达式。
    重复表达式（repeating）：包括简单表达式后面跟着 *、+ 或 ? 运算符。
    序列（sequence）：包括一个或多个重复表达式的串联。
    选择（regexp）：包括一个或多个序列之间使用 | 运算符的选择。

函数调用层次结构：
    parse_regexp 调用 parse_sequence
    parse_sequence 调用 parse_repeating
    parse_repeating 调用 parse_simple
    parse_simple 调用 parse_range
    parse_range 调用 parse_char
这种自顶向下的解析方法通过递归函数调用，逐步解析并处理正则表达式的各个组成部分。


Thompson 构造法（Thompson's Construction）
Thompson 构造法是一种将正则表达式转换为非确定性有限自动机（NFA）的经典算法。它通过构建基本的自动机，并组合这些基本自动机来表示正则表达式中的各种操作（如连接、选择和重复）。

具体实现

基本构造：
    单个字符：使用 parse_char 方法解析单个字符，并构建一个简单的 NFA，包含一个起始状态和一个终止状态，以及一个从起始状态到终止状态的字符边。
    字符范围：使用 parse_range 方法解析字符范围，并构建相应的 NFA，包含多个从起始状态到终止状态的字符边。

组合操作：
    重复操作：使用 parse_repeating 方法处理 *、+ 和 ? 运算符，通过添加 epsilon 边，将基本 NFA 扩展为支持重复的 NFA。
    顺序操作：使用 parse_sequence 方法处理字符的顺序排列，通过将多个 NFA 依次连接起来，构建顺序操作的 NFA。
    选择操作：使用 parse_regexp 方法处理选择运算符 |，通过构建新的起始状态和终止状态，并添加相应的 epsilon 边，将多个 NFA 组合为一个选择操作的 NFA。
通过这些基本构造和组合操作，Thompson 构造法实现了将正则表达式转换为等价的 NFA。
"""