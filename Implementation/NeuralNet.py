from __future__ import absolute_import, division, print_function

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from numpy.random import seed
from tensorflow import set_random_seed
set_random_seed(2)
seed(2)

import tensorflow as tf
from tensorflow import keras
from tensorflow.python import keras

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
    plt.ylabel('Mean Square Error [$MPG^2$]')
    plt.plot(hist['epoch'], hist['mean_squared_error'],
             label='Train Error')
    plt.plot(hist['epoch'], hist['val_mean_squared_error'],
             label='Val Error')
    plt.ylim([0, 20])
    plt.legend()
    plt.show()



def norm(x):
    return (x - train_stats['mean']) / train_stats['std']


# Creates a 3 layer dense neural network. Layer 1 and 2 are hidden layers. Layer 3 is the output layer.
def build_model():
    model = keras.Sequential([
        keras.layers.Dense(64, activation=tf.nn.relu, input_shape=[len(train_dataset.keys())]),
        keras.layers.Dense(64, activation=tf.nn.relu),
        keras.layers.Dense(1),
  ])
    keras.backend.set_epsilon(1)
    model.compile(loss='mse', optimizer='adam', metrics=['acc','cosine'])

    return model


resultsPath = "C:\\Users\\Leuma\\Documents\\results\\dataset.csv"

col_names = ["numberOfOccupants","isRoomOccupied","co2Level"]
raw_dataset = pd.read_csv(resultsPath, names=col_names, na_values="?", comment='\t',
                      sep=";", skipinitialspace=True)

dataset = raw_dataset.copy()

train_dataset = dataset.sample(frac=0.8,random_state=0)
test_dataset = dataset.drop(train_dataset.index)

train_stats = train_dataset.describe()
test_labels = test_dataset.pop('numberOfOccupants')
train_labels = train_dataset.pop('numberOfOccupants')

sns.pairplot(train_dataset[["co2Level", "isRoomOccupied"]], diag_kind="kde")
train_stats = train_stats.transpose()

print(test_dataset)

model = build_model()
model.summary()

example_batch = train_dataset[:10]
print(example_batch)
example_result = model.predict(example_batch)
print(example_result)


class PrintDot(keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs):
    if epoch % 100 == 0: print('')
    print('.', end='')

EPOCHS = 2000
history = model.fit(train_dataset, train_labels, epochs=EPOCHS,
                    validation_split = 0.2, verbose=0, callbacks=[PrintDot()])
keras.callbacks.EarlyStopping(monitor='val_loss', patience=0, verbose=0, mode='auto')

scores = model.evaluate(test_dataset, test_labels, verbose=1)

print("\nNUMBER OF EPOCHS: " + str(EPOCHS))
print("Accuracy: %.2f%%" % (scores[1]*100))


