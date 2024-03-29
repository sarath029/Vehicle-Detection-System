#!/usr/bin/python
# -*- coding: utf-8 -*-
# ----------------------------------------------
# --- Author         : Ahmet Ozlu
# --- Mail           : ahmetozlu93@gmail.com
# --- Date           : 27th January 2018
# ----------------------------------------------

# Imports
import numpy as np
import os
import six.moves.urllib as urllib
import sys
import tarfile
import tensorflow as tf
import zipfile
import cv2
import numpy as np
import csv
import time
import argparse

from collections import defaultdict
from io import StringIO
from matplotlib import pyplot as plt
from PIL import Image

# Object detection imports
from utils import label_map_util
from utils import visualization_utils as vis_util

# initialize .csv
with open('traffic_measurement.csv', 'w') as f:
    writer = csv.writer(f)
    csv_line = \
        'Vehicle Type/Size, Vehicle Color, Vehicle Movement Direction, Vehicle Speed (km/h)'
    writer.writerows([csv_line.split(',')])

if tf.__version__ < '1.14.0':
    raise ImportError('Please upgrade your tensorflow installation to v1.4.* or later!'
                      )

# input video.
#video = "video_1_61.mp4"
parser = argparse.ArgumentParser(description='Vehicle Detection and Classified Counting')
parser.add_argument('--video', help='Path to video file.')
parser.add_argument('--model',required=False ,help = 'Path to the model you want to use. Default is Faster Rcnn Resnet50.')
args = parser.parse_args()

if(args.video):
    if not os.path.isfile(args.video):
        print("Input video file ", args.video, " doesn't exist")
        sys.exit(1)
    cap = cv2.VideoCapture(args.video)
else:
    print("Error . Please Provide a video file as an argument.")
    sys.exit(1)
outputFile  = args.video[:-4] + "new_upd.avi"

#Use these if you want to know the height and width of the video and set the ROI line Accordingly.
height = int( cap.get(cv2.CAP_PROP_FRAME_HEIGHT ))
roi =  int(((height)*2)/3) - 110
if(height == 1080):
    roi = 620

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
vis_util.helper(roi)

# Variables
total_passed_vehicle = 0  # using it to count vehicles

# By default I use an "SSD with Mobilenet" model here. See the detection model zoo (https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md) for a list of other models that can be run out-of-the-box with varying speeds and accuracies.
# What model to download.
if(args.model):
    if not os.path.exists(args.model):
        print("Input model ", args.model, " doesn't exist")
        sys.exit(1)
    MODEL_NAME = args.model
else:
    MODEL_NAME = 'faster_rcnn_resnet50_coco_2018_01_28'


MODEL_FILE = MODEL_NAME + '.tar.gz'
DOWNLOAD_BASE = \
    'http://download.tensorflow.org/models/object_detection/'

# Path to frozen detection graph. This is the actual model that is used for the object detection.
PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

# List of the strings that is used to add correct label for each box.
PATH_TO_LABELS = os.path.join('data', 'mscoco_label_map.pbtxt')

NUM_CLASSES = 90

# Download Model
# uncomment if you have not download the model yet
# Load a (frozen) Tensorflow model into memory.
detection_graph = tf.Graph()
with detection_graph.as_default():
    od_graph_def = tf.GraphDef()
    with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
        serialized_graph = fid.read()
        od_graph_def.ParseFromString(serialized_graph)
        tf.import_graph_def(od_graph_def, name='')

# Loading label map
# Label maps map indices to category names, so that when our convolution network predicts 5, we know that this corresponds to airplane. Here I use internal utility functions, but anything that returns a dictionary mapping integers to appropriate string labels would be fine
label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
categories = label_map_util.convert_label_map_to_categories(label_map,
        max_num_classes=NUM_CLASSES, use_display_name=True)
category_index = label_map_util.create_category_index(categories)


# Helper code
def load_image_into_numpy_array(image):
    (im_width, im_height) = image.size
    return np.array(image.getdata()).reshape((im_height, im_width,
            3)).astype(np.uint8)


# Detection
def object_detection_function():
 #   time1 = cv2.getTickCount()
    total_passed_vehicle = 0
    total_cars = [0]*2
    total_trucks = [0]*2
    total_bus = [0]*2
    total_person = [0]*2
    total_motorcycle = [0]*2
    speed = 'waiting...'
    direction = 'waiting...'
    size = 'waiting...'
    color = 'waiting...'
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:

            # Definite input and output Tensors for detection_graph
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

            # Each box represents a part of the image where a particular object was detected.
            detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

            # Each score represent how level of confidence for each of the objects.
            # Score is shown on the result image, together with the class label.
            detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
            detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name('num_detections:0')
  #          print(detection_classes)
            # for all the frames that are extracted from input video
            vid_writer = cv2.VideoWriter(outputFile, cv2.VideoWriter_fourcc('M','J','P','G'), 30, (round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))
            while cap.isOpened():
                (ret, frame) = cap.read()

                if not ret:
                    print ('end of the video file...')
                    break

                input_frame = frame

                # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
                image_np_expanded = np.expand_dims(input_frame, axis=0)

                # Actual detection.
                (boxes, scores, classes, num) = \
                    sess.run([detection_boxes, detection_scores,
                             detection_classes, num_detections],
                             feed_dict={image_tensor: image_np_expanded})
                #print("CLASSESE",classes)
                # Visualization of the results of a detection.
                (counter, csv_line) = \
                    vis_util.visualize_boxes_and_labels_on_image_array(
                    cap.get(1),
                    input_frame,
                    np.squeeze(boxes),
                    np.squeeze(classes).astype(np.int32),
                    np.squeeze(scores),
                    category_index,
                    use_normalized_coordinates=True,
                    line_thickness=4,
                    )

                total_passed_vehicle = total_passed_vehicle + sum(counter)
                if direction == 'up':
                    total_cars[0] = total_cars[0] + counter[0]
                    total_trucks[0] = total_trucks[0] + counter[1]
                    total_bus[0] = total_bus[0] + counter[2]
                    total_person[0] = total_person[0] + counter[3]
                    total_motorcycle[0] = total_motorcycle + counter[4]
                elif direction == "down":
                    total_cars[1] = total_cars[1] + counter[0]
                    total_trucks[1] = total_trucks[1] + counter[1]
                    total_bus[1] = total_bus[1] + counter[2]
                    total_person[1] = total_person[1] + counter[3]
                    total_motorcycle[1] = total_motorcycle[1] + counter[4]
                #print(counter)
                # insert information text to video frame
                font = cv2.FONT_HERSHEY_SIMPLEX
                cv2.putText(
                    input_frame,
                    'Vehicles:' + str(total_passed_vehicle) + ' Car up:' + str(total_cars[0]) + ' C down:'+str(total_cars[1])+' Truck up:' + str(total_trucks[0]) +' T down:' + str(total_trucks[1]),

                    (10, 35),
                    font,
                    0.8,
                    (0, 0xFF, 0),
                    2,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    )
                cv2.putText(
                    input_frame,
                    'Bus up:' + str(total_bus[0]) + ' B d:' + str(total_bus[1]) + ' P up:' + str(total_person[0])+ ' P down:' + str(total_person[1])+ ' Bike up:' + str(total_motorcycle[0])+ ' B down:' + str(total_motorcycle[1]),

                    (10, 55),
                    font,
                    0.8,
                    (0, 0xFF, 0),
                    2,
                    cv2.FONT_HERSHEY_SIMPLEX,
                    )

                # when the vehicle passed over line and counted, make the color of ROI line green
                if sum(counter) == 1:
                    cv2.line(input_frame, (0, roi), (width, roi), (0, 0xFF, 0), 5)
                else:
                    cv2.line(input_frame, (0, roi), (width, roi), (0, 0, 0xFF), 5)

                # insert information text to video frame
                
                cv2.putText(
                    input_frame,
                    'ROI Line',
                    (width-100, roi-40),
                    font,
                    0.6,
                    (0, 0, 0xFF),
                    2,
                    cv2.LINE_AA,
                    )
                
                vid_writer.write(input_frame.astype(np.uint8))
                #cv2.imshow('vehicle detection', input_frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

                if csv_line != 'not_available':
                    with open('traffic_measurement.csv', 'a') as f:
                        writer = csv.writer(f)
                        (size, color, direction, speed) = \
                            csv_line.split(',')
                        writer.writerows([csv_line.split(',')])
            cap.release()
            cv2.destroyAllWindows()


object_detection_function()
#time2 = cv2.getTickCount()
#time = (time2 - time1) / cv2.getTickFrequency()
#print("Total Time taken to process the video :",time)
