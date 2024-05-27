from flask import Flask, render_template, Response
import cv2

# Camera Servers to stream the video at http ports from videos from S3 bucket
# The videos are stored in S3 bucket and the links are provided below

# Camera wise video links
video_list = {
    "0":0,
    "Cereals Copurchase":"https://rategain2023.s3.ap-south-1.amazonaws.com/videos/Cereals+Copurchase.mp4",
    "Fish theft":"https://rategain2023.s3.ap-south-1.amazonaws.com/videos/Fish+theft.mp4",
    "Shaving Copurchase":"https://rategain2023.s3.ap-south-1.amazonaws.com/videos/Shaving+Copurchase.mp4",
    "Wine theft":"https://rategain2023.s3.ap-south-1.amazonaws.com/videos/Wine+theft.mp4"
}



app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_detection(path_x):
    
    cap = cv2.VideoCapture(path_x)
    while True:
        # try:
            while cap.isOpened():
                success, img = cap.read()
                if success == True:
                    print(img.shape)
                    print("SUCCESSS")
                    yield img
                else:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)



def generate_frames(path_x = ''):
    somewhere = video_detection(path_x)
    for detection_ in somewhere:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


# This is the main function to stream the video from S3 bucket | Camera : Cereal Section
@app.route('/v2')
def video2():
    return Response(generate_frames(path_x = video_list["Cereals Copurchase"]),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


# This is the main function to stream the video from S3 bucket | Camera : Fish Section
@app.route('/v3')
def video3():
    return Response(generate_frames(path_x = video_list["Fish theft"]),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# This is the main function to stream the video from S3 bucket | Camera : Shaving Section
@app.route('/v4')
def video4():
    return Response(generate_frames(path_x = video_list["Shaving Copurchase"]),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# This is the main function to stream the video from S3 bucket | Camera : Wine Section
@app.route('/v5')
def video5():
    return Response(generate_frames(path_x = video_list["Wine theft"]),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    app.run(port=8081,host='0.0.0.0', debug=True)
