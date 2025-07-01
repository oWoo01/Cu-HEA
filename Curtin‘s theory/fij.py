#!/usr/bin/env python3
import numpy as np
import pandas as pd
import multiprocessing as mp
from ovito.io import import_file
from ovito.modifiers import SelectTypeModifier, CommonNeighborAnalysisModifier,\
    InvertSelectionModifier, DeleteSelectedModifier, ExpressionSelectionModifier
from scipy.optimize import minimize
import matplotlib.pyplot as plt

b = 3.552 / 2 ** 0.5  # burgers vector
b_partial = 3.552 / (6 ** 0.5)


def group_atoms(df, t):
    return np.round(df / t) * t

def calc_bgaus(xi, bb, dd):
    sigma = 1.5 * bb
    bgaus = np.exp(-( (xi-dd/2) / sigma )**2 / 2) + np.exp(-( (xi+dd/2) / sigma )**2 /2)
    return bgaus

def calc_fxy(xi, yj, bb ,dd):
    return calc_bgaus(xi, bb, dd) * yj / (xi**2 + yj**2) * bb   # 应该除以den，但为了简化，放到最后再除，反正是个常数

def func(w, x_array, y_array, bb, dd):
    sum_f2=0
    for i in range(len(x_array)):
        for j in range(len(y_array)):
            sum_f2 += (calc_fxy(x_array.iloc[i]-w, y_array.iloc[j], bb, dd)
                       -calc_fxy(x_array.iloc[i], y_array.iloc[j], bb, dd))**2
            # print('sum_f2')
    return sum_f2 / w


def work(ii, x, y):
    d_sf = b * ii
    x_guess = np.asarray(20)
    den_xi = []
    for k in range(len(x_all)):
        den_xi.append(calc_bgaus(x.iloc[k], b_partial, d_sf))
    den = np.sum(den_xi)
    w_cc = minimize(func, x0=x_guess, args=(x, y, b_partial, d_sf),
                    options={'maxiter': 1000}, bounds=[[1, 100]], callback=callbackf)
    print("--------------")
    print("d/b = ", ii)
    print("w_c = ", w_cc.x)
    print("den = ", den)
    print("f2/w = ", w_cc.fun/den)

    return [ii ,w_cc.fun/den*w_cc.x]


def callbackf(result):
    print(result)


# def func(w, sum_fij, sum_fij2, x_array, y_array, bb, dd):
#     sum_fw = 0
#     for ii in range(len(x_array)):
#         for jj in range(len(y_array)):
#             fijw = calc_fxy(x_array[i] - w, y_array[j], bb, dd)
#             sum_fw2 += fijw**2 + 2
#             sum_fw += 2 * fijw

if __name__ == '__main__':
    pipeline = import_file(r"/home/jyzhang/pycode/data.0_disl")
    data = pipeline.compute()

    y_half = data.cell.matrix[1, 3] + (data.cell.matrix[1, 1] - data.cell.matrix[1, 3]) / 2

    #----- getting atoms in stacking faults ------
    modifier = CommonNeighborAnalysisModifier()
    pipeline.modifiers.append(modifier)
    modifier = SelectTypeModifier(
        operate_on="particles",
        property="Structure Type",
        types={CommonNeighborAnalysisModifier.Type.HCP}
    )
    pipeline.modifiers.append(modifier)
    pipeline.modifiers.append(InvertSelectionModifier())
    pipeline.modifiers.append(DeleteSelectedModifier())
    sf = pipeline.compute()  # stacking fault

    # calculate the width of the stacking faults
    z_sf = sf.particles['Position'][:, 2]
    y_sf = sf.particles['Position'][:, 1]
    x_sf = sf.particles['Position'][:, 0]

    # calculate the distribution of b(xi)
    x_min = data.cell.matrix[0, 3]
    x_max = data.cell.matrix[0, 0]
    x0 = np.mean(x_sf)  # new original

    # getting coordinate of all atoms in the model
    x_all = data.particles['Position'][:, 0] - x0
    y_all = data.particles['Position'][:, 1]
    z_all = data.particles['Position'][:, 2]
    co_all = pd.DataFrame({'x': x_all, 'y': y_all, 'z': z_all})
    co_all = co_all[(co_all['z']<2) & (co_all['x']<100)]
    x_all = co_all['x']
    y_all = co_all['y']

    # w_c = []
    # f = []      # fij2/w
    # di = []
    # for i in range(5,41,1):
    #     d_sf = b * i
    #     den_xi = []
    #     for k in range(len(x_all)):
    #         den_xi.append(calc_bgaus(x_all.iloc[k], b_partial, d_sf))
    #     den = np.sum(den_xi)
    #     w_cc = minimize(func, x0=x_guess, args=(x_all, y_all, b_partial, d_sf),
    #                options={'maxiter': 1}, bounds=[[1, 100]], callback=callbackf)
    #     w_c.append(w_cc.x)
    #     f.append(w_cc.fun/den)
    #     di.append(i)
    #     print(i)
    #
    # result = zip(di, f)


    mp.set_start_method('fork')
    pool = mp.Pool(36)
    results = [pool.apply_async(work, args=(i, x_all, y_all)) for i in range(5,41,1)]
    results = [p.get() for p in results]

    with open("fij2-w.txt", "w") as file:
        for item in results:
            file.write(f"{item}\n")

    di, f = zip(*results)
    plt.figure()
    plt.plot(di,f)
    plt.savefig("f-d.png")
    plt.close()

