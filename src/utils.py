import os
import shutil

# 指定DOT和图像文件夹的路径
DOT_FOLDER = './res/dot'
IMAGE_FOLDER = './res/img'

# 如果目录不存在，则创建目录
os.makedirs(DOT_FOLDER, exist_ok=True)
os.makedirs(IMAGE_FOLDER, exist_ok=True)

# 获取DOT文件的完整路径
def get_dot_file_path(filename):
    return os.path.join(DOT_FOLDER, filename)

# 获取图像文件的完整路径
def get_image_file_path(filename):
    return os.path.join(IMAGE_FOLDER, filename)

# 清空指定目录
def clear_directory(directory):
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)  # 删除文件或符号链接
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)  # 删除目录

# 将自动机对象输出为DOT文件（修正后的版本）
def dump(automaton, filename):
    with open(filename, 'w') as file:
        file.write('digraph G {\n')
        file.write('rankdir=LR;\n')  # 从左到右的布局
        file.write('node [shape=circle, fontname="Helvetica", fontsize=12];\n')
        
        # 写入状态节点，终止状态用双圈表示
        for state_index, state in enumerate(automaton.states):
            shape = 'doublecircle' if state_index in automaton.finals else 'circle'
            file.write(f'{state_index} [label="{state_index}", shape={shape}];\n')
        
        # 写入带标签的转换边
        for state_index, state in enumerate(automaton.states):
            for edge in state.edges:
                label = 'ε' if edge.val == 0 else edge.val  # epsilon边用ε表示
                file.write(f'{state_index} -> {edge.dst} [label="{label}"];\n')
        
        file.write('}\n')
