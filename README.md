
Project Presentation:


https://user-images.githubusercontent.com/47524721/173060907-76960106-13e9-4b3f-9867-2a31a01cc2ee.mp4



## Installation Guide

This sonification software is best used with headphones.

First, to download the code to the software
```bash
git clone https://github.com/ScottWilliamAnderson/FloorPlanSonification.git
```


To use only the demo floor plan sonification (does not require a CUDA compatible GPU)
- Please install Python 3.6.1
  - The easiest way to do this is using a conda environment, using the command:
  ```bash
	conda create --name CONDAENVIRONMENTNAME python=3.6.1
	```

- Please install the python modules found in /reqs/requirements.txt
    ```bash
	pip install -r reqs/requirements.txt
	```
	or
	```bash
	conda install --file reqs/requirements.txt
	```

To also use the Sonification tool with any floor plan you wish: (requires a CUDA compatible GPU: https://developer.nvidia.com/cuda-gpus)
- Please install CUDA version 10.0, from the following link:
	- https://developer.nvidia.com/cuda-10.0-download-archive
- Please install a version of cuDNN compatible with CUDA 10.0
	- https://developer.nvidia.com/rdp/cudnn-archive
- To manually verify you have the required .dll files to run the model, navigate to 
  -  \Program Files\NVIDIA GPU Computing Toolkit\CUDA\v10.0\bin (or equivalent)
- You should see the following files included in the folder:
	- cudart64_100.dll
	- nvcuda.dll
	- cublas64_100.dll
	- cufft64_100.dll
	- curand64_100.dll
	- cusolver64_100.dll
	- cusparse64_100.dll
	- cudnn64_7.dll
	- cudart64_100.dll
	- cublas64_100.dll
	- cufft64_100.dll
	- curand64_100.dll
	- cusolver64_100.dll
	- cusparse64_100.dll

- Please also ensure the native text-to-speech system for your operating system is currently downloaded

## User Guide
- You may only use this software with floor plans you have the license or permission to use.
- to run the downloaded Floor Plan Sonification tool:
    ```bash
	python run.py
	```

The software should start fullscreen, and two buttons should be available on a white background:
1. Use Example Floor Plan

2. Upload a Floor Plan

If you don't have a CUDA-enabled GPU, select "Use Example Floor Plan"
If you wish to use your CUDA-enabled GPU to sonify a floor plan of your choosing, select "Upload a Floor Plan". This will prompt you to provide the path to the floor plan image.

When the software has prepared the floor plan for sonification, you can use your mouse (or tap on touch enabled devices) to click anywhere on the generated floor plan (visible on the left half of the screen).

This should display a hat icon on the location where you are "listening" to the surrounding area
Your location information, and room that you are in will be played through your headset.
The surrounding doors and windows will be represented through directional sound, to indicate where they are in location to you.

- To rotate your head counter-clockwise by 90 degrees press *Q*

- To rotate your head clockwise by 90 degrees press *E*

To exit the program, press *esc*

A good way to map out the floor plan in your mind: try listening in each room!

