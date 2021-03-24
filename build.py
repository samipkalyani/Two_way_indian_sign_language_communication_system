import os
import sys
import argparse

class Builder:
    def __init__(self,input_data_path,output_data_path):
        self.input_data_path = input_data_path
        self.output_data_path = output_data_path

    def build(self):
        #comp = '/content/bazel-3.4.1/output/bazel build -c opt --define MEDIAPIPE_DISABLE_GPU=1 mediapipe/examples/desktop/multi_hand_tracking:multi_hand_tracking_cpu'
        # print(self.input_data_path)
        # print(self.output_data_path)
        cmd='GLOG_logtostderr=1 bazel-bin/mediapipe/examples/desktop/multi_hand_tracking/multi_hand_tracking_cpu \--calculator_graph_config_file=mediapipe/graphs/hand_tracking/multi_hand_tracking_desktop_live.pbtxt'
        listfile=os.listdir(self.input_data_path)
        if not(os.path.isdir(self.output_data_path+"Relative/")):
            os.mkdir(self.output_data_path+"Relative/")
        if not(os.path.isdir(self.output_data_path+"Absolute/")):
            os.mkdir(self.output_data_path+"Absolute/")
        print(listfile)
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
            
            # /content/bazel-3.4.1/output/bazel build -c opt --define MEDIAPIPE_DISABLE_GPU=1 \mediapipe/examples/desktop/multi_hand_tracking:multi_hand_tracking_cpu
            for mp4list in fullfilename:
                print(mp4list)     
                inputfilen='   --input_video_path='+self.input_data_path+word+mp4list
                outputfilen='   --output_video_path='+self.output_data_path+'_'+word+mp4list
                
                # print(inputfilen,outputfilen)
                cmdret=cmd+inputfilen+outputfilen
                print(cmdret)
                os.system(cmdret)

def main(input_data_path,output_data_path):
    b = Builder(input_data_path,output_data_path)
    return b