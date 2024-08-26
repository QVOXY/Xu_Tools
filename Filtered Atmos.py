def filter_atoms(file_path, x_range, y_range, z_range):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # 读取元素种类和数量
    elements = lines[5].split()
    element_numbers = list(map(int, lines[6].split()))
    element_delete_numbers = [0] * len(elements)

    # 初始化新的文件内容
    new_lines = lines[:8]

    # 遍历原子坐标
    current_element_index = 0
    current_element_count = 0
    for line in lines[8:]:
        coords = list(map(float, line.split()))
        if x_range[0] <= coords[0] <= x_range[1] and \
           y_range[0] <= coords[1] <= y_range[1] and \
           z_range[0] <= coords[2] <= z_range[1]:
            new_lines.append(line)
        else:
            element_delete_numbers[current_element_index] += 1

        current_element_count += 1
        if current_element_count >= element_numbers[current_element_index]:
            current_element_index += 1
            current_element_count = 0

    # 更新原子数量
    new_element_numbers = [element_numbers[i] - element_delete_numbers[i] for i in range(len(elements))]
    new_lines[6] = ' '.join(map(str, new_element_numbers)) + '\n'

    # 输出结果
    with open('filtered_' + file_path, 'w') as new_file:
        new_file.writelines(new_lines)
if __name__ == "__main__":
    file_path = 'MIL-100.vasp'  # 输入文件路径
    x_range = list(map(float, input("输入x坐标选择范围（例如：0 0.5）：").split()))
    y_range = list(map(float, input("输入y坐标选择范围（例如：0 0.5）：").split()))
    z_range = list(map(float, input("输入z坐标选择范围（例如：0 0.5）：").split()))

    filter_atoms(file_path, x_range, y_range, z_range)
