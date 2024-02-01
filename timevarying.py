import numpy as np
import matplotlib.pyplot as plt

class Synergy():
    def __init__(self, n_dof, n_time, n_synergies):
        self.n_dof = n_dof
        self.n_time = n_time

        self.n_synergies = n_synergies

    def initialize_data(self):
        synergies = np.ones((self.n_synergies, self.n_dof, self.n_time))
        amplitude = np.ones((self.n_synergies, 1), dtype=float)
        delays = np.ones((self.n_synergies, 1), dtype=float)
        data_reconstruct = np.ones((self.n_dof, self.n_time), dtype=float)

        return synergies, amplitude, delays, data_reconstruct
        
    def plot_original_data(data):
        fig, axes = plt.subplots(nrows = self.n_dof, ncols = 1, figsize=(6,100), sharex=True, sharey=True)
        for i, ax in enumerate(axes):
            time = np.arange(0.0, self.n_time / 100 ,0.01)
            ax.plot(time, data[i,:])
        plt.show()

        
    def update_synergy(self, data, data_reconstruct, synergies, amplitude, delays, mu = 0.001):
        """
        Update synergies with gradient descent.
        This algorithm is based on [d'Avella and Tresch, 2002].
        """

        # diff tau - tau(reconstruct)
        
        for i in range(self.n_synergies):
            data_reconstruct += amplitude[i,0] * synergies[i,:,:] * delays[i,0]

        # 型を揃えれば、このように行列を足し合わせることができる。
        # (n_dof行[Nm], n_time列)

        diff = data - data_reconstruct

        
