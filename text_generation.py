# https://www.tensorflow.org/tutorials/text/text_generation

import tensorflow as tf
import tensorflowjs as tfjs

import numpy as np
import os
import time

path_to_file = tf.keras.utils.get_file('shakespeare.txt', 'https://storage.googleapis.com/download.tensorflow.org/data/shakespeare.txt')

# Read, then decode for py2 compat.
text = open(path_to_file, 'rb').read().decode(encoding='utf-8')

# The unique characters in the file
vocab = sorted(set(text))

# Creating a mapping from unique characters to indices
char2idx = {u:i for i, u in enumerate(vocab)}
idx2char = np.array(vocab)

text_as_int = np.array([char2idx[c] for c in text])

# The maximum length sentence we want for a single input in characters
seq_length = 100
examples_per_epoch = len(text)//(seq_length+1)

# Create training examples / targets
char_dataset = tf.data.Dataset.from_tensor_slices(text_as_int)

sequences = char_dataset.batch(seq_length+1, drop_remainder=True)

def split_input_target(chunk):
	input_text = chunk[:-1]
	target_text = chunk[1:]
	return input_text, target_text

dataset = sequences.map(split_input_target)

# Batch size
BATCH_SIZE = 64

# Buffer size to shuffle the dataset
# (TF data is designed to work with possibly infinite sequences,
# so it doesn't attempt to shuffle the entire sequence in memory. Instead,
# it maintains a buffer in which it shuffles elements).
BUFFER_SIZE = 10000

dataset = dataset.shuffle(BUFFER_SIZE).batch(BATCH_SIZE, drop_remainder=True)

# Length of the vocabulary in chars
vocab_size = len(vocab)

# The embedding dimension
embedding_dim = 256

# Number of RNN units
rnn_units = 1024

EPOCHS=10

model = tf.keras.models.load_model('generation.h5')

model.summary()

def generate_text(start_string, model=model):
	# Evaluation step (generating text using the learned model)

	# Number of characters to generate
	num_generate = 1000

	# Converting our start string to numbers (vectorizing)
	input_eval = [char2idx[s] for s in start_string]
	input_eval = tf.expand_dims(input_eval, 0)

	# Empty string to store our results
	text_generated = []

	# Low temperatures results in more predictable text.
	# Higher temperatures results in more surprising text.
	# Experiment to find the best setting.
	temperature = 1.0

	# Here batch size == 1
	model.reset_states()
	for i in range(num_generate):
		predictions = model(input_eval)
		# remove the batch dimension
		predictions = tf.squeeze(predictions, 0)

		# using a categorical distribution to predict the character returned by the model
		predictions = predictions / temperature
		predicted_id = tf.random.categorical(predictions, num_samples=1)[-1,0].numpy()

		# We pass the predicted character as the next input to the model
		# along with the previous hidden state
		input_eval = tf.expand_dims([predicted_id], 0)

		text_generated.append(idx2char[predicted_id])
		
	return (start_string + ''.join(text_generated))