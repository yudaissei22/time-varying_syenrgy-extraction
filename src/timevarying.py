import numpy as np


def extract(dataset, n_synergies, synergy_length, n_dof, n_iter=100, lr=1e-3, refractory_period=10, n_synergies_use=100, amplitude_threshold=1e-2):
    # Initialize synergies
    synergies = np.random.uniform(0.0, 1.0, (n_synergies, synergy_length, n_dof))
    """ 
    synergy lengthとはなんだ？
    ここでは、0~1の値で、3次元配列を作った感じ。
    n_synergies行*synergy_length列の行列が、n_dof個あるというものである。
    """

    # Extract motor synergies
    for i in range(n_iter):
        delays, amplitude = match_synergies(dataset, synergies, n_synergies_use, refractory_period, amplitude_threshold)

# """ 
# delaysってなんだ？何がどう遅れているんだ？
# これは時間の平行移動を表すやつか。 
# amplitudeは振幅である。
# つまり、match_synergiesをn_iterだけ繰り返すことで、delaysとamplitudeを的確な値にできる。
# そんで、各引数の意味について、
# datasetは、tauとかもとのデータ
# synergiesは、delaysとamplitudeで使用するsynergies
# n_synergies_useは分からない。
# refactory_periodも分からない。
# amplitude_thresholdは、振幅のしきい値
# """
        r2 = compute_R2(dataset, synergies, delays, amplitude)
# """
# もとのデータと、time-varying synergyによるデータの差を計算する。
# 引数は納得。
# もとのデータを、それを再構成するために必要な3つのデータ.
# """
        print("Iter {:4d}: R2 = {}".format(i, r2))
        synergies = update_synergies(dataset, synergies, delays, amplitude, lr)
# """
# おそらくr2の結果をもとに、synergyを再構成していく。
# updateしていくための引数は、、
# ・datasetはもとのデータであるが、どのように使われているのか？
# ・synergiesはtime-varying synergyであり、これが新しい値になっていくのか
# ・delaysは時間変化
# ・amplitudeは振幅
# ・lrは、なんだ？
# """
# """
# これは多分、iterationが終わったデータで再構成したデータを計算して表示するためのプログラム.
# """


# Reconstruct actions
    print("here")


    lengths = [d.shape[0] for d in dataset]
    delays, amplitude = match_synergies(dataset, synergies, n_synergies_use, refractory_period, amplitude_threshold)
    dataset_rec = decode(delays, amplitude, synergies, lengths)

    """
    lengthって何？decodeでは何をするの？
    """ 
    return synergies, delays, amplitude, dataset_rec


def match_synergies(dataset, synergies, n_synergy_use, refractory_period, amplitude_threshold):
    """
    Find the delays and amplitude with matching pursuit.

    The algorithm is based on [d'Avella et al., 2005] but without the back-projection.
    """
    
    """
    refactoryは、手に負えない・加工しにくい。
    periodは期間。
    thresholdは、しきい値。
    amplitudeは、振幅
    """
    # Setup variables
    n_data = len(dataset)
    synergy_length = synergies.shape[1]
    n_synergies = synergies.shape[0]
    print("n_data is", n_data)
    print("Synergies shape is", synergies.shape)
    print("Synergies_length shape is", synergies.shape[0])
    print("n_synergies shape is", synergies.shape[1])

    """
    これもとのsynergyとはどういう形のものなの？
    (2, 20 ,3)という形だった。
    """
    
    # Initialize delays
    delays = [[[] for _ in range(n_synergies)] for _ in range(n_data)]
    amplitude = [[[] for _ in range(n_synergies)] for _ in range(n_data)]
    # print("Initialize delay is", delays.shape)
    # print("Initialize amplitute is", amplitude.shape)
    # list object has not shape
    
    # Find delay times for each data sequence
    for n in range(n_data):
        residual = dataset[n].copy()
        data_length = residual.shape[0]

        synergy_available = np.full((n_synergies, data_length), True)  # Whether the delay time of the synergy can be used
        for d in range(n_synergy_use):
            # Compute dot products for all possible patterns
            corr = np.zeros((n_synergies, data_length))
            for k in range(n_synergies):
                for ts in range(data_length - synergy_length):
                    if synergy_available[k, ts]:
                        corr[k, ts] = np.sum(residual[ts:ts+synergy_length, :] * synergies[k])

            # Register the best-matching pattern
            k, ts = np.unravel_index(np.argmax(corr), corr.shape)
            c = np.max(corr) / np.sum(synergies[k] ** 2)

            # Finish matching when the correlation is lower than the threshold
            if c < amplitude_threshold:
                break

            delays[n][k].append(ts)
            amplitude[n][k].append(c)

            # Subtract the selected pattern
            residual[ts:ts+synergy_length, :] -= c * synergies[k]

            # Remove the selected pattern and its surroundings
            t0 = max(ts - refractory_period, 0)
            t1 = min(ts + refractory_period, data_length)
            synergy_available[k, t0:t1] = False

    return delays, amplitude


def update_synergies(dataset, synergies, delays, amplitude, mu=0.001):
    """
    Update synergies with gradient descent.

    The algorithm is based on [d'Avella and Tresch, 2002].
    """
    n_data = len(dataset)
    grad = np.zeros_like(synergies)

    for n in range(n_data):
        data = dataset[n]

        # Compute reconstruction data
        data_est = np.zeros_like(data)
        for k in range(synergies.shape[0]):
            for ts, c in zip(delays[n][k], amplitude[n][k]):
                data_est[ts:ts+synergies.shape[1], :] += c * synergies[k, :, :]

        # Compute the gradient
        deviation = data - data_est
        for k in range(synergies.shape[0]):
            for ts, c in zip(delays[n][k], amplitude[n][k]):
                grad[k, :, :] += deviation[ts:ts+synergies.shape[1], :] * c

    # Compute the gradiento
    grad = grad * -2

    # Update the amplitude
    synergies = synergies - mu * grad
    synergies = np.clip(synergies, 0.0, None)  # Limit to non-negative values

    for k in range(synergies.shape[0]):
        norm = np.sqrt(np.sum(np.square(synergies[k])))
        synergies[k] = synergies[k] / float(norm)

    return synergies


def decode(delays, amplitude, synergies, lengths):
    n_data = len(delays)
    n_synergies, synergy_length, dof = synergies.shape

    dataset = []
    for n in range(n_data):
        data_length = lengths[n]

        data = np.zeros((data_length, dof))
        for k in range(n_synergies):
            for ts, c in zip(delays[n][k], amplitude[n][k]):
                data[ts:ts + synergy_length, :] += c * synergies[k, :, :]

        dataset.append(data)

    return dataset


def compute_R2(dataset, synergies, delays, amplitude):
    n_data = len(dataset)

    mse_sum = 0.0

    for n in range(n_data):
        data = dataset[n]

        # Compute reconstruction data
        data_est = np.zeros_like(data)
        for k in range(synergies.shape[0]):
            for ts, c in zip(delays[n][k], amplitude[n][k]):
                data_est[ts:ts+synergies.shape[1], :] += c * synergies[k, :, :]

        mse_sum += np.sum(np.square(data - data_est))

    data_cat = np.concatenate(dataset, axis=0)
    data_mean = np.mean(data_cat)

    # Compute the R2 value
    R2 = 1 - mse_sum / np.sum(np.square(data_cat - data_mean))

    return R2


def compute_mse(dataset, synergies, delays, amplitude):
    n_data = len(dataset)

    mse_sum = 0.0

    for n in range(n_data):
        data = dataset[n]

        # Compute reconstruction data
        data_est = np.zeros_like(data)
        for k in range(synergies.shape[0]):
            for ts, c in zip(delays[n][k], amplitude[n][k]):
                data_est[ts:ts+synergies.shape[1], :] += c * synergies[k, :, :]

        mse_sum += np.sum(np.square(data - data_est))

    return mse_sum


def transform_nonnegative(dataset):
    """
    Convert a data that has negative values to non-negative signals with doubled dimensions.
    The dataset is assumed to be a list of trajectories with shape of (length, DoF).
    The result dataset is a list of trajectories with shape of (length, 2 * DoF).
    The first half in DoF-axis corresponds to the positive values, whereas the second half corresponds to the negative values.
    """
    dataset_nn = []

    for data in dataset:
        n_dof = data.shape[1]  # Dimensionality of the original data

        # Convert the data to non-negative signals
        data_nn = np.empty((data.shape[0], n_dof*2))
        data_nn[:, :n_dof] = +np.maximum(data, 0.0)
        data_nn[:, n_dof:] = -np.minimum(data, 0.0)

        dataset_nn.append(data_nn)

    return dataset_nn


def inverse_transform_nonnegative(dataset):
    """
    Inverse conversion of `transform_nonnegative()`; Convert a non-negative dataset to another dataset that contains negative values.
    The non-negative dataset is assumed to be a list of trajectories with shape of (length, DoF).
    The reconstructed dataset is a list of trajectories with shape of (length, DoF / 2).
    """
    dataset_rc = []

    for data in dataset:
        n_dof = int(data.shape[1] / 2)  # Dimensionality of the original data

        # Restore the original data
        data_rc = np.empty((data.shape[0], n_dof))
        data_rc = data[:, :n_dof] - data[:, n_dof:]

        dataset_rc.append(data_rc)

    return dataset_rc
