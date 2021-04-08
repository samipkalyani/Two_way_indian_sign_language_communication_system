from __future__ import absolute_import, division, print_function, unicode_literals
import cv2
from PIL import Image
import matplotlib.pyplot as plt
import tensorflow as tf
import time
from IPython import display
import numpy as np
import os
from os.path import isfile, join

class SignGenerator:
  def __init__(self,islsentence):
    self.islsentence = islsentence    
    self.BUFFER_SIZE = 400
    self.BATCH_SIZE = 1
    self.IMG_WIDTH = 512
    self.IMG_HEIGHT = 512
    self.OUTPUT_CHANNELS = 3
    
  def load(self,image_file):
    image = tf.io.read_file(image_file) 
    image = tf.image.decode_jpeg(image)
    w = tf.shape(image)[1]
    w = w // 2
    print(w)
    real_image = image[:, :w, :]
    input_image = image[:, w:, :]

    input_image = tf.cast(input_image, tf.float32)
    real_image = tf.cast(real_image, tf.float32)

    return input_image, real_image

  def resize(self,input_image, real_image):
    input_image = tf.image.resize(input_image, [self.IMG_HEIGHT, self.IMG_WIDTH],method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
    real_image = tf.image.resize(real_image, [self.IMG_HEIGHT, self.IMG_WIDTH],method=tf.image.ResizeMethod.NEAREST_NEIGHBOR)
    return input_image, real_image

  def normalize(self, input_image, real_image):
    input_image = (input_image / 127.5) - 1
    real_image = (real_image / 127.5) - 1
    return input_image, real_image

  def load_image_test(self,image_file):
    input_image, real_image = self.load(image_file)
    input_image, real_image = self.resize(input_image, real_image)
    input_image, real_image = self.normalize(input_image, real_image)

    return input_image, real_image

  def downsample(self, filters, size, apply_batchnorm=True):
    initializer = tf.random_normal_initializer(0., 0.02)

    result = tf.keras.Sequential()
    result.add(
        tf.keras.layers.Conv2D(filters, size, strides=2, padding='same',
                              kernel_initializer=initializer, use_bias=False))

    if apply_batchnorm:
      result.add(tf.keras.layers.BatchNormalization())

    result.add(tf.keras.layers.LeakyReLU())

    return result

  def upsample(self, filters, size, apply_dropout=False):
    initializer = tf.random_normal_initializer(0., 0.02)

    result = tf.keras.Sequential()
    result.add(
      tf.keras.layers.Conv2DTranspose(filters, size, strides=2,
                                      padding='same',
                                      kernel_initializer=initializer,
                                      use_bias=False))

    result.add(tf.keras.layers.BatchNormalization())

    if apply_dropout:
        result.add(tf.keras.layers.Dropout(0.5))

    result.add(tf.keras.layers.ReLU())

    return result

  def Generator(self):
    inputs = tf.keras.layers.Input(shape=[512,512,3])

    down_stack = [
      self.downsample(64, 4, apply_batchnorm=False),
      self.downsample(128, 4), # (bs, 128, 128, 64)
      self.downsample(256, 4), # (bs, 64, 64, 128)
      self.downsample(512, 4), # (bs, 32, 32, 256)
      self.downsample(1024, 4), # (bs, 16, 16, 512)
      self.downsample(1024, 4), # (bs, 8, 8, 512)
      self.downsample(1024, 4), # (bs, 4, 4, 512)
      self.downsample(1024, 4), # (bs, 2, 2, 512)
      self.downsample(1024, 4), # (bs, 1, 1, 512)
    ]

    up_stack = [
      self.upsample(1024, 4, apply_dropout=True), # (bs, 2, 2, 1024)
      self.upsample(1024, 4, apply_dropout=True), # (bs, 4, 4, 1024)
      self.upsample(1024, 4, apply_dropout=True), # (bs, 8, 8, 1024)
      self.upsample(1024, 4), # (bs, 16, 16, 1024)
      self.upsample(512, 4), # (bs, 32, 32, 512)
      self.upsample(256, 4), # (bs, 64, 64, 256)
      self.upsample(128, 4), # (bs, 128, 128, 128)
      self.upsample(64,4),
    ]

    initializer = tf.random_normal_initializer(0., 0.02)
    last = tf.keras.layers.Conv2DTranspose(self.OUTPUT_CHANNELS, 4,
                                          strides=2,
                                          padding='same',
                                          kernel_initializer=initializer,
                                          activation='tanh') # (bs, 256, 256, 3)

    x = inputs

    # Downsampling through the model
    skips = []
    for down in down_stack:
      x = down(x)
      skips.append(x)

    skips = reversed(skips[:-1])

    # Upsampling and establishing the skip connections
    for up, skip in zip(up_stack, skips):
      x = up(x)
      print('---------',x)
      print('`````````',skip)
      x = tf.keras.layers.Concatenate()([x, skip])

    x = last(x)

    return tf.keras.Model(inputs=inputs, outputs=x)

  def Discriminator(self):
    initializer = tf.random_normal_initializer(0., 0.02)

    inp = tf.keras.layers.Input(shape=[512, 512, 3], name='input_image')
    tar = tf.keras.layers.Input(shape=[512, 512, 3], name='target_image')

    x = tf.keras.layers.concatenate([inp, tar]) # (bs, 256, 256, channels*2)

    down1 = self.downsample(128, 4, False)(x) # (bs, 128, 128, 64)
    down2 = self.downsample(256, 4)(down1) # (bs, 64, 64, 128)
    down3 = self.downsample(512, 4)(down2) # (bs, 32, 32, 256)

    zero_pad1 = tf.keras.layers.ZeroPadding2D()(down3) # (bs, 34, 34, 256)
    conv = tf.keras.layers.Conv2D(1024, 4, strides=1,
                                  kernel_initializer=initializer,
                                  use_bias=False)(zero_pad1) # (bs, 31, 31, 512)

    batchnorm1 = tf.keras.layers.BatchNormalization()(conv)

    leaky_relu = tf.keras.layers.LeakyReLU()(batchnorm1)

    zero_pad2 = tf.keras.layers.ZeroPadding2D()(leaky_relu) # (bs, 33, 33, 512)

    last = tf.keras.layers.Conv2D(1, 4, strides=1,
                                  kernel_initializer=initializer)(zero_pad2) # (bs, 30, 30, 1)

    return tf.keras.Model(inputs=[inp, tar], outputs=last)

  def generate_images(self, model, test_input, tar,f):
    prediction = model(test_input, training=True)
    display_list = [test_input[0], prediction[0]]
    title = ['Input Image', 'Predicted Image']
    plt.axis('off')
    plt.imshow(display_list[1] * 0.5 + 0.5)
    plt.savefig('frames-gen/'+str(f)+'.png')
    plt.cla()

  def generate(self):
    test_dataset = tf.data.Dataset.list_files('./test-folder/*.jpg', shuffle=False, seed = 1)
    test_dataset = test_dataset.map(self.load_image_test)
    test_dataset = test_dataset.batch(self.BATCH_SIZE)
    generator = self.Generator()
    tf.keras.utils.plot_model(generator, show_shapes=True, dpi=64)
    generator.summary()
    discriminator = self.Discriminator()
    generator_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
    discriminator_optimizer = tf.keras.optimizers.Adam(2e-4, beta_1=0.5)
    checkpoint_dir = './gan-model'
    checkpoint_prefix = os.path.join(checkpoint_dir, "ckpt-samip200")
    checkpoint = tf.train.Checkpoint(generator_optimizer=generator_optimizer,
                                 discriminator_optimizer=discriminator_optimizer,
                                 generator=generator,
                                 discriminator=discriminator)

    checkpoint.restore(tf.train.latest_checkpoint('./gan-model/'))
    f=1
    for inp, tar in test_dataset.take(len(os.listdir('./test-folder/'))):
      self.generate_images(generator, inp, tar,f)
      f+=1
    pathIn= './frames-gen/'
    pathOut = './static/video.mp4'
    fps = 24
    frames_array = []
    files=[]
    fs = [f for f in os.listdir(pathIn)]
    for f in fs:
      new_f = f.split('.')[0]
      files.append(new_f)
    files.sort(key=int)
    for file in files:
      file += '.png'
      frames_array.append(file)
    print(frames_array)
    m=[]
    for i in range(len(frames_array)):
        filename=pathIn + frames_array[i]
        img = cv2.imread(filename)
        height, width, layers = img.shape
        size = (width,height)
        #inserting the frames into an image array
        m.append(img)
    #print(frame_array)
    out = cv2.VideoWriter(pathOut,cv2.VideoWriter_fourcc(*'DIVX'), fps, size)
    for i in range(len(m)):
        # writing to a image array
        out.write(m[i])
    out.release()
    return True

def main(islsentence):
  g = SignGenerator(islsentence)
  return g