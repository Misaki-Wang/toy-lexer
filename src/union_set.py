class UnionSet:
    def __init__(self, num):
        # 初始化并查集，_arr[i] 表示元素 i 所属的集合的根
        self._arr = [i for i in range(num)]

    def find(self, i):
        # 查找元素 i 所属集合的根，并进行路径压缩
        while self._arr[i] != self._arr[self._arr[i]]:
            self._arr[i] = self._arr[self._arr[i]]  # 路径压缩
        return self._arr[i]

    def union(self, i, j):
        # 合并两个集合
        self._arr[self.find(i)] = self.find(j)

    def to_closure(self):
        # 将并查集转换为闭包形式
        closure = [None] * len(self._arr)
        for i in range(len(self._arr)):
            root = self.find(i)  # 查找元素 i 的根
            if closure[root] is None:
                closure[root] = {i}  # 如果根节点还没有对应的集合，则创建一个新的集合
            else:
                closure[root].add(i)  # 否则将元素添加到对应的集合中
            closure[i] = closure[root]  # 将当前元素指向其根节点的集合
        return closure
