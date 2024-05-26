from flask import Flask, render_template, Response
from camera import VideoCamera

video_list = {
    "0":0,
    "Cereals Copurchase":"https://rategain2023.s3.ap-south-1.amazonaws.com/videos/Cereals+Copurchase.mp4",
    "Fish theft":"https://rategain2023.s3.ap-south-1.amazonaws.com/videos/Fish+theft.mp4",
    "Shaving Copurchase":"https://rategain2023.s3.ap-south-1.amazonaws.com/videos/Shaving+Copurchase.mp4",
    "Wine theft":"https://rategain2023.s3.ap-south-1.amazonaws.com/videos/Wine+theft.mp4"
}



import cv2

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
                # 1.2 x zoom
                # img = cv2.resize(img, (0,0), None, 1.2, 1.1)
                if success == True:
                    print(img.shape)
                    print("SUCCESSS")
                    yield img
                else:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            # cap = cv2.VideoCapture(path_x)
        # except:
        #     cap = cv2.VideoCapture(path_x)
        #     print("BRUH")



def generate_frames(path_x = ''):
    somewhere = video_detection(path_x)
    for detection_ in somewhere:
        ref,buffer=cv2.imencode('.jpg',detection_)

        frame=buffer.tobytes()
        # yield (b'--frame\r\n'
        #             b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# @app.route('/v')
# def video_feed():
#     return Response(gen(VideoCamera(URL = "https://drive.google.com/uc?export=view&id=1DvjBD42U1ifiVvbeE3mi1y5kPwu_5O_K")),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/v2')
# def video():
#     return Response(generate_frames(path_x = "https://drive.google.com/uc?export=view&id=1mNqcLgeFwcJ_jMppnG9HMY9Xl9NAd-xz"),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


# @app.route('/v2')
# def video():
#     return Response(generate_frames(path_x = "https://cdn.discordapp.com/attachments/871472954486194206/1243467852854595595/Fish_theft.mp4?ex=6651952e&is=665043ae&hm=0164cd260e078f938114671ab761b004272a9ecbc6d9ae856f9a98580ae2fbae&"),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/v2')
def video2():
    return Response(generate_frames(path_x = video_list["Cereals Copurchase"]),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/v3')
def video3():
    return Response(generate_frames(path_x = video_list["Fish theft"]),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/v4')
def video4():
    return Response(generate_frames(path_x = video_list["Shaving Copurchase"]),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/v5')
def video5():
    return Response(generate_frames(path_x = video_list["Wine theft"]),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/v3')
# def video2():
#     return Response(gen(VideoCamera2(URL = "https://drive.google.com/uc?export=view&id=1DvjBD42U1ifiVvbeE3mi1y5kPwu_5O_K")),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(port=8081,host='0.0.0.0', debug=True)