# LOP_database

## Installation

### Pre-requisite
You need to install :
- Numpy, the basic package for scientific computing with Python (http://www.numpy.org/)
- Mido, a python library for Midi files processing (https://mido.readthedocs.io/en/latest/)
- GCC

### Automatic alignement function
The automatic alignement function is coded in C and need to be compiled using the following commands :

    cd LOP_database/utils/Needleman/
    python setup.py build

The a .so file is created in build/"some-path"/needleman_chord.so
Copy it to the utils folder :

    cp LOP_database/utils/Needleman/build/"some-path"/needleman_chord.so LOP_database/utils/



### Add the library to the python path
Simply add the repository to your Python path :
    
    export PYTHONPATH=$PYTHONPATH:/path/to/downloaded_git_repo

It can be added either temporarilly by taping this command in a terminal or permanently by copying it to your ~/.bashprofile file

## Use
Once the repository is added to your python path, all its function will be accessible through the *LOP_database* package.

The *main.py* file at the root of the LOP_database folder allow you to take a database with the same structure as the LOP database one, and produce a version of this database containing automatically aligned midi files
