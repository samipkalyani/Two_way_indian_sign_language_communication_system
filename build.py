import os
import shutil
import sys
import argparse
import subprocess
import time

class Builder:
    def __init__(self,input_data_path,output_data_path):
        self.input_data_path = input_data_path
        self.output_data_path = output_data_path

    def build(self):
        outputFile = open("output.log","r+")
        outputFile.truncate(0)
        outputFile.close()
        
        listfile=os.listdir(self.input_data_path)
        if not(os.path.isdir(self.output_data_path+"Relative/")):
            os.mkdir(self.output_data_path+"Relative/")
        if not(os.path.isdir(self.output_data_path+"Absolute/")):
            os.mkdir(self.output_data_path+"Absolute/")

        for file in listfile:
            print(file)
            if not(os.path.isdir(self.input_data_path+file)): #ignore .DS_Store
                continue
            word = file+"/"
            fullfilename=os.listdir(self.input_data_path+word)
            if not(os.path.isdir(self.output_data_path+"_"+word)):
                os.mkdir(self.output_data_path+"_"+word)
            if not(os.path.isdir(self.output_data_path+"Relative/"+word)):
                os.mkdir(self.output_data_path+"Relative/"+word)
            if not(os.path.isdir(self.output_data_path+"Absolute/"+word)):
                os.mkdir(self.output_data_path+"Absolute/"+word)

            with open("output.log", "a") as output:
                subprocess.call("docker run -itd -e DISPLAY=$DISPLAY --name modified_mediapipe modified_mediapipe", shell=True, stdout=output, stderr=output)
                subprocess.call("docker cp ./protected/test modified_mediapipe:/mediapipe", shell=True, stdout=output, stderr=output)
                subprocess.call("docker cp ./output/ modified_mediapipe:/mediapipe", shell=True, stdout=output, stderr=output)
                
            shutil.rmtree('./output')

            with open("output.log", "a") as output:
                subprocess.call("docker cp script.py  modified_mediapipe:/mediapipe", shell=True, stdout=output, stderr=output)
                subprocess.call("docker exec -it modified_mediapipe python script.py", shell=True, stdout=output, stderr=output)

            with open("output.log", "a") as output:
                subprocess.call("docker cp modified_mediapipe:/mediapipe/output .", shell=True, stdout=output, stderr=output)
            
            with open("output.log", "a") as output:
                subprocess.call("docker container stop modified_mediapipe", shell=True, stdout=output, stderr=output)
                subprocess.call("docker container rm modified_mediapipe", shell=True, stdout=output, stderr=output)
            
            os.remove('./protected/test/word/test.mp4')
            return

def main(input_data_path,output_data_path):
    b = Builder(input_data_path,output_data_path)
    return b