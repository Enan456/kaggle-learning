from __future__ import print_function

import math

from IPython import display
from matplotlib import cm
from matplotlib import gridspec
import sklearn 
from sklearn import metrics as metricsC
import tensorflow as tf
from tensorflow.python.data import Dataset
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import random
#ln 6-7 in order to have it work in a file think and not ipython
""" from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline') """

#load datasets
data_train = pd.read_csv('train.csv')
data_test = pd.read_csv('test.csv')

data_train.sample(3)

#clean data
def simplify_ages(df):
    df.Age = df.Age.fillna(-0.5)
    bins = (-1, 0, 5, 12, 18, 25, 35, 60, 120)
    group_names = ['Unknown', 'Baby', 'Child', 'Teenager', 'Student', 'Young Adult', 'Adult', 'Senior']
    categories = pd.cut(df.Age, bins, labels=group_names)
    df.Age = categories
    return df

def simplify_cabins(df):
    df.Cabin = df.Cabin.fillna('N')
    df.Cabin = df.Cabin.apply(lambda x: x[0])
    return df

def simplify_fares(df):
    df.Fare = df.Fare.fillna(-0.5)
    bins = (-1, 0, 8, 15, 31, 1000)
    group_names = ['Unknown', '1_quartile', '2_quartile', '3_quartile', '4_quartile']
    categories = pd.cut(df.Fare, bins, labels=group_names)
    df.Fare = categories
    return df

def format_name(df):
    df['Lname'] = df.Name.apply(lambda x: x.split(' ')[0])
    df['NamePrefix'] = df.Name.apply(lambda x: x.split(' ')[1])
    return df    
    
def drop_features(df):
    return df.drop(['Ticket', 'Name', 'Embarked'], axis=1)

def transform_features(df):
    df = simplify_ages(df)
    df = simplify_cabins(df)
    df = simplify_fares(df)
    df = format_name(df)
    df = drop_features(df)
    return df


#data display
fig, axs = plt.subplots(ncols=3)

sns.barplot(x="Embarked", y="Survived", hue="Sex", data=data_train, ax = axs[0])
data_train = transform_features(data_train)
data_test = transform_features(data_test)
data_train.head()
sns.pointplot(x="Pclass", y="Survived", hue="Sex", data=data_train, palette={"male": "blue", "female": "pink"}, markers=["*", "o"], linestyles=["-", "--"], ax = axs[1])
sns.pointplot(x="Age", y="Survived", hue="Sex", data=data_train, palette={"male": "blue", "female": "pink"}, markers=["*", "o"], linestyles=["-", "--"], ax = axs[2])
export_csv = data_train.to_csv (r'/home/enron/Documents/kaggle-learning/titanic/csv_dump/cleaned.csv', index = None, header=True)
plt.show()


####################################################################################################################################
#enter tensorflow
def data_fill_empty(df_temp):
  #pass ARGS [panda Dataframe]
  #return filled dataframe
  df_temp.fillna(-1)
  return df_temp


pd.options.display.max_rows = 10
pd.options.display.float_format = '{:.1f}'.format

cDataset = pd.read_csv('train.csv')

cDataset = cDataset.reindex(
    np.random.permutation(cDataset.index))

#set customs 
outputTargetVal = "Survived"
cPeriods = 10
cShuffle = 10000
training_count = 600
testing_count = 290
"""Transfer feature set from columns as input layers"""

def preprocess_features(cDataset):
  """Prepares input features from  data set.

  Args:
    cDataset: A Pandas DataFrame expected to contain data
      from the  data set.
  Returns:
    A DataFrame that contains the features to be used for the model, including
    synthetic features.
  """
  selected_features = cDataset[
    ["Pclass",
     "PassengerId",
     "Age",
     "SibSp",
     "Parch",
     "Fare",
     "Sex",
     "Ticket",
     "Embarked"]]
  processed_features = selected_features.copy()
  # Create a synthetic feature.
  return processed_features

def preprocess_targets(cDataset):
  """Prepares target features (i.e., labels) from  data set.
	Args:
    cDataset: A Pandas DataFrame expected to contain data
      from the  data set.
  Returns:
    A DataFrame that contains the target feature.
  """
  output_targets = pd.DataFrame()
  return output_targets



# Choose the first 12000 (out of 17000) examples for training.

training_examples = data_fill_empty(cDataset.head(training_count))
training_targets = data_fill_empty(cDataset.head(training_count))

# Choose the last 5000 (out of 17000) examples for validation.
validation_examples = data_fill_empty(cDataset.tail(testing_count))
validation_targets = data_fill_empty(cDataset.tail(testing_count))

# Double-check that we've done the right thing.
print("Training examples summary:")
print(training_examples)
display.display(training_examples.describe())
print("Validation examples summary:")
display.display(validation_examples.describe())

print("Training targets summary:")
export_csv = training_targets.to_csv (r'/home/enron/Documents/kaggle-learning/titanic/csv_dump/training_targets.csv', index = None, header=True)
display.display(training_targets.describe())
print("Validation targets summary:")
display.display(validation_targets.describe())

"""## Building a Neural Network

The NN is defined by the [DNNRegressor](https://www.tensorflow.org/api_docs/python/tf/estimator/DNNRegressor) class.

Use **`hidden_units`** to define the structure of the NN.  The `hidden_units` argument provides a list of ints, where each int corresponds to a hidden layer and indicates the number of nodes in it.  For example, consider the following assignment:

`hidden_units=[3,10]`

The preceding assignment specifies a neural net with two hidden layers:

* The first hidden layer contains 3 nodes.
* The second hidden layer contains 10 nodes.
"""

def construct_feature_columns(input_features):
  """Construct the TensorFlow Feature Columns.

  Args:
    input_features: The names of the numerical input features to use.
  Returns:
    A set of feature columns
  """ 
  return set([tf.feature_column.numeric_column(my_feature)
              for my_feature in input_features])

def my_input_fn(features, targets, batch_size=1, shuffle=True, num_epochs=None):
    """Trains a neural net regression model.
  
    Args:
      features: pandas DataFrame of features
      targets: pandas DataFrame of targets
      batch_size: Size of batches to be passed to the model
      shuffle: True or False. Whether to shuffle the data.
      num_epochs: Number of epochs for which data should be repeated. None = repeat indefinitely
    Returns:
      Tuple of (features, labels) for next data batch
    """
    
    # Convert pandas data into a dict of np arrays.
    features = {key:np.array(value) for key,value in dict(features).items()}                                             
 
    # Construct a dataset, and configure batching/repeating.
    ds = Dataset.from_tensor_slices((features,targets)) # warning: 2GB limit
    ds = ds.batch(batch_size).repeat(num_epochs)
    
    # Shuffle the data, if specified.
    if shuffle:
      ds = ds.shuffle(cShuffle)
    
    # Return the next batch of data.
    features, labels = ds.make_one_shot_iterator().get_next()
    return features, labels

def train_nn_regression_model(
    learning_rate,
    steps,
    batch_size,
    hidden_units,
    training_examples,
    training_targets,
    validation_examples,
    validation_targets):
  """Trains a neural network regression model.
  
  In addition to training, this function also prints training progress information,
  as well as a plot of the training and validation loss over time.
  
  Args:
    learning_rate: A `float`, the learning rate.
    steps: A non-zero `int`, the total number of training steps. A training step
      consists of a forward and backward pass using a single batch.
    batch_size: A non-zero `int`, the batch size.
    hidden_units: A `list` of int values, specifying the number of neurons in each layer.
    training_examples: A `DataFrame` containing one or more columns from
      `cDataset` to use as input features for training.
    training_targets: A `DataFrame` containing exactly one column from
      `cDataset` to use as target for training.
    validation_examples: A `DataFrame` containing one or more columns from
      `cDataset` to use as input features for validation.
    validation_targets: A `DataFrame` containing exactly one column from
      `cDataset` to use as target for validation.
      
  Returns:
    A `DNNRegressor` object trained on the training data.
  """

  periods = cPeriods
  steps_per_period = steps / periods
  
  # Create a DNNRegressor object.
  my_optimizer = tf.train.GradientDescentOptimizer(learning_rate=learning_rate)
  my_optimizer = tf.contrib.estimator.clip_gradients_by_norm(my_optimizer, 5.0)
  dnn_regressor = tf.estimator.DNNRegressor(
      feature_columns=construct_feature_columns(training_examples),
      hidden_units=hidden_units,
      optimizer=my_optimizer,
  )
  
  # Create input functions.
  training_input_fn = lambda: my_input_fn(training_examples, 
                                          training_targets[outputTargetVal], 
                                          batch_size=batch_size)
  predict_training_input_fn = lambda: my_input_fn(training_examples, 
                                                  training_targets[outputTargetVal], 
                                                  num_epochs=1, 
                                                  shuffle=False)
  predict_validation_input_fn = lambda: my_input_fn(validation_examples, 
                                                    validation_targets[outputTargetVal], 
                                                    num_epochs=1, 
                                                    shuffle=False)

  # Train the model, but do so inside a loop so that we can periodically assess
  # loss metrics.
  print("Training model...")
  print("RMSE (on training data):")
  training_rmse = []
  validation_rmse = []
  for period in range (0, periods):
    # Train the model, starting from the prior state.
    dnn_regressor.train(
        input_fn=training_input_fn,
        steps=steps_per_period
    )
    # Take a break and compute predictions.
    training_predictions = dnn_regressor.predict(input_fn=predict_training_input_fn)
    training_predictions = np.array([item['predictions'][0] for item in training_predictions])
    
    validation_predictions = dnn_regressor.predict(input_fn=predict_validation_input_fn)
    validation_predictions = np.array([item['predictions'][0] for item in validation_predictions])
    
    # Compute training and validation loss.
    training_root_mean_squared_error = math.sqrt(
        metricsC.mean_squared_error(training_predictions, training_targets))
    validation_root_mean_squared_error = math.sqrt(
        metricsC.mean_squared_error(validation_predictions, validation_targets))
    # Occasionally print the current loss.
    print("  period %02d : %0.2f" % (period, training_root_mean_squared_error))
    # Add the loss metrics from this period to our list.
    training_rmse.append(training_root_mean_squared_error)
    validation_rmse.append(validation_root_mean_squared_error)
  print("Model training finished.")

  # Output a graph of loss metrics over periods.
  plt.ylabel("RMSE")
  plt.xlabel("Periods")
  plt.title("Root Mean Squared Error vs. Periods")
  plt.tight_layout()
  plt.plot(training_rmse, label="training")
  plt.plot(validation_rmse, label="validation")
  plt.legend()

  print("Final RMSE (on training data):   %0.2f" % training_root_mean_squared_error)
  print("Final RMSE (on validation data): %0.2f" % validation_root_mean_squared_error)

  return dnn_regressor

#run regressor
training_examples = training_examples.fillna("unknown")
training_targets = training_targets.fillna("unknown")
validation_examples = validation_examples.fillna("unknown")
validation_targets = validation_targets.fillna("unknown")
export_csv = training_targets.to_csv (r'/home/enron/Documents/kaggle-learning/titanic/csv_dump/pre_dnn_training_targets.csv', index = None, header=True)
export_csv = validation_examples.to_csv (r'/home/enron/Documents/kaggle-learning/titanic/csv_dump/pre_dnn_validation_examples.csv', index = None, header=True)
export_csv = validation_targets.to_csv (r'/home/enron/Documents/kaggle-learning/titanic/csv_dump/pre_dnn_validation_target.csv', index = None, header=True)

dnn_regressor = train_nn_regression_model(learning_rate=0.02, steps=10,
    batch_size=10, hidden_units=[8, 6, 4, 2], 
    training_examples=training_examples, training_targets=training_targets,
    validation_examples=validation_examples, validation_targets=validation_targets)

"""Validation/testing"""

california_housing_test_data = pd.read_csv("https://download.mlcc.google.com/mledu-datasets/california_housing_test.csv", sep=",")

test_examples = preprocess_features(california_housing_test_data)
test_targets = preprocess_targets(california_housing_test_data)

predict_testing_input_fn = lambda: my_input_fn(test_examples, 
                                               test_targets[outputTargetVal], 
                                               num_epochs=1, 
                                               shuffle=False)

test_predictions = dnn_regressor.predict(input_fn=predict_testing_input_fn)
test_predictions = np.array([item['predictions'][0] for item in test_predictions])

root_mean_squared_error = math.sqrt(
    metrics.mean_squared_error(test_predictions, test_targets))

print("Final RMSE (on test data): %0.2f" % root_mean_squared_error)
