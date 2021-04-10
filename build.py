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
        
        lsdir = os.listdir(self.input_data_path)
        print(lsdir)
        for i in range(len(lsdir)):
            listfile=os.listdir(self.input_data_path+lsdir[i])
            print("listfile")
            print(listfile)

            print(self.output_data_path+"output"+str(i+1))
            os.mkdir(self.output_data_path+"output"+str(i+1))

            print(self.output_data_path+"output"+str(i+1)+"/Relative/")
            if not(os.path.isdir(self.output_data_path+"output"+str(i+1)+"/Relative/")):
                os.mkdir(self.output_data_path+"output"+str(i+1)+"/Relative/")
            print(self.output_data_path+"output"+str(i+1)+"/Absolute/")
            if not(os.path.isdir(self.output_data_path+"output"+str(i+1)+"/Absolute/")):
                os.mkdir(self.output_data_path+"output"+str(i+1)+"/Absolute/")

            print("file in listfile")
            for file in listfile:
                print(file)
                print(self.input_data_path+"/"+str(lsdir[i])+"/"+file)
                if not(os.path.isdir(self.input_data_path+"/"+str(lsdir[i])+"/"+file)): #ignore .DS_Store
                    continue
                word = file+"/"
                fullfilename=os.listdir(self.input_data_path+"/"+str(lsdir[i])+"/"+word)
                print(fullfilename)
                print(self.output_data_path+"output"+str(i+1)+"/_"+word)
                if not(os.path.isdir(self.output_data_path+"output"+str(i+1)+"/_"+word)):
                    os.mkdir(self.output_data_path+"output"+str(i+1)+"/_"+word)
                print(self.output_data_path+"output"+str(i+1)+"/Relative/"+word)
                if not(os.path.isdir(self.output_data_path+"output"+str(i+1)+"/Relative/"+word)):
                    os.mkdir(self.output_data_path+"output"+str(i+1)+"/Relative/"+word)
                print(self.output_data_path+"output"+str(i+1)+"/Absolute/"+word)
                if not(os.path.isdir(self.output_data_path+"output"+str(i+1)+"/Absolute/"+word)):
                    os.mkdir(self.output_data_path+"output"+str(i+1)+"/Absolute/"+word)

            with open("output.log", "a") as output:
                subprocess.call("docker run -itd -e DISPLAY=$DISPLAY --name modified_mediapipe"+str(i+1)+" modified_mediapipe", shell=True, stdout=output, stderr=output)
                subprocess.call("docker cp ./protected/test"+str(i+1)+" modified_mediapipe"+str(i+1)+":/mediapipe", shell=True, stdout=output, stderr=output)
                subprocess.call("docker cp ./output/output"+str(i+1)+"/ modified_mediapipe"+str(i+1)+":/mediapipe", shell=True, stdout=output, stderr=output)
                
            # shutil.rmtree('./output')

            with open("output.log", "a") as output:
                subprocess.call("docker cp script.py  modified_mediapipe"+str(i+1)+":/mediapipe", shell=True, stdout=output, stderr=output)
                # subprocess.call("docker exec -it modified_mediapipe python script.py", shell=True, stdout=output, stderr=output)

        for i in range(len(lsdir)):
            with open("output.log", "a") as output:
                subprocess.call("docker exec -itd modified_mediapipe"+str(i+1)+" python script.py", shell=True, stdout=output, stderr=output)

        time.sleep(240)

        for i in range(len(lsdir)):
            with open("output.log", "a") as output:
                subprocess.call("docker cp modified_mediapipe"+str(i+1)+":/mediapipe/output"+str(i+1)+" .", shell=True, stdout=output, stderr=output)
            
            # with open("output.log", "a") as output:
            #     subprocess.call("docker container stop modified_mediapipe", shell=True, stdout=output, stderr=output)
            #     subprocess.call("docker container rm modified_mediapipe", shell=True, stdout=output, stderr=output)
            
            # os.remove('./protected/test/word/test.mp4')
        return

def main(input_data_path,output_data_path):
    b = Builder(input_data_path,output_data_path)
    return b