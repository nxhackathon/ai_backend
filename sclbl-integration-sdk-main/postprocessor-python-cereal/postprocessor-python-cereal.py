import os
import sys
import socket
import signal
import re
import struct
import requests
import datetime
import json
import numpy as np
import cv2
import communication_utils

# This post processor is used to handle feeds from the Cereal Section Camera


POST_PROCESSOR_ID = 0 # This is the ID of the postprocessor used to identify the cameras in the Analysis Server
script_location = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_location, "../sclbl-utilities/python-utilities"))
Postprocessor_Name = "Python-Postprocessor-cereal"
Postprocessor_Socket_Path = "/tmp/python-postprocessor-cereal.sock"

# Mapping of class indices to class names
categories = { 
    0: "person", 1: "bicycle", 2: "car", 3: "motorbike", 4: "aeroplane", 5: "bus", 6: "train", 7: "truck", 8: "boat", 9: "traffic light", 
    10: "fire hydrant", 11: "stop sign", 12: "parking meter", 13: "bench", 14: "bird", 15: "cat", 16: "dog", 17: "horse", 18: "sheep", 19: "cow", 
    20: "elephant", 21: "bear", 22: "zebra", 23: "giraffe", 24: "backpack", 25: "umbrella", 26: "handbag", 27: "tie", 28: "suitcase", 29: "frisbee", 
    30: "skis", 31: "snowboard", 32: "sports ball", 33: "kite", 34: "baseball bat", 35: "baseball glove", 36: "skateboard", 37: "surfboard", 38: "tennis racket", 39: "bottle", 
    40: "wine glass", 41: "cup", 42: "fork", 43: "knife", 44: "spoon", 45: "bowl", 46: "banana", 47: "apple", 48: "sandwich", 49: "orange",
     50: "broccoli", 51: "carrot", 52: "hot dog", 53: "pizza", 54: "donut", 55: "cake", 56: "chair", 57: "sofa", 58: "potted plant", 59: "bed", 
     60: "dining table", 61: "toilet", 62: "tv monitor", 63: "laptop", 64: "mouse", 65: "remote", 66: "keyboard", 67: "cell phone", 68: "microwave", 69: "oven", 
     70: "toaster", 71: "sink", 72: "refrigerator", 73: "book", 74: "clock", 75: "vase", 76: "scissors", 77: "teddy bear", 78: "hair drier", 79: "toothbrush", 
     100: "cereal_boxes", 101: "oats_tins", 102: "peppermints", 103: "biscuits", 104: "sugarfree_cookies", 105: "cereal_tins", 106: "toilet_paper" 
     }

# Product Catalog Provided by Admin
PROD_TYPE = "Cereals Section"
prod_catalog ={
    PROD_TYPE:
    {"100:cereal_boxes;101:oats_tins;102:peppermints;103:biscuits;104:sugarfree_cookies;105:cereal_tins;106:toilet_paper": 
     [10.0, 177.0, 452.0, 247.0, 1.0, 100, 60.0, 253.0, 444.0, 291.0, 1.0, 101, 63.0, 296.0, 437.0, 330.0, 1.0, 102, 62.5, 334.0, 433.5, 374.0, 1.0, 103, 71.0, 376.0, 431.0, 416.0, 1.0, 104, 80.5, 420.5, 421.5, 469.5, 1.0, 105, 6.5, 96.5, 457.5, 161.5, 1.0, 106]
     },
}

def convert_prod_catalog_to_dict(data):
    class_mapping = list(data.keys())[0]
    data = data[class_mapping]
    class_mapping = class_mapping.split(';')
    class_mapping = {int(x.split(':')[0]):x.split(':')[1] for x in class_mapping}
    result = {}

    for i in range(0, len(data), 6):
        x1, y1, x2, y2, conf, class_idx = data[i:i+6]
        class_name = class_mapping[int(class_idx)]
        
        if class_name not in result:
            result[class_name] = []
        
        result[class_name].append([x1, y1, x2, y2, conf])

    return result


# Convert tuple to bytes
def tuple_to_bytes(t):
    print("python3 || ******** Tuple to bytes: ", t)
    return struct.pack('f' * len(t), *t)

# Convert bytes to tuple
def bytes_to_tuple(b):
    return struct.unpack('f' * (len(b) // 4), b)

# Send a post request to the Analysis Server
def send_post_request(bboxes,endpoint="detection"):
    # This function assumes that the API is up and running
    # jsonify bboxes and send in post resuest body
    bboxes = json.dumps(bboxes)
    endpoint = f"http://192.168.0.114:8888/{endpoint}?postprocessorid={POST_PROCESSOR_ID}" # ATTENTION: Change the IP address to the AWS EC2 instance IP address for Analysis Server
    try:
        response = requests.post(endpoint, json=bboxes)
        response.raise_for_status()  # Raises a HTTPError if the response was unsuccessful
    except requests.exceptions.RequestException as err:
        print(f"python2 | Postprocessor -  An error occurred: {err}")


# Wrapper class to handle post requests
# Keeps track of the last timestamp when a post request was sent
# Sends a post request only if the time gap is greater than the specified gap
# Gap = 2 seconds by default
class PostRequestHandler:
    def __init__(self,gap=2) -> None:
        self.last_timestamp = None
        self.gap = gap
    
    def handle_post_request(self, bboxes, endpoint):
        # Send in every gap seconds
        cur_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.last_timestamp is None:
            self.last_timestamp = cur_timestamp
            send_post_request(bboxes,endpoint)
        if (datetime.datetime.strptime(cur_timestamp, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(self.last_timestamp, "%Y-%m-%d %H:%M:%S")).seconds >= self.gap:
            send_post_request(bboxes,endpoint)
            self.last_timestamp = cur_timestamp


def convert_to_dict(input_string):
    _, items = input_string.split(';', 1)
    key_value_pairs = items.split(';')
    result_dict = {}
    for pair in key_value_pairs:
        key, value = pair.split(':')
        result_dict[int(key)] = value
    return result_dict

def decode_binary_to_array(binary_data, shape):
    # Convert the binary string to a byte array
    flattened = np.array(list(struct.unpack('f' * (len(binary_data) // 4), binary_data)))
    # Reshape the byte data to the desired shape
    print("python3 || Flattened shape: ", flattened.shape)
    array_data = flattened.reshape(shape[0])
    return array_data


# Converts the output of Yolov8 model to bounding boxes
# Uses Confidence threshold and NMS threshold to filter out the bounding boxes
# Returns a list of bounding boxes along with their confidence scores and class IDs
def get_bounding_boxes(output, confidence_threshold=0.5, nms_threshold=0.4, num_classes=1):
    # Assume the output shape is (1, 84, 8400)    
    # Reshape the output if necessary
    print("python3 || Output shape: ", output.shape)
    print("python3 || 4+num_classes: ", (1, 4+num_classes, 8400))
    output = output.reshape((1, 4+num_classes, 8400))
    
    # Extract bounding boxes, confidence scores, and class scores
    bounding_boxes = []
    confidences = []
    class_ids = []

    for detection in output[0].transpose(1, 0):
        # Extract the scores for each class
        scores = detection[4:]
        class_id = np.argmax(scores)
        confidence = scores[class_id]

        if confidence > confidence_threshold:
            center_x, center_y, width, height = detection[0:4]
            x = int(center_x - width / 2)
            y = int(center_y - height / 2)
            bounding_boxes.append([x, y, int(width), int(height)])
            confidences.append(float(confidence))
            class_ids.append(class_id)
    
    # Apply Non-Maximum Suppression
    indices = cv2.dnn.NMSBoxes(bounding_boxes, confidences, confidence_threshold, nms_threshold)
    
    # Collect the final bounding boxes, confidences, and class IDs
    final_boxes = []

    if len(indices) > 0:
        for i in indices.flatten():
            bounding_boxes[i][2] = bounding_boxes[i][0]+bounding_boxes[i][2]
            bounding_boxes[i][3] = bounding_boxes[i][1]+bounding_boxes[i][3]
            final_boxes.append(bounding_boxes[i]+[confidences[i]]+[class_ids[i]]) 
            
    final_boxes = np.array(final_boxes).astype(float).reshape(-1).tolist()
    # final_boxes = [datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")]+(np.array(final_boxes).astype(float).tolist())+['interaction']
    return tuple(final_boxes)


# Converts the output of Yolov8-Pose model to bounding boxes
# Uses Confidence threshold and NMS threshold to filter out the bounding boxes
# Recives the shape of the output tensor: (1, 56, 8400)
# Returns a list of bounding boxes along with their confidence scores and class IDs for person detection
# Returns a list of bounding boxes along with their confidence scores and class IDs for body part detection
def get_bbox_from_pose_output(output,person_conf_thresh=0.5,person_nms_thresh=0.5, body_part_conf_thresh=0.0):
    """
    output : (1,56,8400)
    56 = xywh + conf + 17*3
    """
    # For person detection
    keypoints_to_bodyparts = [
      "Nose",
      "Left Eye",
      "Right Eye",
      "Left Ear",
      "Right Ear",
      "Left Shoulder",
      "Right Shoulder",
      "Left Elbow",
      "Right Elbow",
      "Left Wrist",
      "Right Wrist",
      "Left Hip",
      "Right Hip",
      "Left Knee",
      "Right Knee",
      "Left Ankle",
      "Right Ankle"
    ]
    
    class_label_map = ';'.join([f"{81+i}:{keypoints_to_bodyparts[i]}" for i in range(17)])

    
    output = output.reshape(56, 8400)
    output = output.transpose()
    output = output.reshape(8400, 56)
    output = output[output[:,4] > person_conf_thresh]
    indices = cv2.dnn.NMSBoxes(output[:,0:4], output[:,4], person_conf_thresh, person_nms_thresh)

    if len(indices) == 0:
        return [],[],[],{class_label_map:[]}
    

    person_output_56 = output[indices.flatten()]
    person_output = []

    # Convert to x1,y1,x2,y2
    for i in range(len(person_output_56)):
      x_center, y_center, w, h = person_output_56[i][0:4]
      x1 = int(x_center - w/2)
      y1 = int(y_center - h/2)
      x2 = int(x_center + w/2)
      y2 = int(y_center + h/2)
      conf = person_output_56[i][4]
      person_output.append([x1,y1,x2,y2,conf])
    
    # for each person -> body part detection
    person_wise_keypoints_output = []
    for person in person_output_56:
      person_keypoints = person[5:].reshape(17,3)
      # exclude keypoints with confidence less than body_part_conf_thresh
      person_keypoints = person_keypoints[person_keypoints[:,2] > body_part_conf_thresh]
      person_wise_keypoints_output.append(person_keypoints)
      
    # Generate bbox from keypoints using a +3 -3  
    person_wise_keypoints_bbox_output = []
    for person_keypoints in person_wise_keypoints_output:
      temp = []
      for keypoints in person_keypoints:
        x,y,c = keypoints[0],keypoints[1],keypoints[2]
        temp.append([x-3,y-3,x+3,y+3,c])
      person_wise_keypoints_bbox_output.append(temp)

    # hands only (9th and 10th keypoints)
    person_wise_hand_keypoints_output = [person_keypoints[[9,10]] for person_keypoints in person_wise_keypoints_output]
    person_wise_hand_keypoints_bbox_output = []
    for person_keypoints in person_wise_hand_keypoints_output:
      temp = []
      for keypoints in person_keypoints:
        x,y,c = keypoints[0],keypoints[1],keypoints[2]
        temp.append([x-3,y-3,x+3,y+3,c])
      person_wise_hand_keypoints_bbox_output.append(temp)
    
    # Serialize into (x1,y1,x2,y2,conf,cls) person_wise_keypoints_bbox_output
    serlized_person_wise_keypoints_bbox_output = []
    for i,person_keypoints_bbox in enumerate(person_wise_keypoints_bbox_output):
      for j,keypoints_bbox in enumerate(person_keypoints_bbox):
        x1,y1,x2,y2,conf = keypoints_bbox
        serlized_person_wise_keypoints_bbox_output.extend([x1,y1,x2,y2,conf,81+j])
    
    person_output_serlized = []
    for person in person_output:
        x1,y1,x2,y2,conf = person
        person_output_serlized.extend([x1,y1,x2,y2,conf,0])

    # serlize person_wise_hand_keypoints_bbox_output
    serlized_person_wise_hand_keypoints_bbox_output = []
    for i,person_keypoints_bbox in enumerate(person_wise_hand_keypoints_bbox_output):
      for j,keypoints_bbox in enumerate(person_keypoints_bbox):
        x1,y1,x2,y2,conf = keypoints_bbox
        serlized_person_wise_hand_keypoints_bbox_output.extend([x1,y1,x2,y2,conf,81+9+j])

    #  person_output : [x_center, y_center, width, height, conf, cls]
    #  person_wise_keypoints_bbox_output : [[x1,y1,x2,y2],[],[]]
    #  person_wise_hand_keypoints_bbox_output : [[x1,y1,x2,y2],[],[]]
    #  serlized_person_wise_keypoints_bbox_output : [[x1,y1,x2,y2,conf,cls],[],[]]

    return person_output, person_wise_keypoints_bbox_output,person_wise_hand_keypoints_bbox_output, {class_label_map:serlized_person_wise_hand_keypoints_bbox_output+person_output_serlized}









def main():
    # Start socket listener to receive messages from NXAI runtime
    post_request_handler = PostRequestHandler()
    server = communication_utils.startUnixSocketServer(Postprocessor_Socket_Path)
    # Wait for messages in a loop
    while True:
        # Wait for input message from runtime
        try:
            input_message, connection = communication_utils.waitForSocketMessage(server)
        except socket.timeout:
            # Request timed out. Continue waiting
            continue

        input_object = communication_utils.parseInferenceResults(input_message)
        # Deserialize the binary data to a numpy array
        decoded_data = decode_binary_to_array(input_object['Outputs']['output0'], input_object['OutputShapes'])


        # get_bounding_boxes
        person_output, person_wise_keypoints_bbox_output,person_wise_hand_keypoints_bbox_output,serialized_person_wise_keypoints_bbox_output = get_bbox_from_pose_output(decoded_data,person_conf_thresh=0.5,person_nms_thresh=0.5, body_part_conf_thresh=0.0)  
        encoded_boxes = tuple_to_bytes(tuple(serialized_person_wise_keypoints_bbox_output[list(serialized_person_wise_keypoints_bbox_output.keys())[0]]))

        # Get the product catalog key
        prod_catalog_key = list(prod_catalog[PROD_TYPE].keys())[0]
        prod_catalog_spec = prod_catalog[PROD_TYPE][prod_catalog_key]

        # Convert the product catalog to bytes
        encoded_prod_catalog_spec = tuple_to_bytes(prod_catalog_spec)

    
        output_object = {
            "Outputs": {
                "bboxes-format:xyxysc;"+';'.join([f"{k}:{v}" for k,v in categories.items()])+";"+list(serialized_person_wise_keypoints_bbox_output.keys())[0]+";"+prod_catalog_key:
                encoded_boxes+encoded_prod_catalog_spec
            },
        
            'OutputRanks': [2],
            'OutputShapes': [[len(encoded_boxes+encoded_prod_catalog_spec)//6, 6]],
            'OutputDataTypes': [1]
        }

        # Send the output to the Analysis Server
        post_request_handler.handle_post_request({
            "ProductType": PROD_TYPE,
            "person_wise_hand_keypoints_bbox_output": person_wise_hand_keypoints_bbox_output,
            "productgroup_wise_keypoints_bbox_output": convert_prod_catalog_to_dict(prod_catalog[PROD_TYPE])
        }
            ,endpoint="interaction")

        output_message = communication_utils.writeInferenceResults(output_object)
        # Send message back to runtime
        communication_utils.sendMessageOverConnection(connection, output_message)


def signalHandler(sig, _):
    print("python3 | EXAMPLE PLUGIN: Received interrupt signal: ", sig)
    sys.exit(0)


if __name__ == "__main__":
    print("python3 | EXAMPLE PLUGIN: Input parameters: ", sys.argv)
    # Parse input arguments
    if len(sys.argv) > 1:
        Postprocessor_Socket_Path = sys.argv[1]
    # Handle interrupt signals
    signal.signal(signal.SIGINT, signalHandler)
    # Start program
    main()
