PRMD is set of four half-pyramid objects scattered around a dace floor. This repository hosts the majority of the code that generates the visuals (as inputs to LEDs) through four FadeCandy devices.

The basic flow is:
1. AudioInput: listens on input devices, reads audio in chunks and extracts audio features.


## Requirements
1. Aubio, needs to be compiled + the python installation and setting that lib folder
2. install the requirements.txt file using `pip install -r requirements.txt`
