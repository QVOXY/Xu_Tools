import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox

def extract_data(input_file, start_angle, end_angle):
    # 根据起始角度和终止角度生成输出文件名
    output_file = f"{input_file.rstrip('.txt')}({start_angle}-{end_angle}).txt"

    # 打开输入文件和输出文件
    with open(input_file, 'r') as infile, open(output_file, 'w') as outfile:
        # 读取所有行
        lines = infile.readlines()

        # 遍历所有行
        for line in lines:
            # 忽略掉以星号开头的元数据行
            if line.startswith('*'):
                continue

            # 分割角度和强度数据
            parts = line.split()
            try:
                angle = float(parts[0])  # 第一列是角度
            except (ValueError, IndexError):
                continue  # 如果转换失败或格式不正确，跳过这一行

            # 检查角度是否在指定的范围内
            if start_angle <= angle <= end_angle:
                # 如果在范围内，写入输出文件
                outfile.write(line)
# 用于处理用户输入并调用extract_data函数的函数
def process_data():
    input_file = entry_file.get()
    try:
        start_angle = float(entry_start.get())
        end_angle = float(entry_end.get())
    except ValueError:
        messagebox.showerror("错误", "请输入有效的数字作为角度。")
        return

    if start_angle >= end_angle:
        messagebox.showerror("错误", "起始角度必须小于终止角度。")
        return

    # 调用原始的函数来处理数据
    extract_data(input_file, start_angle, end_angle)
    messagebox.showinfo("完成", "数据提取完成。")

# 创建主窗口
root = tk.Tk()
root.title("数据提取工具")

# 创建输入文件的输入框和浏览按钮
label_file = tk.Label(root, text="输入文件:")
entry_file = tk.Entry(root)
button_browse = tk.Button(root, text="浏览", command=lambda: entry_file.insert(0, filedialog.askopenfilename()))

# 创建起始角度和终止角度的输入框
label_start = tk.Label(root, text="起始角度:")
entry_start = tk.Entry(root)
label_end = tk.Label(root, text="终止角度:")
entry_end = tk.Entry(root)

# 创建处理数据的按钮
button_process = tk.Button(root, text="提取数据", command=process_data)

# 布局
label_file.grid(row=0, column=0, sticky="ew", padx=10, pady=5)
entry_file.grid(row=0, column=1, padx=10, pady=5)
button_browse.grid(row=0, column=2, padx=10, pady=5)

label_start.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
entry_start.grid(row=1, column=1, padx=10, pady=5)

label_end.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
entry_end.grid(row=2, column=1, padx=10, pady=5)

button_process.grid(row=3, column=0, columnspan=3, padx=10, pady=5)

# 运行主循环
root.mainloop()
