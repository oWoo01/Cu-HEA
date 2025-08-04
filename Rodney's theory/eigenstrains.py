#!/usr/bin/env python

# coding:utf8

# # @Time    : 2025/7/29 9:42


# calculate the eigenstrain 𝜀𝛼 (defined as the change of lattice spacing with composition around the alloy composition）
# P.-A. Geslin and D. Rodney, Journal of the Mechanics and Physics of Solids 153 (2021) 104479

# Create by oWoo

#


import os
import re
import numpy as np
import csv
import pandas as pd
import matplotlib.pyplot as plt

if __name__ == "__main__":
    delta_c = 0.01  # 浓度扰动
    nelem = 4

    if nelem == 2:
        alloy = 'binary'
    else:
        alloy = 'quaternary'

    # 设置路径和参数
    path = os.path.expanduser(f'results/{alloy}/')
    base_dirs = sorted(
        [d for d in os.listdir(path) if re.match(r'^W\d+\.\d+', d)],
        key=lambda x: float(x[1:])
    )


    # 初始化
    c_w_list = []       # 保存每个目录的W浓度
    da_dc_list = []     # 保存对应的da/dc值
    mean_lc_list = []   # 保存平均晶格常数
    e_list = []     # 保存本征应变
    tau_std_list = []

    # ======== 求 eigenstrains 和 tau_std =============
    for base_dir in base_dirs:
        print(f'Processing: {base_dir}')
        c_w = float(base_dir[1:])
        c_w_list.append(c_w)

        filepath = os.path.join(path, base_dir, "lattice-constant.txt")
        if not os.path.isfile(filepath):
            print(f"⚠️ Warning: {filepath} not found.")
            continue

        with open(filepath, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]

        elem_names = []
        values_pos = []
        values_neg = []

        for i in range(0, len(lines), 6):
            key = lines[i]
            values = [float(lines[i+j]) for j in range(1, 6)]
            avg_val = np.mean(values)

            elem, sign = key.rsplit('_', 1)

            if sign == 'pos':
                elem_names.append(elem)
                values_pos.append(avg_val)
            elif sign == 'neg':
                values_neg.append(avg_val)

        # === 计算导数 ===
        if len(values_pos) == len(values_neg):
            da_dc = [(p - n) / (2 * delta_c) for p, n in zip(values_pos, values_neg)]
            avg_lc = [(p + n) / 2 for p, n in zip(values_pos, values_neg)]
            da_dc_list.append(da_dc)
            mean_lc = np.mean(avg_lc)
            mean_lc_list.append(mean_lc)
        else:
            print(f"⚠️ Incomplete pos/neg pairs in {base_dir}")
            da_dc_list.append([np.nan]*len(values_pos))
            mean_lc = np.nan
            mean_lc_list.append(np.nan)

        # === 计算eigenstrain ===
        if nelem == 2:
            other = 1 - c_w
            e_Nb = 2 * other / mean_lc * da_dc[0]
            e_W = 2 * c_w / mean_lc * da_dc[1]
            es = [e_Nb, e_W]

        else:
            other= (1 - c_w) / (nelem - 1)
            e_Nb = other/mean_lc * (2 * da_dc[0] - da_dc[1] - da_dc[2]) + c_w / mean_lc * (da_dc[0] - da_dc[3])
            e_Mo = other/mean_lc * (2 * da_dc[1] - da_dc[0] - da_dc[2]) + c_w / mean_lc * (da_dc[1] - da_dc[3])
            e_Ta = other/mean_lc * (2 * da_dc[2] - da_dc[1] - da_dc[0]) + c_w / mean_lc * (da_dc[2] - da_dc[3])
            e_W = other/mean_lc * (3 * da_dc[3] -da_dc[0] - da_dc[1] - da_dc[2])
            es = [e_Nb, e_Mo, e_Ta, e_W]

        e_list.append(es)
        print('Finished')


    # ============ 保存结果 =============
    output_file = f"{path}/eigenstrains.csv"

    # 写入 CSV 文件
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)

        # 写入表头
        if nelem == 2:
            writer.writerow(['W_conc', 'da_dc_Nb', 'da_dc_W', 'mean_lc', 'e_Nb', 'e_W'])
        else:
            writer.writerow(['W_conc', 'da_dc_Nb', 'da_dc_Mo', 'da_dc_Ta', 'da_dc_W',
                             'mean_lc', 'e_Nb', 'e_Mo', 'e_Ta', 'e_W'])

        # 写入每一行数据
        for i in range(len(c_w_list)):
            row = [c_w_list[i]]

            # 加入导数
            row.extend(da_dc_list[i])

            # 加入平均晶格常数
            row.append(mean_lc_list[i])

            # 加入eigenstrain
            row.extend(e_list[i])

            writer.writerow(row)

    print(f"✅ 已保存至 {output_file}")


    # 绘图
    df = pd.read_csv(f'{path}/eigenstrains.csv')

    plt.plot(df['W_conc'], df['e_Nb'], '-o', label='e_Nb')
    if nelem == 4:
        plt.plot(df['W_conc'], df['e_Mo'], '-o', label='e_Mo')
        plt.plot(df['W_conc'], df['e_Ta'], '-o', label='e_Ta')
    plt.plot(df['W_conc'], df['e_W'], '-o', label='e_W')
    plt.xlabel('W concentration')
    plt.ylabel('Eigenstrain')
    plt.legend()
    plt.grid(True)
    plt.savefig(f'{path}/eigenstrains.png', dpi=300)
    # plt.show()
