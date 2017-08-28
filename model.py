import os
import h5py
import numpy as np
import keras.backend as K
from keras.models import load_model, Model
from keras.layers import Input, Flatten, Dense, Dropout
from keras.layers.normalization import BatchNormalization
from keras.applications.vgg16 import VGG16
from keras.callbacks import EarlyStopping, ModelCheckpoint


def round_mae(y_true, y_pred):
    return K.mean(K.abs(K.round(y_pred) - y_true), axis=-1)


def initialize_model(image_shape, train_conv_layers=False):
    """ Creates a new model if `saved_model.h5` does not exist in the current
       directory. """

    # Custom input tensor with parameter `image_shape`.
    input = Input(shape=image_shape, name='image_input')

    # Load VGG16 model and weights without top dense layers.
    initial_model = VGG16(weights='imagenet', include_top=False)

    # Parameter `train_conv_layers` (default False) determines whether or not
    # to train convolutional layers of the VGG16 model.
    if not train_conv_layers:
        for layer in initial_model.layers:
            layer.trainable = False

    # Three dense layer blocks with RELU activations, batch normalization, and
    # 50% dropout rate. Final layer is a single fully connected output unit.
	x = Flatten()(initial_model(input))

    """
	x = Dense(1000, activation='relu')(x)
	x = BatchNormalization()(x)
	x = Dropout(0.5)(x)

	x = Dense(1000, activation='relu')(x)
	x = BatchNormalization()(x)
	x = Dropout(0.5)(x)
    """

    x = Dense(1250, activation='relu')(x)
    x = BatchNormalization()(x)
    x = Dropout(0.5)(x)

    # If using multi class labels, make sure to either set this to a dense
    # layer with 14 units or load one of the multi class models already saved
    # at /home/aicg2/group2/model/saved_models/multi_class/.
    x = Dense(1, activation='linear')(x)

    model = Model(inputs=input, outputs=x)
    model.compile(loss='mse', optimizer='adam', metrics=[round_mae, 'mae'])

    print(model.summary())

    return model


def train_model(dataset, epochs):
    """ Sets paths to training and validation labels, creates data generators,
        defines callbacks, and then runs fit_generator to simultaneously train
        and validate. """

    def batcherator(chunk_size, mode, labels):
        """ Generator that yields chunks of training data with their labels or
            validation data with their labels. """

        labels = np.genfromtxt(labels, dtype=int)
        chunk_start = 0
        data = next = np.array([1])

        with h5py.File(data_file, 'r') as f:
            while True:
                if mode is 'train':
                    data = f[dataset]['train'][chunk_start:chunk_start + chunk_size]
                    next =  f[dataset]['train'][chunk_start + chunk_size:chunk_start + (2*chunk_size)]
                elif mode is 'val':
                    data = f[dataset]['val'][chunk_start:chunk_start + chunk_size]
                    next =  f[dataset]['val'][chunk_start + chunk_size:chunk_start + (2*chunk_size)]

                data_labels = labels[chunk_start:chunk_start + chunk_size]
                chunk_start += chunk_size
                data = np.true_divide(data, 255)

                # If on the last batch of training or validation data, reset
                # `chunk_start` for next epoch.
                if not next.size:
                    chunk_start = 0

                yield data, data_labels

    # Sets the path to training and validation labels for single class
    # (all vehicle objects) models...change `label_path` at the bottom to
    # '../multi_class_labels/' to train on all 14 classes -- make sure to also
    # either load a multi class model or change the final dense layer in
    # `initialize_model` to have 14 units.
    train_labels = label_path + '{}_train_labels.txt'.format(dataset)
    val_labels = label_path + '{}_val_labels.txt'.format(dataset)

    # Creates generators for training and validation data...
    # `chunk_size` * `steps_per_epoch`/`validation_steps`
    # (for train_gen and val_gen respectively) should be equal to or slightly
    # less than the total number of training/validation instances. Adjust
    # `chunk_size` to conform with memory constraints of your system.
    train_gen = batcherator(chunk_size=5, mode='train', labels=train_labels)
    val_gen = batcherator(chunk_size=5, mode='val', labels=val_labels)

    # Stop training if loss value does not improve after two epochs.
    early_stop = EarlyStopping(patience=2)
    # Save model after each epoch only if the loss value is the best yet.
    checkpoint = ModelCheckpoint('checkpoint.h5', save_best_only=True)

    model.fit_generator(
                generator=train_gen,
                steps_per_epoch=11897,
                validation_data=val_gen,
                validation_steps=3855,
                epochs=epochs,
                verbose=1,
                callbacks=[early_stop, checkpoint]
                )


def evaluate_model(dataset):
    """ Evaluate model on a given dataset's validation data subset. """

    def batcherator(chunk_size, labels):

        labels = np.genfromtxt(labels, dtype=int)
        chunk_start = 0
        data = next = np.array([1])

        with h5py.File(data_file, 'r') as f:
            while True:
                data = f[dataset]['val'][chunk_start:chunk_start + chunk_size]
                next =  f[dataset]['val'][chunk_start + chunk_size:chunk_start + (2*chunk_size)]

                data_labels = labels[chunk_start:chunk_start + chunk_size]
                chunk_start += chunk_size
                data = np.true_divide(data, 255)

                if not next.size:
                    chunk_start = 0

                yield data, data_labels

    val_labels = label_path + '{}_val_labels.txt'.format(dataset)
    val_gen = batcherator(chunk_size=5, labels=val_labels)

    print "Mean squared error: {}\nRounded mean absolute error: {}\nMean absolute error: {}".format(*model.evaluate_generator(generator=val_gen, steps=3855))

if __name__ == '__main__':

    # Set these data file and label directory variables for your system. Labels
    # should be included in this package, but the data file is remote
    # (it's nearly 134GBs).
    #
    # This code expects `data.h5` to be an HDF file with the following design:
    # {
    #   'aic540': {
    #       'train': ndarray.shape=(59482, 540, 960, 3),
    #       'val': ndarray.shape=(19272, 540, 960, 3)
    #       },
    #   'aic480': {
    #       'train': ndarray.shape=(7640, 480, 720, 3),
    #       'val': ndarray.shape=(3372, 480, 720, 3)
    #       }
    # }
    #
    # Set `label_path` to 'labels/multi_class_labels/' to train on the 14 class
    # labels instead of the single aggregated vehicle count labels.
    data_file = '/home/aicg2/data/data.h5'
    label_path = 'labels/single_class_labels/'
    dataset = 'aic540'

    # Creates a new model if `saved_model.h5` does not exist in the current
    # directory. Otherwise loads the saved_model.
    if not os.path.isfile('checkpoint.h5'):
        if dataset is 'aic540':
            model = initialize_model(image_shape=(540, 960, 3), train_conv_layers=False)
        elif dataset is 'aic480':
            model = initialize_model(image_shape=(480, 720, 3), train_conv_layers=False)
    else:
        model = load_model('checkpoint.h5', custom_objects={'round_mae': round_mae})
        print model.summary()

    #train_model(dataset=dataset, epochs=10)
    #evaluate_model(dataset=dataset)
