import numpy as np
import matplotlib.pyplot as plt
from skimage.transform import resize
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense
from tensorflow.keras.optimizers import SGD

def getModel(): 
    X_raw = np.load('X.npy')
    X_raw = X_raw/255.
    y = np.load('y.npy')
    X = []
    size = (28,28)
    for x in X_raw:
        X.append(resize(x, size))
    X = np.array(X)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

    bs = 16
    lr = 0.0005

    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(*size, 1)),
        MaxPooling2D(),
        Conv2D(64, (3, 3), activation='relu', padding='same'),
        MaxPooling2D(),
        Conv2D(128, (3, 3), activation='relu', padding='same'),
        MaxPooling2D(),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(10, activation='softmax')
    ])

    optimizer1 = SGD(learning_rate=lr)
    model.compile(optimizer=optimizer1, loss='sparse_categorical_crossentropy', metrics=['accuracy'])

    log = model.fit(X_train, y_train, batch_size=bs, epochs=400, validation_data=(X_test, y_test))
    #model.save('model.keras') #Remove this comment if you want to generate the model.keras 
    return model

