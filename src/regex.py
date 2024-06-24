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
            if self.peek() == chr(0) or self.peek() in self.FORBIDDEN_CHAR:
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
