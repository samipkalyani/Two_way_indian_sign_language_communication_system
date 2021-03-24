// Copyright 2019 The MediaPipe Authors.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//      http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#include "mediapipe/examples/desktop/autoflip/quality/scene_cropper.h"

#include "mediapipe/examples/desktop/autoflip/quality/focus_point.pb.h"
#include "mediapipe/framework/port/gmock.h"
#include "mediapipe/framework/port/gtest.h"
#include "mediapipe/framework/port/opencv_core_inc.h"
#include "mediapipe/framework/port/status_matchers.h"

namespace mediapipe {
namespace autoflip {

using testing::HasSubstr;

const int kCropWidth = 90;
const int kCropHeight = 160;

const int kSceneWidth = 320;
const int kSceneHeight = 180;

const int kNumSceneFrames = 30;

// Returns default values for SceneKeyFrameCropSummary. Sets scene size and crop
// window size from default values.
SceneKeyFrameCropSummary GetDefaultSceneKeyFrameCropSummary() {
  SceneKeyFrameCropSummary scene_summary;
  scene_summary.set_scene_frame_width(kSceneWidth);
  scene_summary.set_scene_frame_height(kSceneHeight);
  scene_summary.set_crop_window_width(kCropWidth);
  scene_summary.set_crop_window_height(kCropHeight);
  return scene_summary;
}

// Returns default values for scene frames of size kNumSceneFrames. Stes each
// frame to be solid red color at default scene size.
std::vector<cv::Mat> GetDefaultSceneFrames() {
  std::vector<cv::Mat> scene_frames(kNumSceneFrames);
  for (int i = 0; i < kNumSceneFrames; ++i) {
    scene_frames[i] = cv::Mat(kSceneHeight, kSceneWidth, CV_8UC3);
    scene_frames[i] = cv::Scalar(255, 0, 0);
  }
  return scene_frames;
}

// Makes a vector of FocusPointFrames given size. Stes each FocusPointFrame
// to have one FocusPoint at the center of the frame.
std::vector<FocusPointFrame> GetFocusPointFrames(const int num_frames) {
  std::vector<FocusPointFrame> focus_point_frames(num_frames);
  for (int i = 0; i < num_frames; ++i) {
    auto* point = focus_point_frames[i].add_point();
    point->set_norm_point_x(0.5);
    point->set_norm_point_y(0.5);
  }
  return focus_point_frames;
}
// Returns default values for FocusPointFrames of size kNumSceneFrames.
std::vector<FocusPointFrame> GetDefaultFocusPointFrames() {
  return GetFocusPointFrames(kNumSceneFrames);
}

// Checks that CropFrames checks output pointer is not null.
TEST(SceneCropperTest, CropFramesChecksOutputNotNull) {
  SceneCropper scene_cropper;
  const auto status = scene_cropper.CropFrames(
      GetDefaultSceneKeyFrameCropSummary(), GetDefaultSceneFrames(),
      GetDefaultFocusPointFrames(), GetFocusPointFrames(0), nullptr);
  EXPECT_FALSE(status.ok());
  EXPECT_THAT(status.ToString(), HasSubstr("Output cropped frames is null."));
}

// Checks that CropFrames checks that scene frames size is positive.
TEST(SceneCropperTest, CropFramesChecksSceneFramesSize) {
  SceneCropper scene_cropper;
  std::vector<cv::Mat> scene_frames(0);
  std::vector<cv::Mat> cropped_frames;
  const auto status = scene_cropper.CropFrames(
      GetDefaultSceneKeyFrameCropSummary(), scene_frames,
      GetDefaultFocusPointFrames(), GetFocusPointFrames(0), &cropped_frames);
  EXPECT_FALSE(status.ok());
  EXPECT_THAT(status.ToString(), HasSubstr("No scene frames."));
}

// Checks that CropFrames checks that FocusPointFrames has the right size.
TEST(SceneCropperTest, CropFramesChecksFocusPointFramesSize) {
  SceneCropper scene_cropper;
  std::vector<cv::Mat> cropped_frames;
  const auto status = scene_cropper.CropFrames(
      GetDefaultSceneKeyFrameCropSummary(), GetDefaultSceneFrames(),
      GetFocusPointFrames(kNumSceneFrames - 1), GetFocusPointFrames(0),
      &cropped_frames);
  EXPECT_FALSE(status.ok());
  EXPECT_THAT(status.ToString(), HasSubstr("Wrong size of FocusPointFrames"));
}

// Checks that CropFrames checks crop size is positive.
TEST(SceneCropperTest, CropFramesChecksCropSizePositive) {
  auto scene_summary = GetDefaultSceneKeyFrameCropSummary();
  scene_summary.set_crop_window_width(-1);
  SceneCropper scene_cropper;
  std::vector<cv::Mat> cropped_frames;
  const auto status = scene_cropper.CropFrames(
      scene_summary, GetDefaultSceneFrames(), GetDefaultFocusPointFrames(),
      GetFocusPointFrames(0), &cropped_frames);
  EXPECT_FALSE(status.ok());
  EXPECT_THAT(status.ToString(), HasSubstr("Crop width is non-positive."));
}

// Checks that CropFrames checks that crop size does not exceed frame size.
TEST(SceneCropperTest, InitializesRetargeterChecksCropSizeNotExceedFrameSize) {
  auto scene_summary = GetDefaultSceneKeyFrameCropSummary();
  scene_summary.set_crop_window_height(kSceneHeight + 1);
  SceneCropper scene_cropper;
  std::vector<cv::Mat> cropped_frames;
  const auto status = scene_cropper.CropFrames(
      scene_summary, GetDefaultSceneFrames(), GetDefaultFocusPointFrames(),
      GetFocusPointFrames(0), &cropped_frames);
  EXPECT_FALSE(status.ok());
  EXPECT_THAT(status.ToString(),
              HasSubstr("Crop height exceeds frame height."));
}

// Checks that CropFrames works when there are not any prior FocusPointFrames.
TEST(SceneCropperTest, CropFramesWorksWithoutPriorFocusPointFrames) {
  SceneCropper scene_cropper;
  std::vector<cv::Mat> cropped_frames;
  MP_ASSERT_OK(scene_cropper.CropFrames(
      GetDefaultSceneKeyFrameCropSummary(), GetDefaultSceneFrames(),
      GetDefaultFocusPointFrames(), GetFocusPointFrames(0), &cropped_frames));
  ASSERT_EQ(cropped_frames.size(), kNumSceneFrames);
  for (int i = 0; i < kNumSceneFrames; ++i) {
    EXPECT_EQ(cropped_frames[i].rows, kCropHeight);
    EXPECT_EQ(cropped_frames[i].cols, kCropWidth);
  }
}

// Checks that CropFrames works when there are prior FocusPointFrames.
TEST(SceneCropperTest, CropFramesWorksWithPriorFocusPointFrames) {
  SceneCropper scene_cropper;
  std::vector<cv::Mat> cropped_frames;
  MP_EXPECT_OK(scene_cropper.CropFrames(
      GetDefaultSceneKeyFrameCropSummary(), GetDefaultSceneFrames(),
      GetDefaultFocusPointFrames(), GetFocusPointFrames(3), &cropped_frames));
  EXPECT_EQ(cropped_frames.size(), kNumSceneFrames);
  for (int i = 0; i < kNumSceneFrames; ++i) {
    EXPECT_EQ(cropped_frames[i].rows, kCropHeight);
    EXPECT_EQ(cropped_frames[i].cols, kCropWidth);
  }
}

}  // namespace autoflip
}  // namespace mediapipe
