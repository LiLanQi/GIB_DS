# Graph Information Bottleneck-Based Dual Subgraph Prediction for Molecular Interactions




## Overview
Recently, graph neural networks have achieved remarkable success in predicting molecular interactions. 

However, existing methodologies often fall short of comprehensively considering a pivotal factor influencing these interactions: the core subgraph within molecules, commonly represented by functional groups or atoms capable of engaging in interactions with other molecules. 

In this work, we propose a novel interaction prediction framework, called GIB-DS, which centers on the identification of the core subgraph in pairs of molecules to anticipate their interaction behavior. 

Guided by the principles of the Graph Information Bottleneck, our approach adeptly identifies two subgraphs within this pair of graphs that capture the essential information pertinent to the task at hand. 

We think that the dual-subgraph formulation could more faithfully capture the underlying nature of chemical reactions, where interactions between molecules and the interactions among specific atoms are inherently intertwined. 

Extensive experimentation across diverse datasets underscores the superiority of GIB-DS over state-of-the-art baselines, achieving an approximate 5% improvement. The proposed GIB-DS code will be released publicly.



### Requirements

- Python version: 3.8.15
- Pytorch version: 1.12.1
- RDKit version:2022.9.3
- scikit-learn version: 1.2.0
- torch-scatter version: 2.1.0+pt112cu113
- torch-cluster version: 1.6.0+pt112cu113
- torch-sparse versions: 0.6.16+pt112cu113
- torch-geometric version: 2.2.0
- texttable versions:1.7.0
- tensorboardX version: 2.6.2.2

### How to Run the code?

Please refer to the README.md file in each task folder for further instructions and details on how to run the code.



### How to set up the relevant environment?

Here, we take the example of running a similarity learning task

- First, you can build a relevant Conda environment with Python version 3.8 and torch version 1.12.1 by using the following commands

  ```python
  conda create -n GIB_DS python=3.8
  conda activate GIB_DS
  pip install torch==1.12.1+cu113 torchvision==0.13.1+cu113 torchaudio==0.12.1 --extra-index-url https://download.pytorch.org/whl/cu113
  ```

- After that, install the required Python libraries with the following commands. Note that the installation of the torch_geometric library is a bit more complicated, and you need to go to the corresponding website to download the whl file and then install it. Website :https://data.pyg.org/whl/. Here, we are using torch-geometric version 2.2.0, if it is any other version, you may get an error when you run the code.

  ```python
  pip install scikit-learn==1.2.0
  
  pip install torch_scatter-2.1.0+pt112cu113-cp38-cp38-linux_x86_64.whl
  pip install torch_sparse-0.6.16+pt112cu113-cp38-cp38-linux_x86_64.whl 
  pip install torch_cluster-1.6.0+pt112cu113-cp38-cp38-linux_x86_64.whl
  pip install torch-geometric==2.2.0
  
  pip install texttable
  
  pip install tensorboardX
  
  ```

- Finally, you can make a simple attempt with the following command:

  ```shell
  cd SimilarityLearning
  python main_classification.py
  ```

Here, the CUDA version of our machine is 11.4, if your version does not match, the configuration process needs to make relevant adjustments



## An Simple Example

```shell
cd SimilarityLearning
python main_classification.py
```

After that, the program runs normally.

Finally, a folder with the same name as the dataset will be generated in the 'results' directory, which contains the final generated files, such as 'GIB_DS.txt' and 'GIB_DS_total.txt'. The former contains the results of each experiment, while the latter includes the results averaged over multiple runs. The relevant content is as follows:

GIB_DS.txt:

```
--------------------------------------------------------------------------------- 
embedder_GIB_DS_dataset_openssl_min50_learning_rate_0.0001_beta_0.01
Loss : 0.1507 || AUC : 0.9886 
--------------------------------------------------------------------------------- 
--------------------------------------------------------------------------------- 
embedder_GIB_DS_dataset_openssl_min50_learning_rate_0.0001_beta_0.01
Loss : 0.1507 || AUC : 0.9886 
--------------------------------------------------------------------------------- 
--------------------------------------------------------------------------------- 
embedder_GIB_DS_dataset_openssl_min50_learning_rate_0.0001_beta_0.01
Loss : 0.1922 || AUC : 0.9812 
--------------------------------------------------------------------------------- 
--------------------------------------------------------------------------------- 
embedder_GIB_DS_dataset_openssl_min50_learning_rate_0.0001_beta_0.01
Loss : 0.1624 || AUC : 0.9861 
--------------------------------------------------------------------------------- 
--------------------------------------------------------------------------------- 
embedder_GIB_DS_dataset_openssl_min50_learning_rate_0.0001_beta_0.01
Loss : 0.2704 || AUC : 0.9592 
--------------------------------------------------------------------------------- 
```



GIB_DS_total.txt:

```
--------------------------------------------------------------------------------- 
embedder_GIB_DS_dataset_openssl_min50_learning_rate_0.0001_beta_0.01
Loss : 0.2030(0.0455) || AUC : 0.9763(0.0115) 
--------------------------------------------------------------------------------- 
```



To reproduce these results, navigate to the 'SimilarityLearning' folder and execute 'main_classification.py'. Set the number of epochs to 10,000, learning rate (lr) to 1e-4, dataset to 'openssl_min50', batch_size to 16, and beta to 0.01.

Inside the similarity task, only the openssl dataset corresponds to main_classification.py, the remaining 2 datasets correspond to main_regression.py


--------------------------------------------------------------------------------- 

### Note

The relevant configuration items are located in the corresponding parser.py or argument.py files, where you can modify various hyper-parameters, such as beta, learning rate, dataset, and so on.
