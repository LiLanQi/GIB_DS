# Molecular Interaction Prediction Task

### Download and Create datasets

Here we have provided you with the relevant dataset. If an error occurs during the processing of the dataset or if you want to re-download and process it again, please refer to the following steps:

- Download Chromophore dataset from https://figshare.com/articles/dataset/DB_for_chromophore/12045567/2, and leave only **Absorption max (nm)**,  **Emission max (nm)**, and **Lifetime (ns)** column.
    - Make separate csv file for each column, and erase the NaN values for each column.
    - We log normalize the target value for **Lifetime (ns)** data due to its high skewness.
- Download Solvation Free Energy datasets from https://www.sciencedirect.com/science/article/pii/S1385894721008925#appSB, and create the dataset based on the **Source_all** column in the excel file.
    - Make separate csv file for each data source.
- Put each datasets into ``data/raw`` and run ``data.py`` file.
- Then, the python file will create ``{}.pt`` file in ``data/processed``.

### Hyperparameters
Following Options can be passed to `main.py`

`--dataset:`
Name of the dataset. Supported names are: AP_dataset, CB_dataset, FS_dataset, TUM, CHAB, CHEM, CHLT, and CombiSolv. Usually, you just need to keep the name consistent with the dataset name. Here, Fs_dataset=FreeSolv,

AP_dataset=Abraham,CB_dataset=CompSol,CHAB=Absorption,CHEM=Emission,CHLT=Lifetime.

You could add another Dataset.

usage example :`--dataset chr_abs`

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

