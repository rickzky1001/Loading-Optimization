def read_nth_last_column(file_path, n):
    result = []  # 用于存储结果
    with open(file_path, 'r') as file:
        for line in file:
            line = line.strip()  # 去掉首尾空白字符
            if line and not line.startswith("Nodes"):  # 跳过标题行或其他不需要的行
                parts = line.split()  # 按空格分割
                if len(parts) >= n:  # 确保列数足够
                    nth_last_column = parts[-n]  # 提取倒数第 n 列
                    result.append(nth_last_column)
                else:
                    print(f"Warning: Line '{line}' has fewer than {n} columns.")
    return result
def string_to_num(string_list,tpe=float):
    return [tpe(string_list[i]) for i in range(len(string_list))]

import numpy as np
def visualize_log(file,lr_file):
    file_path='result/'+file+'.txt'
    lr_file_path='result/'+lr_file+'.txt'
    
    BestBd= string_to_num(read_nth_last_column(file_path, 4),tpe=float)
    Incumbent= read_nth_last_column(file_path, 5)
    Incumbent=np.array(string_to_num([item if item != "-" else 1000 for item in Incumbent],tpe=float))
    Time= read_nth_last_column(file_path, 1)
    Time=np.array(string_to_num([int(Time[i].rstrip('s')) for i in range(len(Time))],tpe=int))
    #lr
    lr_BestBd= string_to_num(read_nth_last_column(lr_file_path, 4),tpe=float)
    lr_Incumbent= read_nth_last_column(lr_file_path, 5)
    lr_Incumbent=np.array(string_to_num([item if item != "-" else 1000 for item in lr_Incumbent],tpe=float))
    lr_Time= read_nth_last_column(lr_file_path, 1)
    lr_Time=np.array(string_to_num([int(lr_Time[i].rstrip('s')) for i in range(len(lr_Time))],tpe=int))

    mask = Incumbent != 1000
    Incumbent_mask=Incumbent[mask]
    Time_mask=Time[mask]
    #lr
    lr_mask = lr_Incumbent != 1000
    lr_Incumbent_mask=lr_Incumbent[lr_mask]
    lr_Time_mask=lr_Time[lr_mask]

    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 设置字体为 SimHei
    plt.rcParams['axes.unicode_minus'] = False  # 禁用 Unicode 负号


    _, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))  # 1 行 2 列的子图布局

    # 在第一个子图中绘制数据
    Time_max_v=max(lr_Time.max(),Time.max())
    ax1.plot(Time_mask,Incumbent_mask, label='原始目标函数值', color='blue') 
    ax1.set_xlabel('Time')  # 设置 x 轴标签
    ax1.set_ylabel('目标函数值(下界)')  # 设置 y 轴标签
    ax1.set_title(f'路径{file[-1]}')  # 设置子图标题
    ax1.set_xlim(0,Time_max_v+300)
    # lr
    ax1.plot(lr_Time_mask,lr_Incumbent_mask, label='松弛目标函数值', color='red') 
    ax1.legend()

    # 在第二个子图中绘制数据
    Time_max_v=max(lr_Time.max(),Time.max())
    ax2.plot(Time,BestBd, label='原始最大上界', color='blue') 
    ax2.set_xlabel('Time')  # 设置 x 轴标签
    ax2.set_ylabel('最大上界')  # 设置 y 轴标签
    ax2.set_title(f'路径{file[-1]}')  # 设置子图标题
    ax2.set_xlim(0,Time_max_v+300)
    #lr
    ax2.plot(lr_Time,lr_BestBd, label='松弛最大上界', color='red') 
    ax2.legend()

    plt.savefig(rf'result/{file}_vs_{lr_file}.png')

if __name__=='__main__':
    log_D3 = 'log_D3'
    log_lr_D3 = 'log_lr_D3'
    log_D4 = 'log_D4'
    log_lr_D4 = 'log_lr_D4'
    visualize_log(log_D3,log_lr_D3)
    visualize_log(log_D4,log_lr_D4)