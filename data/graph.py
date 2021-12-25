import time
import pickle
import numpy as np
from matplotlib import pyplot as plt
import seaborn as sns
from scipy.ndimage import gaussian_filter1d

def load_pickle(filename, filtered = True):
    if isinstance(filename, str):
        with open(filename, 'rb') as f:
            return pickle.load(f)
    elif isinstance(filename, list):
        files = []
        for name in filename:
            if filtered:
                files.append(gaussian_filter1d(load_pickle(name), 80))
            else:
                files.append(load_pickle(name))
        return files

def plot_results(values, title, ylabel, legend):
    sns.set_style('white')
    sns.set_context('talk')
    plt.title(title)
    plt.plot(values)
    plt.ylabel(ylabel)
    plt.legend(legend, loc=5)
    sns.despine()
    plt.show()

def main():
    filecode =  ['12-12-19:49', '12-13-17:40', '12-13-23:01', '12-13-23:04', '12-15-15:44']
    legend   =  ['DQN origin', 'FCN', 'smallnet', 'large_decay', 'q-learning']
#    filecode =  ['12-12-19:49', '12-13-17:40', '12-13-23:01', '12-13-23:04']
#    legend   =  ['DQN origin',  'FCN', 'smallnet', 'large_decay']
    reward_pkl = [f'{code}/{code}_avg_reward.pkl' for code in filecode]
    stats_pkl = [f'{code}/{code}_stats.pkl' for code in filecode]
    loss_pkl = [f'{code}/{code}_loss.pkl' for code in filecode[:-1]]

    reward = load_pickle(reward_pkl, False)
    reward = [np.array(value[:600]) for value in reward]
    a = np.array(reward)
    a[0] = gaussian_filter1d(a[0], 2)
    a[1] = gaussian_filter1d(a[1], 2)
    a[2] = gaussian_filter1d(a[2], 2)
    a[3] = gaussian_filter1d(a[3], 2)
    a[4] = gaussian_filter1d(a[4], 2)

    reward = a.transpose()
    plot_results(reward, 'average reward per 1000 games', 'reward', legend)
    
    stats = load_pickle(stats_pkl, False)
    winrate = np.array([np.array([sample[0]/sum(sample) for sample in stat[:600]]) for stat in stats])
    a = np.array(winrate)
    a[0] = gaussian_filter1d(a[0], 4)
    a[1] = gaussian_filter1d(a[1], 4)
    a[2] = gaussian_filter1d(a[2], 4)
    a[3] = gaussian_filter1d(a[3], 4)
    a[4] = gaussian_filter1d(a[4], 4)

    winrate = a.transpose()
    plot_results(winrate, 'winrate per 1000 games', 'winrate', legend)

    loss = load_pickle(loss_pkl, False)
    loss = [np.array(value[:600]) for value in loss]
    a = np.array(loss)
    a[0] = gaussian_filter1d(a[0], 1)
    a[1] = gaussian_filter1d(a[1], 1)
    a[2] = gaussian_filter1d(a[2], 1)
    a[3] = gaussian_filter1d(a[3], 1)

    loss = a.transpose()
    plot_results(loss, 'Huber loss per update', 'loss', legend)

if __name__ == '__main__':
    main()
#    filecode = ['11-21-16:00']
#    board_pkl = [f'{code}/{code}_small_board_Q.pkl' for code in filecode]
#    reward_pkl = [f'{code}/{code}_small_board_avg_reward.pkl' for code in filecode]
#    stats_pkl = [f'{code}/{code}_small_board_stats.pkl' for code in filecode]
#    legend = ['random']
#
#    reward = np.array(load_pickle(reward_pkl, False))
#    reward = reward.transpose()
#    print(np.mean(reward), np.var(reward))
#    plot_results(reward, 'average reward per 1000 games', 'reward', legend)
#
#    stats = load_pickle(stats_pkl, False)
#    winrate = [[sample[0]/sum(sample) for sample in stat] for stat in stats]
#    winrate = np.array(winrate).transpose()
#
#    print(np.mean(winrate), np.var(winrate))
#    legend = ['random']
#    plot_results(winrate, 'winrate per 1000 games', 'winrate', legend)
