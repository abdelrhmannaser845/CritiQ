import tensorflow as tf
from tensorflow.keras import layers, models


NUM_WORDS = 10000
MAX_LEN = 200
MODEL_PATH = "sentiment_model.keras"


def build_model():
    model = models.Sequential(
        [
            layers.Embedding(NUM_WORDS, 16, input_length=MAX_LEN),
            layers.GlobalAveragePooling1D(),
            layers.Dense(16, activation="relu"),
            layers.Dense(1, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=["accuracy"],
    )

    return model


def train_and_save():
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.imdb.load_data(
        num_words=NUM_WORDS
    )

    x_train = tf.keras.preprocessing.sequence.pad_sequences(x_train, maxlen=MAX_LEN)
    x_test = tf.keras.preprocessing.sequence.pad_sequences(x_test, maxlen=MAX_LEN)

    model = build_model()
    model.fit(x_train, y_train, epochs=10, validation_split=0.2)

    _test_loss, test_accuracy = model.evaluate(x_test, y_test)
    print(f"Test accuracy: {test_accuracy:.4f}")

    model.save(MODEL_PATH)


if __name__ == "__main__":
    train_and_save()
