import numpy as np
import matplotlib.pyplot as plt
import timevarying


"""
データの読み込みと処理
"""


tau_t = np.loadtxt("nlopt/Aug--7-17-21-37-2023-motion.taulist")
pos_t = np.loadtxt("nlopt/Aug--7-17-21-37-2023-motion.avlist")

"""
241 * 33 ⇨　33 * 241
"""

tau = np.delete(tau_t, 0, axis=1)
pos = np.delete(pos_t, 0, axis=1)

tau = tau.T
pos = pos.T
# これ転置したあとjointの順番はあっているのか？

n_dof = tau.shape[0] # 33
n_time = tau.shape[1] # 241

# n_dof[Nm]行、n_time列

synergy_instance = timevarying.Synergy(n_dof, n_time, n_synergies=3)

# synergy_instance.plot_original_data(tau)
# なぜか引数が合わないというエラーが出る。沼理想なのであと周り

synergies, amplitude, delays, data_reconstruct = synergy_instance.initialize_data()

r2 =  synergy_instance.update_synergy(tau, data_reconstruct,synergies, amplitude, delays, data_reconstruct)

