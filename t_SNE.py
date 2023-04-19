import numpy as np
from sklearn.manifold import TSNE
import matplotlib.pyplot as plt
import dataLSTM
import getData
# Assume your data is stored in a variable called "data" with shape (600, 200, 104)


directories = ['pcapfiles/down','pcapfiles/left']
csi, labels = getData.get_data(directories)

# Flatten each sample into a 1D array of length 200*104=20800
data_flat = csi.reshape((600, -1))

# Use t-SNE to reduce the dimensionality of the data to 2 dimensions
tsne = TSNE(n_components=2, perplexity=30, learning_rate=200)
data_tsne = tsne.fit_transform(data_flat)

# Plot the data in the t-SNE space
plt.scatter(data_tsne[:,0], data_tsne[:,1], c=labels)
plt.show()