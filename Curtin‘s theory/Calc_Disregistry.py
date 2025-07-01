import numpy as np
import pandas as pd
from ovito.io import import_file
from ovito.modifiers import SelectTypeModifier, CommonNeighborAnalysisModifier,\
    InvertSelectionModifier, DeleteSelectedModifier, ExpressionSelectionModifier
from scipy.optimize import fmin
from scipy.optimize import minimize
import matplotlib
matplotlib.use('macosx')
import matplotlib.pyplot as plt

def group_atoms(df, t):
    return np.round(df / t) * t

def calc_bgaus(xi, bb, dd):
    sigma = 1.5 * bb
    bgaus = np.exp(-( (xi-dd/2) / sigma )**2 / 2) - np.exp(-( (xi+dd/2) / sigma )**2 /2)
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
    b = 3.552 / 2 ** 0.5     # burgers vector
    b_partial = 3.552 / (6 ** 0.5)

    result = pd.DataFrame(columns=['x_Cu', 'w_c', 'fij/w'])

    pipeline = import_file(rf"/Users/kaioneer/data/fecu_7.data")
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
    co_sf = pd.DataFrame({'x': x_sf, 'y': y_sf, 'z': z_sf})
    co_sf = co_sf[(co_sf['y']<100) & (co_sf['y']>50)]
    co_sf['z_grouped'] = group_atoms(co_sf['z'], 1)
    di=[]
    for zi in co_sf['z_grouped'].unique():
        subset = co_sf[co_sf['z_grouped'] == zi]
        if len(subset) > 1:
            di.append(subset['x'].max() - subset['x'].min())
        else:
            print(f'Atoms grouped in {zi} may have something wrong.')
    d_sf = np.mean(di)  # width of stacking faults
    print(f"width of stacking faults = {d_sf}")

    # calculate the distribution of b(xi)
    x_min = data.cell.matrix[0, 3]
    x_max = data.cell.matrix[0, 0]
    x0 = np.mean(x_sf)  # new original
    x_lf = x_min - x0
    x_rt = x_max - x0
    xi_array = np.linspace(x_lf, x_rt, num=500)
    den_xi = []
    for k in range(len(xi_array)):
        den_xi.append(calc_bgaus(xi_array[k], b_partial, d_sf))
    den = np.sum(den_xi)
    # plt.plot(list(xi_array/b_partial), den_xi)
    # plt.plot(list(xi_array / d_sf)[200:280], den_xi[200:280])
    # plt.xlabel('x/d_sf')
    # plt.ylabel('b(x)/b_partial')
    # plt.title('Distribution of Burgers vector magnitude in the glide plane')
    # plt.show()

    # bxi = b_partial * calc_bgaus(xi, b_partial, d_sf) / den

    # getting coordinate of all atoms in the model
    x_all = data.particles['Position'][:, 0] - x0
    y_all = data.particles['Position'][:, 1]
    z_all = data.particles['Position'][:, 2]
    co_all = pd.DataFrame({'x': x_all, 'y': y_all, 'z': z_all})
    co_all = co_all[(co_all['z']<2) & (co_all['x']>-100) & (co_all['x']<100)]
    x_all = co_all['x']
    y_all = co_all['y']
    # w_c = fmin(func, x0=1, args=(x_all, y_all, b_partial, d_sf), maxiter=1000)
    x_guess = np.asarray(20)
    w_cc = minimize(func, x0=x_guess, args=(x_all, y_all, b_partial, d_sf),
                    options={'maxiter': 1}, bounds=[[1, 100]], callback=callbackf)

    print("Result of optimization is:")
    print(f"w_c = {w_cc.x}")
    print(f"value of func = {w_cc.fun}")

    # new_result = pd.DataFrame({'x_Cu': [iii]], 'w_c': [w_cc.x], 'fij/w': [w_cc.fun]})
    # result = pd.concat([result, new_result])
    # sum_fij2 = 0
    # sum_fij = 0
    # for i in range(len(x_all)):
    #     for j in range(len(y_all)):
    #         sum_fij2 += calc_fxy(x_all[i], y_all[j], b_partial, d_sf) ** 2
    #         sum_fij += calc_fxy(x_all[i], y_all[j], b_partial, d_sf)

    #
    # pipeline3 = import_file(rf"C:\Users\kaioneer\Desktop\fecu_7.data")
    # modifier = ExpressionSelectionModifier(expression=rf"Position.Y<81 && Position.Y>79")
    # pipeline3.modifiers.append(modifier)
    # pipeline3.modifiers.append(InvertSelectionModifier())
    # pipeline3.modifiers.append(DeleteSelectedModifier())
    # slice_top = pipeline3.compute()
    # x_top = slice_top.particles['Position'][:, 0]
    # z_top = slice_top.particles['Position'][:, 2]
    #
    # # dx = 3.552/2*2**0.5
    # tolerance = 1.1
    # co_top = pd.DataFrame({'x': x_top, 'z': z_top})
    # co_top['x_grouped'] = group_atoms(co_top['x'], 1.1)
    # co_top_sorted = co_top.sort_values(by=['x_grouped', 'z'])
    # co_bot = pd.DataFrame({'x': x_bot, 'z': z_bot})
    # co_bot['x_grouped'] = np.round(co_bot['x'] / tolerance) * tolerance
    # co_bot_sorted = co_bot.sort_values(by=['x_grouped', 'z'])
    #
    #
    #
    # x =     # average of coordinate-x of the atoms which have the same z
    # b_local = calc_b(x, b, d)
    # f_xz = calc_f(b_local, xy)
    #
