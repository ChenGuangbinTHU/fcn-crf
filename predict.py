import argparse
import LoadBatches
from keras.models import load_model
import glob
import cv2
import numpy as np
import random
import time
import os
from models import FCN8, resnet_aspp, vgg16_aspp
import config
import result_visulize
import miou

if not config.use_gpu:
	os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"   # see issue #152
	os.environ["CUDA_VISIBLE_DEVICES"] = ""

n_classes = config.n_classes
model_name = config.model_name
images_path = config.test_images
input_width =  config.input_width
input_height = config.input_height

modelFNs = {'fcn8':FCN8.FCN8, 'vgg16_aspp':vgg16_aspp.vgg16_aspp, 'resnet_aspp':resnet_aspp.resnet_aspp}

if model_name not in modelFNs:
	print('please choose model name from {fcn8, vgg16_aspp, resnet_aspp}')
	exit(0)

modelFN = modelFNs[model_name]
m = modelFN( n_classes , input_height=input_height, input_width=input_width   )
m.load_weights(  config.save_weights_path + config.test_model_name  )
# m.compile(loss='categorical_crossentropy',
#       optimizer= 'adadelta' ,
#       metrics=['accuracy'])
m.summary()

output_height = m.outputHeight
output_width = m.outputWidth

images = glob.glob( images_path + "*.jpg"  ) + glob.glob( images_path + "*.png"  ) +  glob.glob( images_path + "*.jpeg"  )
images.sort()
# print(images)
# exit(0)
# colors = [  ( random.randint(0,255),random.randint(0,255),random.randint(0,255)   ) for _ in range(n_classes)  ]
colors=[(0,0,0),(255,255,255)]
for imgName in images:
	outName = imgName.replace( images_path ,  config.output_path )
	X = LoadBatches.getImageArr(imgName , config.input_width  , config.input_height  )
	start = time.time()
	pr = m.predict( np.array([X]) )[0]
	end = time.time()
	print(end-start,'s')
	pr = pr.reshape(( output_height ,  output_width , n_classes ) ).argmax( axis=2 )
	seg_img = np.zeros( ( output_height , output_width , 3  ) )
	for c in range(n_classes):
		seg_img[:,:,0] += ( (pr[:,: ] == c )*( colors[c][0] )).astype('uint8')
		seg_img[:,:,1] += ((pr[:,: ] == c )*( colors[c][1] )).astype('uint8')
		seg_img[:,:,2] += ((pr[:,: ] == c )*( colors[c][2] )).astype('uint8')
	# print(seg_img)
	# print(output_height, output_width)
	# print(seg_img)
	seg_img = cv2.resize(seg_img  , (input_width , input_height ))
	# print(seg_img)
	# exit(0)
	cv2.imwrite(  outName , seg_img )
	

if config.visulize:
	print('result visulization')
	result_visulize.main(config.test_images, config.output_path, config.visulize_image_path)

if config.show_iou:
	print('calculate iou')
	miou.main(config.test_annotations, config.output_path)