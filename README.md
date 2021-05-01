<h1>Two-way Indian sign language communication system using general adversarial networks and recurrent neural networks.</h1>

## Overview
This project proposes an implementation of generation and recognition of Indian sign language using Computer Vision and Natural Language Preprocessing. The intended end result of this project is to develop a communication system between an normal user not knowing Indian sign language and a specially-abled user having speech impairments.

## Dataset
The system uses video representation of words in Indian Sign Language as listed in the ISL dictionary. It consists of 2988 words, each word has two instances. You can download complete [dataset](https://drive.google.com/drive/folders/1bnnpumQFlEXKyx1jS2Qq7-K_u5heJgQU?usp=sharing)

## Setup
1. Install the dependencies mentioned in `requirements.txt` to run this project.
2. **For Sign generation**
- Build [Openpose](https://github.com/CMU-Perceptual-Computing-Lab/openpose#installation)
- Download the Stanford parser folder from the [drive link](https://drive.google.com/drive/folders/1xxxyj90SUK_fqjo_S-DW-jfMoHBcjbre) and place it in the main project repository. It is used in `text-parser.py` to translate input  sentences to gloss sequences.
- Download the pre-trained [checkpoint folder](https://drive.google.com/drive/folders/1MtvtGxfR93cT2yLNKRaD97l-Nlw-6wSh?usp=sharing), [all-frames-gen](https://drive.google.com/drive/folders/1c4sGre9983FCpBMOZpNPKZNY6Z5sqHvt?usp=sharing) folder to run the generation and save all these folders in the main project repository. If you want to train on your image then run the [colab file](https://colab.research.google.com/drive/1oqT2RrK9c5XfWw8_aQ8dHNbDD5W7iwCw?usp=sharing) to get a trained model
3. **For Sign recognition**
- Clone Medapipe
```shell
  git clone https://github.com/rabBit64/mediapipe.git
```
- Change **end_loop_calculator.h** file to our new /end_loop_calculator.h file in the modified_mediapipe folder.
```shell
  cd ~/mediapipe/mediapipe/calculators/core
  rm end_loop_calculator.h
```
- Change **demo_run_graph_main.cc** file to our new demo_run_graph_main.cc file in the modified_mediapipe folder.
```shell
  cd ~/mediapipe/mediapipe/examples/desktop
  rm demo_run_graph_main.cc
```
- Change **landmarks_to_render_data_calculator.cc** file to our new landmarks_to_render_data_calculator.cc file in the modified_mediapipe folder.
```shell
  cd ~/mediapipe/mediapipe/calculators/util
  rm landmarks_to_render_data_calculator.cc
```
- Build the above Mediapipe folder using 🐳 docker given [here](https://google.github.io/mediapipe/getting_started/install.html#installing-using-docker).

4. Make all the mention folders and sub-folders to have the added folders in main repository as shown below.
```shell
BE_Project
├── all-frames-gen
├── checkpoints
├── output
├── protected
    └── test
        └── word
└── stanford-parser-4.0.0
```
5. Setting up a twilio backend
- [Create a Twilio account](https://www.twilio.com/referral/7fB3Je) (if you don't have one yet). It's free!
- [Generate an API Key](https://www.twilio.com/console/project/api-keys) for your account.
- Clone this repository
- Create a .env file by copying the .env.template file. Fill out the values for your Twilio account's SID, API Key SID and API Key Secret.

## Usage
- Execute **_`python main.py`_** to start the server.
- Navigate to `http://localhost:5000` on your web browser and connect as a `specially-abled user` from the system that started the server. Navigate again to `http://localhost:5000` using different machine on the same network and connect as a `normal1 user1. We also suggest you use ngrok to broadcast localhost on a temporary HTTPS URL.

## Publications
Please refer to our [sign generation paper](https://ieeexplore.ieee.org/abstract/document/9315979)

## 👤Contributors
**[Neel Vasani](https://github.com/neelvasani16999), [Pratik Autee](https://github.com/prtkx2), [Samip Kalyani](https://github.com/samipkalyani)**
