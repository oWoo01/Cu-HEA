# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : tau_std.py
# Time       ：2025/7/29 16:28
# Author     ：oWoo
# Description：compute tau_std according to Rodney's elastic model
"""
import numpy as np
import pandas as pd
import csv


if __name__ == '__main__':
    nelem = 4
    alloy = 'quaternary'
    factor_bcc = 2.397812118626113431

    path = '/home/jyzhang/lammps/Rodney'
    modulus_path = f'{path}/elastic-modulus/avg_modulus{nelem}.txt'
    eigenstrains_path = f'{path}/results/{alloy}/eigenstrains.csv'

    df1 = pd.read_csv(modulus_path, sep=' ', names=['W_conc', 'mu', 'nu'])
    df2 = pd.read_csv(eigenstrains_path)

    if len(df1) != len(df2):
        print('⚠️ Modulus and eigenstrains are unmatched!')

    tau_std_list = []
    W_conc_list = []
    for _, row in df1.iterrows():
        c_w = row['W_conc']
        mu = row['mu']      # unit: GPa
        nu = row['nu']

        subset = df2[df2['W_conc']==c_w]
        a_lat = subset['mean_lc']       # unit: Angstrom
        e = np.array(subset.iloc[0][-nelem:])

        other = (1-c_w)/(nelem-1)
        comps = np.full(nelem, other)
        comps[-1] = c_w
        delta_e2 = np.sum(comps * e ** 2)

        # Eq.(22)
        v_at_bcc = a_lat**3/2
        tau_var = 9/4 * (v_at_bcc*mu/np.pi) ** 2 * delta_e2 * ((1+nu)/(1-nu))**2 * factor_bcc / a_lat**6     # unit: GPa^2

        tau_std = np.sqrt(tau_var) * 1000    # unit: MPa
        tau_std_list.append(tau_std)
        W_conc_list.append(c_w)


    # 写入 CSV 文件
    output_file = f"{path}/results/{alloy}/tau_std.csv"
 
    with open(output_file, 'w', newline='') as f:
        writer = csv.writer(f)

        writer.writerow(['W_conc', 'tau_std(MPa)'])

        for i in range(len(tau_std_list)):
            row = [W_conc_list[i]]
            row.extend(tau_std_list[i])

            writer.writerow(row)

    print(f"✅ 已保存至 {output_file}")

