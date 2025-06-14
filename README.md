# CelebrityTTS
<img src="tts_demo.gif" width="900" />

## Overview
 - This python project integrates neural network models I trained utilizing the PyTorch TacoTron 2/Wavenet architecture for voice synthesis from text. It includes an interactive GUI, which allows users to input their own text and have it be read out by a chosen celebrity. 
 - Furthermore, it integrates functionality of the Streamlabs API, a popular software platform that live streamers use for managing their stream. My program allows the user to connect to the Streamlab's API to have the live streamers donations be read out by a chosen celebrity. 
 - There are three voices which are available, one being a default voice created using the LJ Speech Dataset which can be found [here](https://keithito.com/LJ-Speech-Dataset/). The two other voices are Elon Musk, and a fairly popular live streamer called Trainwrecks since this application was originally tailored towards live streamers. Both of these were trained from custom datasets I created.

## Implementation
First in order to create the training data for the celebrities' voices, I gathered large amounts of clear audio from online sources and split them into hundreds of distinct clips. Then, I transcribed these clips into a CSV file and trained the neural network on a Linux machine using an NVIDIA GPU. I then used these models for generating the speech from the text. The GUI is created using a Python library called Tkinter. The program separates the multithreaded GUI application and the voice generation into two separate processes using multiprocessing, due to the voice generation being very CPU intensive. The GUI application has two tabs, one managing the speech thats being generated, and the other for connecting to the Streamlabs API and showing donation logs. The program processes the donations received from the API and adds them to a multiprocessor queue which allows inter process communication between the audio generation process and Tkinter process. The audio process generates the audio one donation at a time, and changes flags in a multiprocessor dictionary in order to change the state of the GUI. Lastly, the donations are processed/cleaned and error handling is put into place since the donations are open for any viewer of the live stream.

## Installation
1. Clone this repository using "git clone git@github.com:brycerichards13/CelebrityTTS.git"
1. Download anaconda, a python package manager, which can be found here: https://www.anaconda.com/download
2. Create a conda environment, and activate it
3. Run the command "python Installer.py"
4. Launch the GUI using the command, "python gui.pyw"

## Background
This project was originally an idea of mine that I had before I ever wanted to do computer science in college. I knew nothing about the field, but I wanted to make my idea a reality. So I started learning python and tried to make it myself. Since then I have learned a lot through college and personal experience. The first version of this program was written at an obviously novice level, but since then I have rewritten it and uploaded it github. This project is special to me, because trying to turn this idea into reality made me want to go into the field and create something of my own. I hope you enjoy!
