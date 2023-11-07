# Drug-Drug Interaction Prediction Task

### Download and Create datasets

Here we have provided you with the relevant dataset. If an error occurs during the processing of the dataset or if you want to re-download and process it again, please refer to the following steps:

- Download Drug-Drug Interaction dataset from https://github.com/isjakewong/MIRACLE/tree/main/MIRACLE/datachem.
- Put each datasets into ``data/raw`` and run ``data.py`` file.
- Then, the python file will create ``{}.pt`` file in ``data/processed``.

### Hyperparameters
Following Options can be passed to `main.py`

`--dataset:`
Name of the dataset. Supported names are: ZhangDDI, and ChChMiner.  
usage example :`--dataset ZhangDDI`

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