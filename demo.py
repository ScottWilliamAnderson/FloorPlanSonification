# PLEASE NOTE:
# This demo.py file is provided by the authors of the paper:
# @article{zeng,
#   doi = {10.48550/ARXIV.1908.11025},
#   url = {https://arxiv.org/abs/1908.11025},
#   author = {Zeng,  Zhiliang and Li,  Xianzhi and Yu,  Ying Kin and Fu,  Chi-Wing},
#   keywords = {Computer Vision and Pattern Recognition (cs.CV),  FOS: Computer and information sciences,  FOS: Computer and information sciences, deep, floorplan},
#   title = {Deep Floor Plan Recognition Using a Multi-Task Network with Room-Boundary-Guided Attention},
#   publisher = {arXiv},
#   year = {2019},
# }

# https://github.com/zlzeng/DeepFloorplan

# I have made only minor modifications to this file to make it compatible with the rest of the project.


import os
import argparse
import numpy as np
import tensorflow as tf

from scipy.misc import imread, imsave, imresize
from matplotlib import pyplot as plt

os.environ['CUDA_VISIBLE_DEVICES'] = '0'

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

# input image path
parser = argparse.ArgumentParser()

parser.add_argument('--im_path', type=str, default='./demo/45765448.jpg',
                    help='input image paths.')

# color map
floorplan_map = {
	0: [255,255,255], # background
	1: [192,192,224], # closet
	2: [192,255,255], # batchroom/washroom
	3: [224,255,192], # livingroom/kitchen/dining room
	4: [255,224,128], # bedroom
	5: [255,160, 96], # hall
	6: [255,224,224], # balcony
	7: [255,255,255], # not used
	8: [255,255,255], # not used
	9: [255, 60,128], # door & window
	10:[  0,  0,  0]  # wall
}

def ind2rgb(ind_im, color_map=floorplan_map):
	rgb_im = np.zeros((ind_im.shape[0], ind_im.shape[1], 3))

	for i, rgb in color_map.items():
		rgb_im[(ind_im==i)] = rgb

	return rgb_im

def main(args):
	# load input
	im = imread(args, mode='RGB')
	im = im.astype(np.float32)
	im = imresize(im, (512,512,3)) / 255.

	# create tensorflow session
	with tf.Session() as sess:
		
		# initialize
		sess.run(tf.group(tf.global_variables_initializer(),
					tf.local_variables_initializer()))

		# restore pretrained model
		# saver = tf.train.import_meta_graph('/DeepFloorplan/pretrained/pretrained_r3d.meta')
		saver = tf.train.import_meta_graph(os.path.join(os.getcwd(), "pretrained\pretrained_r3d.meta"))
		saver.restore(sess, os.path.join(os.getcwd(), "pretrained\pretrained_r3d"))

		# get default graph
		graph = tf.get_default_graph()

		# restore inputs & outpus tensor
		x = graph.get_tensor_by_name('inputs:0')
		room_type_logit = graph.get_tensor_by_name('Cast:0')
		room_boundary_logit = graph.get_tensor_by_name('Cast_1:0')
  
  		# infer results
		[room_type, room_boundary] = sess.run([room_type_logit, room_boundary_logit],\
										feed_dict={x:im.reshape(1,512,512,3)})
		room_type, room_boundary = np.squeeze(room_type), np.squeeze(room_boundary)

		# merge results
		floorplan = room_type.copy()
		floorplan[room_boundary==1] = 9
		floorplan[room_boundary==2] = 10
		floorplan_rgb = ind2rgb(floorplan)

		plt.subplot(121)
		plt.imshow(im)
		plt.subplot(122)
		plt.imsave(os.path.join(os.getcwd(), 'map', 'result.png'),floorplan_rgb/255)
		return

if __name__ == '__main__':
	FLAGS, unparsed = parser.parse_known_args()
	main(FLAGS)
