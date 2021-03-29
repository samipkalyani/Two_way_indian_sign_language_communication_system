# import os
# import ffmpeg

# class Preprocessor:
#     def __init__(self,input_videos_path):
#         self.input_videos_path = input_videos_path
    
#     def preprocess(self):
#         for filename in os.listdir(self.input_videos_path):
#             folder_name = filename.split('.')[0]
#             if ' ' in filename:
#                 filename = filename.replace(' ','\ ')
#             if ' ' in folder_name:
#                 folder_name = folder_name.replace(' ','\ ')

#             print(filename)
#             print(folder_name)

#             os.chdir('..\openpose')
#             os.system('build\\x64\Release\OpenPoseDemo.exe --video ..\BE_Project\protected\\test\\videos\\'+filename+'  --display 0 --face --hand --write_images ..\BE_Project\protected\\test\openpose_images\\'+folder_name+'  --disable_blending --alpha_pose 1 --part_candidates --model_pose BODY_25 --net_resolution "320x176" --face_net_resolution "320x320"')
#             os.chdir('..\BE_Project')

            

# def main(input_videos_path):
#     p = Preprocessor(input_videos_path)
#     return p
