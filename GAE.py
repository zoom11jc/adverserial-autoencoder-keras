# -*- coding: utf-8 -*-

# -*- coding: utf-8 -*-
# Author : Ali Mirzaei
# Date : 19/09/2017


from keras.models import Sequential, Model
from keras.layers import Dense, Input, Flatten, Reshape
from keras.datasets import mnist, cifar10
from keras.optimizers import Adam
import numpy as np
import matplotlib.pyplot as plt
from sklearn.neighbors.kde import KernelDensity
from mpl_toolkits.mplot3d import Axes3D
class GAE():
    def __init__(self, img_shape=(28, 28), encoded_dim=2):
        self.encoded_dim = encoded_dim
        self.optimizer = Adam(0.001)
        self._initAndCompileFullModel(img_shape, encoded_dim)
        self.img_shape = img_shape

    def _genEncoderModel(self, img_shape, encoded_dim):
        """ Build Encoder Model Based on Paper Configuration
        Args:
            img_shape (tuple) : shape of input image
            encoded_dim (int) : number of latent variables
        Return:
            A sequential keras model
        """
        encoder = Sequential()
        encoder.add(Flatten(input_shape=img_shape))
        encoder.add(Dense(1000, activation='relu'))
        encoder.add(Dense(1000, activation='relu'))
        encoder.add(Dense(encoded_dim))
        encoder.summary()
        return encoder

    def _getDecoderModel(self, encoded_dim, img_shape):
        """ Build Decoder Model Based on Paper Configuration
        Args:
            encoded_dim (int) : number of latent variables
            img_shape (tuple) : shape of target images
        Return:
            A sequential keras model
        """
        decoder = Sequential()
        decoder.add(Dense(1000, activation='relu', input_dim=encoded_dim))
        decoder.add(Dense(1000, activation='relu'))
        decoder.add(Dense(np.prod(img_shape), activation='sigmoid'))
        decoder.add(Reshape(img_shape))
        decoder.summary()
        return decoder


    def _initAndCompileFullModel(self, img_shape, encoded_dim):
        self.encoder = self._genEncoderModel(img_shape, encoded_dim)
        self.decoder = self._getDecoderModel(encoded_dim, img_shape)
        img = Input(shape=img_shape)
        encoded_repr = self.encoder(img)
        gen_img = self.decoder(encoded_repr)
        self.autoencoder = Model(img, gen_img)
        self.autoencoder.compile(optimizer=self.optimizer, loss='mse')
    def imagegrid(self, epochnumber):
        fig = plt.figure(figsize=[20, 20])
        for i in range(-5, 5):
            for j in range(-5,5):
                topred = np.array((i*0.5,j*0.5))
                topred = topred.reshape((1, 2))
                img = self.decoder.predict(topred)
                img = img.reshape((28, 28))
                ax = fig.add_subplot(10, 10, (i+5)*10+j+5+1)
                ax.set_axis_off()
                ax.imshow(img, cmap="gray")
        fig.savefig(str(epochnumber)+".png")
        plt.show()
        plt.close(fig)

    def train(self, x_train, batch_size=32, epochs=5):
        self.autoencoder.fit(x_train, x_train, batch_size=batch_size,
                             epochs=epochs)
        codes = self.encoder.predict(x_train)
        self.kde = KernelDensity(kernel='gaussian', bandwidth=0.2).fit(codes)

    def generate(self, n = 10):
        fig = plt.figure(figsize=[20, 20])
        codes = self.kde.sample(n*n)
        images = self.decoder.predict(codes)
        for index,image in enumerate(images):
            image = image.reshape(self.img_shape)
            ax = fig.add_subplot(n, n, index+1)
            ax.set_axis_off()
            ax.imshow(image, cmap="gray")
        fig.savefig("generated.png")
        plt.show()

if __name__ == '__main__':
    # Load MNIST dataset
    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    x_train = x_train.astype(np.float32) / 255.
    x_test = x_test.astype(np.float32) / 255.
    ann = GAE(img_shape=(32,32,3), encoded_dim=10)
    ann.train(x_train, epochs=1)
    ann.generate(10)
    #codes = ann.kde.sample(1000)
    #ax = Axes3D(plt.gcf())
    codes = ann.encoder.predict(x_train)
    plt.scatter(codes[:,0], codes[:,1], c=y_train)
    plt.show()