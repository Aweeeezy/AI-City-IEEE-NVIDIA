model.py
========================================

Required packages
----------------------------------
* Keras
* h5py
* numpy

How to run
-------------------
* the weights of our trained models exceed 1GB so they could not be uploaded to
  the repository
* go to main at the bottom of the script
* change the variable `data_file` to be the path to an hdf5 data file...this
  file's structure form is specified in the comments of the main and the script
  `make_HDF5.py` will create this data file
* the variables `label_path` and `dataset` should work as is, but if you want
  to run the model on the AIC480 dataset or run a multi class model instead,
  you will have to update them accordingly
* if a model checkpoint named `checkpoint.h5` exists in the current directory,
  it will be loaded -- otherwise a new model will be initialized
* uncomment one of the last two lines in order to train and/or evaluate the
  model respectively


make_HDF5.py
========================================

Required packages
----------------------------------
* scipy
* h5py
* numpy

How to run
-------------------
* this script must be run to recreate the data file as it is approximately
  134GB and could not be uploaded to github
* update the variable `root` to specify the directory of the environment in
  which the directories `data` and `datasets` exist
* will create a data file located at `<root>/data/data.h5`

regression_labeler.py
========================================

Required packages
----------------------------------
* numpy

How to run
-------------------
* this script shouldn't need to be run since the labels are included in this
  repository
* edit the list variable called `paths` so that the file path strings inside of
  it are paths to the training and validation labels for the AIC540 and AIC480
  datasets
