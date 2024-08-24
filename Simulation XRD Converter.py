import tkinter as tk
from tkinter import filedialog, simpledialog
import os

# 定义全局变量
output_path = None


def on_select_file():
    global output_path
    file_path = filedialog.askopenfilename(
        title='选择.int文件',
        filetypes=[('INT files', '*.int')]
    )
    if file_path:
        input_dir = os.path.dirname(file_path)
        output_filename = os.path.splitext(os.path.basename(file_path))[0]+ '-Simulation' + '.txt'
        output_path = os.path.join(input_dir, output_filename)

        # 弹出对话框获取用户输入的角度范围
        min_angle, max_angle = simpledialog.askstring("输入角度范围", "请输入最小角度和最大角度，用空格分隔:").split()
        try:
            min_angle, max_angle = float(min_angle), float(max_angle)
            process_file(file_path, output_path, min_angle, max_angle)
        except ValueError:
            print("输入的角度值无效，请输入数字。")


def process_file(input_path, output_path, min_angle, max_angle):
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        next(infile)  # 跳过第一行
        next(infile)  # 跳过第二行
        for line in infile:
            columns = line.split()
            angle = float(columns[0])
            if min_angle <= angle <= max_angle:
                columns_without_third = columns[:2] + columns[3:]
                outfile.write(' '.join(columns_without_third) + '\n')

    print(f'文件已处理并保存在: {output_path}')


# 创建主窗口
root = tk.Tk()
root.title('Simulation XRD Converter Xu')
root.geometry("400x50")
# 创建一个按钮，当点击时会触发选择文件的操作
select_button = tk.Button(root, text='选择文件', command=on_select_file)
select_button.pack()

# 运行主循环
root.mainloop()