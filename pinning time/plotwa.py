# !/usr/bin/env python
# -*-coding:utf-8 -*-

"""
# File       : plotwa.py
# Time       ：2025/2/22 16:58
# Author     ：oWoo
# Description：
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go

if __name__ == '__main__':
    filepath = '/Users/kaioneer/Downloads'

    # data = pd.read_csv(f'{filepath}/pt_8.txt', sep=' ')
    data = pd.read_csv(f'{filepath}/pt_250MPa.txt', sep=' ')
    data = data[data['pinning_time'] != -1].reset_index(drop=True)
    x = data['Coord1'] - 460.7205
    y = data['Coord2'] - 199.761
    z = data['pinning_time']

    x_unique = np.unique(x)  # 获取唯一的x坐标值
    y_unique = np.unique(y)  # 获取唯一的y坐标值

    X, Y = np.meshgrid(x_unique, y_unique)

    Z = np.full_like(X, np.nan, dtype=float)
    for i in range(len(x)):
        x_idx = np.where(x_unique == x[i])[0][0]        # 列的位置
        y_idx = np.where(y_unique == y[i])[0][0]       # 行的位置
        Z[y_idx, x_idx] = z[i]

    # fig = plt.figure(figsize=(20, 8))
    # ax = fig.add_subplot(111, projection='3d')
    # surf = ax.plot_surface(X, Y, Z, cmap='viridis')
    # fig.colorbar(surf)
    # ax.set_xlabel('X')
    # ax.set_ylabel('Z')
    # ax.set_zlabel('Pinning time')
    # ax.view_init(elev=20, azim=120)
    # plt.savefig(f"{filepath}/pt.png")

    pt_max = np.nanargmax(Z, axis=0)
    pt_max_x = X[0, :]
    pt_max_y = Y[pt_max, 0]

    fig = go.Figure(data=[go.Surface(z=Z, x=X, y=Y)])

    # 更新布局，设置3D视角
    fig.update_layout(scene=dict(
        xaxis=dict(title='X'),
        yaxis=dict(title='Z'),
        zaxis=dict(title='Pinning time')
    ))

    # 保存为HTML文件
    fig.write_html(f'{filepath}/pt_250MPa.html')