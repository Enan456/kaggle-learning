import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
#ln 6-7 in order to have it work in a file think and not ipython
from IPython import get_ipython
get_ipython().run_line_magic('matplotlib', 'inline')

#load datasets
data_train = pd.read_csv('train.csv')
data_test = pd.read_csv('test.csv')

data_train.sample(3)