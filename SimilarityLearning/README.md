# Graph Similarity Learning Task

### Download and Create datasets

Here we have provided you with the relevant dataset. If an error occurs during the processing of the dataset or if you want to re-download and process it again, please refer to the following steps:

- Download AIDS OpenSSL dataset from https://github.com/cszhangzhen/H2MN.
- Download IMDB dataset from https://github.com/yunshengb/SimGNN.
- Put each datasets into ``datasets``.

### Hyperparameters
Following Options can be passed to `main_regression.py` and `main_classification.py`

`--dataset:`
Name of the dataset. Supported names are: AIDS700nef, IMDBMulti, and openssl_min50.  
usage example :`--dataset AIDS700nef`

`--lr:`
Learning rate for training the model.  
usage example :`--lr 0.001`

`--epochs:`
Number of epochs for training the model.  
usage example :`--epochs 500`

`--beta:`
Hyperparameters for balance the trade-off between prediction and compression. GIB_DS and CGIB all use it.  It's very important hyperparameters,usually set from 1e-1、1e-2... 1e-10 and 1.0、0
usage example :`--beta 1.0`

`--tau:`
Temperature hyperparameter for $\text{CGIB}_{\text{cont}}$.  Especially used to compare with GIB_DS.
usage example :`--tau 1.0`