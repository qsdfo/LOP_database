import matplotlib.pyplot as plt


def histogram(data):
    n, bins, patches = plt.hist(data, bins=50, normed=1, histtype='bar', rwidth=0.8)
    plt.show()
