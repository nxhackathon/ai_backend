# Flask server to recieve the detection streams 
# Run at 192.168.0.108(localhost) port 8888

from flask import Flask, request, Response
import json
from collections import defaultdict
import datetime
import numpy as np
import cv2

app = Flask(__name__)

# to handle f"http://192.168.0.114:8888/detection?postprocessorid={POST_PROCESSOR_ID}"

class JSONHandler:
    def __init__(self, gap=10, filename='data.json'):
        self.camwise_data = {}
        self.latest_timestamp = None
        self.gap = gap
        self.filename = filename

    def update_json(self, data, postprocessorid):
        if postprocessorid not in self.camwise_data:
            self.camwise_data[postprocessorid] = {}
            self.camwise_data[postprocessorid]['productgroup_wise_keypoints_bbox_output']=data['productgroup_wise_keypoints_bbox_output']
            self.camwise_data[postprocessorid]['person_time_wise_hand_keypoints'] = []

        if len(data['person_wise_hand_keypoints_bbox_output']) > 0:
            self.camwise_data[postprocessorid]['person_time_wise_hand_keypoints'].append({
                'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'person_wise_hand_keypoints_bbox_output': data['person_wise_hand_keypoints_bbox_output']
            })
            self.write_file()

    def write_file(self):
        cur_timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if self.latest_timestamp is None:
            self.latest_timestamp = cur_timestamp
            with open(self.filename, 'w') as f:
                # print(self.camwise_data)
                json.dump(self.camwise_data, f, indent=4)
            print("File written successfully for the first time at ", self.filename)
        else:
            if (datetime.datetime.strptime(cur_timestamp, "%Y-%m-%d %H:%M:%S") - datetime.datetime.strptime(self.latest_timestamp, "%Y-%m-%d %H:%M:%S")).seconds >= self.gap:
                self.latest_timestamp = cur_timestamp
                with open(self.filename, 'w') as f:
                    # print(self.camwise_data)
                    json.dump(self.camwise_data, f, indent=4)
                print("File written successfully at ", self.filename)

        # # append ]]]}]}} at the end of the file
        # with open(self.filename, 'a') as f:
        #     f.write("]}]}]}")


JSON_HANDLERS = {
    # 'default': JSONHandler(),
    'Cereals Section': JSONHandler(gap=10, filename='prodwise_activity/CerealsSection.json'),
    'Fish Section': JSONHandler(gap=10, filename='prodwise_activity/FishSection.json'),
    'Shaving Section': JSONHandler(gap=10, filename='prodwise_activity/ShavingSection.json'),
    'Wine Section': JSONHandler(gap=10, filename='prodwise_activity/WineSection.json'),
}
ALL_CAMERAS = list(JSON_HANDLERS.keys())
ALL_CAMERA_PATHS = {key:value.filename for key,value in JSON_HANDLERS.items()}

TEMP_CAMERAS = ['Cereals Section', 'Fish Section', 'Shaving Section', 'Wine Section']
TEMP_ALL_CAMERA_PATHS = {
    'Cereals Section': 'prodwise_activity/CerealsSection.json',
    'Fish Section': 'prodwise_activity/FishSection2.json', 
    'Shaving Section': 'prodwise_activity/ShavingSection.json', # Not available
    'Wine Section': 'prodwise_activity/WineSection.json', # Not available
}




class ProductGrpMapping:
    def __init__(self, productgroup_wise_keypoints_bbox_output):
        self.product_grp_to_timeofinteraction = defaultdict(list)
        self.productgroup_wise_keypoints_bbox_output = productgroup_wise_keypoints_bbox_output
        
    def checkwithin(self, hand_xy, productgroup_xy):
        # hand_xy = hand_xy[0]* 480 / 640 , hand_xy[1]* 848 / 640
        productgroup_xy = productgroup_xy[0]* 640 /480  , productgroup_xy[1]* 848 / 640, productgroup_xy[2]* 640 /480, productgroup_xy[3]* 848 / 640
        if hand_xy[0] > productgroup_xy[0] and hand_xy[0] < productgroup_xy[2] and hand_xy[1] > productgroup_xy[1] and hand_xy[1] < productgroup_xy[3]:
            return True
        return False

    def process(self,hand_feed):
        """
        hand_feed = {
            "timestamp": 0,
            "person_wise_hand_keypoints_bbox_output": [
                [
                    [right_hand_x1, right_hand_y1, right_hand_x2, right_hand_y2, right_hand_score],
                    [left_hand_x1, left_hand_y1, left_hand_x2, left_hand_y2, left_hand_score]
                ],
                ... # person 2
            ]
        }
        """
        for person in hand_feed["person_wise_hand_keypoints_bbox_output"]:
            for hand in person:
                hand_xy = [(hand[0]+hand[2])/2, (hand[1]+hand[3])/2] # center of hand
                for product_grp, product_grp_xy in self.productgroup_wise_keypoints_bbox_output.items():
                    if self.checkwithin(hand_xy, product_grp_xy[0][:4]):
                        self.product_grp_to_timeofinteraction[product_grp].append(datetime.datetime.strptime(hand_feed["timestamp"], "%Y-%m-%d %H:%M:%S"))

         # remove duplicates
        for product_grp in self.product_grp_to_timeofinteraction:
            self.product_grp_to_timeofinteraction[product_grp] = list(set(self.product_grp_to_timeofinteraction[product_grp]))
            # sort
            self.product_grp_to_timeofinteraction[product_grp].sort()

    def process_all(self, hand_feed_list):
        for hand_feed in hand_feed_list:
            self.process(hand_feed)

    def analyze(self,timedelta=24,window_wise_count_threshold=1):
        # I want to take time window of timedelta=24 seconds starting from the minimum time of interaction wrt all product groups
        # At each window, group the products which falls under 24 seconds window for each product group

        # get the minimum time of interaction wrt all product groups
        # convert string to datetime
        min_time = min([min(self.product_grp_to_timeofinteraction[product_grp]) for product_grp in self.product_grp_to_timeofinteraction])
        max_time = max([max(self.product_grp_to_timeofinteraction[product_grp]) for product_grp in self.product_grp_to_timeofinteraction])
        time_left = min_time
        time_right = min_time + datetime.timedelta(seconds=timedelta)
        stride = datetime.timedelta(seconds=timedelta)

        product_grp_to_timeofinteraction_window = defaultdict(list)

        while time_right < max_time:
            cur_win_dict = {}
            for product_grp in self.product_grp_to_timeofinteraction:
                cur_win_dict = []
                for time in self.product_grp_to_timeofinteraction[product_grp]:
                    if time >= time_left and time <= time_right:
                        cur_win_dict.append(time.strftime("%Y-%m-%d %H:%M:%S"))
                product_grp_to_timeofinteraction_window[product_grp].append(cur_win_dict)
            time_left += stride
            time_right += stride

        # Mapping product group to window wise interaction count along with the time of first interaction
        product_grp_to_timeofinteraction_window = dict(product_grp_to_timeofinteraction_window)
        window_wise_count = {}
        for product_grp in product_grp_to_timeofinteraction_window:
            window_wise_count[product_grp] = [[len(product_grp_to_timeofinteraction_window[product_grp][i]),(min_time+datetime.timedelta(seconds=timedelta*i)).strftime("%Y-%m-%d %H:%M:%S")] for i in range(len(product_grp_to_timeofinteraction_window[product_grp]))]
            
        # In each window if there are more than 8 interactions, then add those products in a bucket
        # buckets contain list of list of products
        buckets = []
        for i in range(len(product_grp_to_timeofinteraction_window)):
            cur_bucket = []
            for product_grp in product_grp_to_timeofinteraction_window:
                if window_wise_count[product_grp][i][0] >=window_wise_count_threshold:
                    cur_bucket.append(product_grp)
            if len(cur_bucket) > 1:
                buckets.append(cur_bucket)
                
        # remove duplicates
        buckets = [list(bucket) for bucket in list(set([tuple(sorted(bucket)) for bucket in buckets]))]

        return product_grp_to_timeofinteraction_window,window_wise_count,buckets
        
    def get_product_grp_to_timeofinteraction(self):
        return self.product_grp_to_timeofinteraction
    

def anlayze_interaction(data):
    camera_wise_interaction_window = {}
    camera_wise_buckets = {}

    for camera in ALL_CAMERAS:
        try:
            prod_grp_mapping = ProductGrpMapping(data[camera]["productgroup_wise_keypoints_bbox_output"])
            prod_grp_mapping.process_all(data[camera]["person_time_wise_hand_keypoints"])
            prod_grp_mapping.get_product_grp_to_timeofinteraction();
            anl_res,window_wise_count,buckets = prod_grp_mapping.analyze()
            camera_wise_interaction_window[camera] = window_wise_count
            camera_wise_buckets[camera] = buckets
        except:
            print("! Error in camera:",camera)
            camera_wise_interaction_window[camera] = {}
            camera_wise_buckets[camera] = []

    with open('prodwise_activity/output_camera_wise_interaction_window.json', 'w') as f:
        print("-------------------------- Interaction Window --------------------------")
        print(camera_wise_interaction_window)
        camera_wise_interaction_window_json_data = json.dumps(camera_wise_interaction_window, indent=4)
        f.write(camera_wise_interaction_window_json_data)

    with open('prodwise_activity/output_camera_wise_buckets.json', 'w') as f:
        print("-------------------------- Buckets --------------------------")
        print(camera_wise_buckets)
        camera_wise_buckets_json_data = json.dumps(camera_wise_buckets, indent=4)
        f.write(camera_wise_buckets_json_data)
    

    return {
        "camera_wise_interaction_window_json_data": camera_wise_interaction_window,
        "camera_wise_buckets_json_data": camera_wise_buckets
    }




def anomaly_detect(data, threshold=1.2):
    frequencies = [int(item[0]) for item in data]
    mean = np.mean(frequencies)
    std_dev = np.std(frequencies)
    
    # Detect anomalies
    anomalies = []
    for i, (frequency, timestamp) in enumerate(data):
        z_score = (frequency - mean) / std_dev
        if abs(z_score) > threshold:
            anomalies.append((frequency, timestamp, z_score))
    
    return anomalies

def theft(data):
    all_anomalies = {}

    for cam in data:
        prod_wise_data = data[cam]
        cam_wise_data = []
        for prod in prod_wise_data:
            for freq, timestamp in prod_wise_data[prod]:
                if not cam_wise_data:
                    cam_wise_data.append([freq, timestamp])
                else:
                    for i in range(len(cam_wise_data)):
                        if cam_wise_data[i][1] == timestamp:
                            cam_wise_data[i][0] += freq
                            break
                    else:
                        cam_wise_data.append([freq, timestamp])
        # print(cam_wise_data)
        if len(cam_wise_data) > 0:
            anomalies = anomaly_detect(cam_wise_data)
            # print(anomalies)
            all_anomalies[cam] = anomalies
    
    # Convert anomalies to json
    all_anomalies = {cam: [[freq, timestamp, z_score] for freq, timestamp, z_score in anomalies] for cam, anomalies in all_anomalies.items()}
    return all_anomalies

















@app.route('/analysis', methods=['GET'])
def analysis():
    # combine all the data from all the cameras 
    # Mind it when connecting to the mongoDB
    data = {}
    for camera in TEMP_ALL_CAMERA_PATHS: # TEMP Set for testing
        try:
            with open(TEMP_ALL_CAMERA_PATHS[camera]) as f: # TEMP Set for testing
                data[camera] = json.load(f)[camera]
        except:
            print("Error in camera:",camera)
    
    report = anlayze_interaction(data) 
    report = json.dumps(report, indent=4)
    # return the camera_wise_buckets_json_data with status 200
    return Response(report, status=200)


@app.route('/theft', methods=['GET'])
def theft_analysis():
    with open('prodwise_activity/anam_output_camera_wise_interaction_window.json', 'r') as f: # TEMP Set for testing
        camera_wise_interaction_window = json.load(f) 
    theft_data = theft(camera_wise_interaction_window)
    theft_data = json.dumps(theft_data, indent=4)
    return Response(theft_data, status=200)
    


# endpoint = f"http://192.168.0.114:8888/{endpoint}?postprocessorid={POST_PROCESSOR_ID}"
@app.route('/interaction', methods=['POST'])
def interaction():
    data = request.get_json()
    json_data = json.loads(data)
    POST_PROCESSOR_ID = request.args.get('postprocessorid')
    print('-------- interaction -------- from ',POST_PROCESSOR_ID)
    # print('-------- Start Data --------')
    # print(json_data)
    # print('--------- End Data ---------')

    # JSON_HANDLERS[json_data['ProductType']].update_json(json_data, json_data['ProductType'])    # Temporarily disabled
    return Response(status=200)

if __name__ == '__main__':
    print('Server is running at http://192.168.0.114:8888')
    app.run(host='0.0.0.0', port=8888,debug=False)