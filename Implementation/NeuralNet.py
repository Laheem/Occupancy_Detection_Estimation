from __future__ import absolute_import, division, print_function

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from numpy.random import seed
from tensorflow import set_random_seed
import tensorflow as tf
from tensorflow import keras
from tensorflow.python import keras


# Set the machine learning seeds to predetemined values to allow for reproducible results.
set_random_seed(2)
seed(2)
DATASET_PATH = None
EPOCHS = 2000


# Can be used to create a plot function of the attributes returned by the model.
def plot_history(history):
    hist = pd.DataFrame(history.history)
    hist['epoch'] = history.epoch

    plt.figure()
    plt.xlabel('Epoch')
    plt.ylabel('Mean Abs Error [Occupants]')
    plt.plot(hist['epoch'], hist['mean_absolute_error'],
             label='Train Error')
    plt.plot(hist['epoch'], hist['val_mean_absolute_error'],
             label='Val Error')
    plt.ylim([0, 5])
    plt.legend()

    plt.figure()
    plt.xlabel('Epoch')
    plt.plot(hist['epoch'], hist['mean_squared_error'],
             label='Train Error')
    plt.plot(hist['epoch'], hist['val_mean_squared_error'],
             label='Val Error')
    plt.ylim([0, 20])
    plt.legend()
    plt.show()

# Normalises the results to increase the accuracy of prediction from the model.
def norm(x):
    return (x - train_stats['mean']) / train_stats['std']


# Creates a 3 layer dense neural network. Layer 1 and 2 are hidden layers. Layer 3 is the output layer.
def build_model():
    model = keras.Sequential([
        keras.layers.Dense(64, activation=tf.nn.relu, input_shape=[len(train_dataset.keys())]),
        keras.layers.Dense(64, activation=tf.nn.relu),
        keras.layers.Dense(1),
  ])
    # Fixes a bug relating to weird MSE results.
    keras.backend.set_epsilon(1)
    model.compile(loss='mse', optimizer='adam', metrics=['acc','cosine'])

    return model

# Pulls a CSV file from the target path and parses it given the names below.
resultsPath = DATASET_PATH

col_names = ["numberOfOccupants","isRoomOccupied","co2Level"]
raw_dataset = pd.read_csv(resultsPath, names=col_names, na_values="?", comment='\t',
                      sep=";", skipinitialspace=True)

# Copy the dataset into a training set, and get 80% of it for training purposes.
dataset = raw_dataset.copy()

train_dataset = dataset.sample(frac=0.8,random_state=0)
test_dataset = dataset.drop(train_dataset.index)

# Remove the number of occupants from the testing and training dataset for future purposes.
train_stats = train_dataset.describe()
test_labels = test_dataset.pop('numberOfOccupants')
train_labels = train_dataset.pop('numberOfOccupants')

sns.pairplot(train_dataset[["co2Level", "isRoomOccupied"]], diag_kind="kde")
train_stats = train_stats.transpose()

# Build a model based on the parameters passed in and show a summary of the data provided.
model = build_model()
model.summary()

# Create a validation set of the data, and attempt to predict the number of occupants based off of CO2
example_batch = train_dataset[:10]
example_result = model.predict(example_batch)


# Prints a dot on every epoch trained.
class PrintDot(keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs):
    if epoch % 100 == 0: print('')
    print('.', end='')

# Attempt to use the model to predict the remaining 20% of data over a specified number of epochs.
history = model.fit(train_dataset, train_labels, epochs=EPOCHS,
                    validation_split = 0.2, verbose=0, callbacks=[PrintDot()])
# Give up after a while if no noticeable improvements to the model can be made, to avoid overfitting.
keras.callbacks.EarlyStopping(monitor='val_loss', patience=0, verbose=0, mode='auto')

# Get a result based on the results of the model against the validation set. 
scores = model.evaluate(test_dataset, test_labels, verbose=1)

print("\nNUMBER OF EPOCHS: " + str(EPOCHS))
print("Accuracy: %.2f%%" % (scores[1]*100))


