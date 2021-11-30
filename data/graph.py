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
    # '11-12-22:15' alpha
    # '11-13-23:52' alpha + epsilon-decay
    # '11-13-01:59' no decay
    # '11-11-15:28' original
    # '11-21-16:00' random -3789 81980
    #                       0.2929 0.0002038
    filecode =  ['11-12-22:15', '11-13-23:52', '11-13-01:59', '11-11-15:28']
    legend   =  ['alpha',       'alpha-decay', 'no-decay'   , 'original', 'random']
    board_pkl = [f'{code}/{code}_small_board_Q.pkl' for code in filecode]
    reward_pkl = [f'{code}/{code}_small_board_avg_reward.pkl' for code in filecode]
    stats_pkl = [f'{code}/{code}_small_board_stats.pkl' for code in filecode]

    reward = load_pickle(reward_pkl, False)
    reward = np.array([value[:50000] for value in reward])
    reward[0] = gaussian_filter1d(reward[0], 50)
    reward[1] = gaussian_filter1d(reward[1], 80)
    reward[2] = gaussian_filter1d(reward[2], 80)
    reward[3] = gaussian_filter1d(reward[3], 130)
    reward = np.vstack([reward, gaussian_filter1d(np.random.normal(-3789, 81980**.5, (50000,)), 15)])

    reward = reward.transpose()
    plot_results(reward, 'average reward per 1000 games', 'reward', legend)
    
    stats = load_pickle(stats_pkl, False)
    stats = np.array([value[:50000] for value in stats])
    winrate = np.array([[sample[0]/sum(sample) for sample in stat] for stat in stats])
    winrate[0] = gaussian_filter1d(winrate[0], 80)
    winrate[1] = gaussian_filter1d(winrate[1], 80)
    winrate[2] = gaussian_filter1d(winrate[2], 80)
    winrate[3] = gaussian_filter1d(winrate[3], 130)
    winrate = np.vstack([winrate, gaussian_filter1d(np.random.normal(.2929, .0002038**.5, (50000,)), 15)])
    winrate = winrate.transpose()
    plot_results(winrate, 'winrate per 1000 games', 'winrate', legend)

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
