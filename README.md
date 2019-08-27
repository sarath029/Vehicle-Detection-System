# vehicle_counting
You need to add a model from the tensorflow model zoo - https://github.com/tensorflow/models/blob/master/research/object_detection/g3doc/detection_model_zoo.md into the directory.

Change the model name in line 70 of vehicle_detection_main.py

You can run using the command -  python vehicle_detection_main.py --video "video_1_61.mp4"

Change the roi line based on the height and width of your input.

This gives a classified count of the different vehicles - Cars, Trucks, Buses and Person.
