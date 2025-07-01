# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : pt-dislline.py
# Time       ：2025/2/25 16:07
# Author     ：oWoo
# Description：
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from ovito.io import import_file
from ovito.modifiers import SelectTypeModifier, CommonNeighborAnalysisModifier,\
    InvertSelectionModifier, DeleteSelectedModifier

def calc_line(sf):
    # calculate the width of the stacking faults
    z_sf = sf.particles['Position'][:, 2]
    y_sf = sf.particles['Position'][:, 1]
    x_sf = sf.particles['Position'][:, 0]

    linex, linez = group_atoms(list(zip(z_sf, x_sf)))

    return linex, linez


def group_atoms(data, threshold=0.5):

    data.sort(key=lambda x: x[0])
    xs = []
    zs = []
    current_x = [data[0][1]]
    current_z = [data[0][0]]

    for i in range(1, len(data)):
        if data[i][0] - data[i - 1][0] <= threshold:
            current_x.append(data[i][1])
            current_z.append(data[i][0])
        else:
            xs.append(np.mean(current_x))
            zs.append(np.mean(current_z))
            current_z = [data[i][0]]
            current_x = [data[i][1]]
    xs.append(np.mean(current_x))
    zs.append(np.mean(current_z))

    return xs, zs

if __name__ == '__main__':
    filepath = "/Users/kaioneer/Documents/data/disl_line"
    steps = list(range(0, 50001, 50))

    x_list = []
    z_list = []

    for step in steps:
        pipeline = import_file(f"{filepath}/dump/sf_2_{step}.cfg")
        data = pipeline.compute()

        # # getting atoms in stacking faults
        # modifier = CommonNeighborAnalysisModifier()
        # pipeline.modifiers.append(modifier)
        # modifier = SelectTypeModifier(
        #     operate_on="particles",
        #     property="Structure Type",
        #     types={CommonNeighborAnalysisModifier.Type.HCP}
        # )
        # pipeline.modifiers.append(modifier)
        # pipeline.modifiers.append(InvertSelectionModifier())
        # pipeline.modifiers.append(DeleteSelectedModifier())
        # sf_atoms = pipeline.compute()  # stacking fault

        linex, linez = calc_line(data)
        with open(f'{filepath}/line/line_{step}.txt', 'w') as file:
            for item1, item2 in zip(linex, linez):
                file.write(f'{item1}\t{item2}\n')

        # if step == 0:
        #     pt = pd.read_csv(f'{filepath}/pt_200MPa.txt', sep=' ')
        #     pt = pt[pt['pinning_time'] != -1].reset_index(drop=True)
        #     x = pt['Coord1'] + data.cell.matrix[0, 3]
        #     y = pt['Coord2'] + data.cell.matrix[2, 3]
        #     z = pt['pinning_time']
        #
        #     x_unique = np.unique(x)  # 获取唯一的x坐标值
        #     y_unique = np.unique(y)  # 获取唯一的y坐标值
        #
        #     X, Y = np.meshgrid(x_unique, y_unique)
        #
        #     Z = np.full_like(X, np.nan, dtype=float)
        #     for i in range(len(x)):
        #         x_idx = np.where(x_unique == x[i])[0][0]  # 列的位置
        #         y_idx = np.where(y_unique == y[i])[0][0]  # 行的位置
        #         Z[y_idx, x_idx] = z[i]
        #
        #     pt_max = np.nanargmax(Z, axis=0)
        #     pt_max_x = X[0, :]
        #     pt_max_y = Y[pt_max, 0]

        plt.figure()
        plt.plot(linex,linez, label='dislocation line')
        # plt.scatter(pt_max_x, pt_max_y, s=10, edgecolor='r', facecolor='none', label='pinning point')
        plt.xlabel('x (Å)')
        plt.ylabel('z (Å)')
        plt.legend()
        plt.xlim(0, 500)
        plt.title(f'step {step}')
        plt.savefig(f"{filepath}/pic/line_{step}.png")
        plt.close()



