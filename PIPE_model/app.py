from cloudinary import uploader,config
from flask import Flask, request,jsonify , render_template,send_file
from flask_cors import CORS
from functools import wraps
import ultralytics
import json
import uuid
import requests
import os
import time
from werkzeug.utils import secure_filename
import cloudinary.uploader
from draw_on_image import draw_bounding_boxes_number , draw_bounding_boxes


model_name = "best.pt"
confidence_threshold = .6


save_dir = "saved_results"


model = ultralytics.YOLO(model_name)

app = Flask(__name__)

CORS(app, origins='*')

# Cloudinary configuration
config(
    cloud_name="",
    api_key="",
    api_secret="",
)


def load_credentials():
    with open('credentials.json') as f:
        return json.load(f)


credentials = load_credentials()



def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract the authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'message': 'Missing Authorization Header'}), 401

        # Attempt to extract the token type and token value
        parts = auth_header.split()
        if parts[0].lower() != 'bearer' or len(parts) != 2:
            return jsonify({'message': 'Invalid Authorization Header'}), 401

        token = parts[1]
        if token != credentials['token']:
            return jsonify({'message': 'Invalid or expired token'}), 401

        return f(*args, **kwargs)

    return decorated_function

@app.route('/login', methods=['POST'])
def login():
    # Extract submitted credentials
    auth_request = request.json
    username = auth_request.get('username')
    password = auth_request.get('password')

    # Validate credentials
    if username == credentials['username'] and password == credentials['password']:
        # Return the token if credentials are valid
        return jsonify({'token': credentials['token']})
    else:
        # Return error if credentials are invalid
        return jsonify({'message': 'Invalid username or password'}), 401


def download_image(url, save_path, down_image, max_attempts=10, retry_delay=1):
    attempts = 0
    while attempts < max_attempts:
        try:
            # Send a GET request to the URL
            response = requests.get(url, stream=True,timeout=2)
            # Check if the request was successful (status code 200)
            if response.status_code == 200:
                # Read the content immediately to ensure the entire file is downloaded
                content = response.content
                # Open a file in binary write mode and save the content of the response
                with open(os.path.join(save_path, down_image), 'wb') as file:
                    file.write(content)
                print(f"Image downloaded successfully: {down_image}")
                return  True
            else:
                print(f"Failed to download image (attempt {attempts+1}/{max_attempts}): {response.status_code}")
        except Exception as e:
            print(f"An error occurred (attempt {attempts+1}/{max_attempts}): {e}")
        attempts += 1
        time.sleep(retry_delay)

    print("Failed to download image after multiple attempts")
    return False


@app.route('/api-doc',methods=['GET'])
def api_doc():
    return render_template('index.html')




@app.route('/cloudinary', methods=['POST'])
@authenticate
def detect_objects():
    delete_folder_contents("/code/runs/detect/")
    image_path = request.json.get('image_path')
    down_image = "downimage.jpg"

    if not download_image(image_path,"/code/",down_image):
        return jsonify({
            "Error":"Error While Downloading Image"
       })

    if 'confidence_threshold' in request.json:
        confidence_threshold = float(request.json.get("confidence_threshold"))


    # results = model.predict(source="/code/"+down_image, conf=confidence_threshold, save=True, hide_labels=True, save_txt=True)
    results = model.predict(source="/code/" + down_image, conf=confidence_threshold,
                            save=True, hide_labels=True, save_txt="/code/output.txt")

    string_content = str(len(results[0]))
    color = '#FFFFFF'
    if(int(string_content) > 0):
        draw_bounding_boxes("/code/" + down_image, "/code/runs/detect/predict/labels/downimage.txt",
                        "/code/" + "edit_" + down_image,color)

    file_name = get_filename_in_path("/code/runs/detect/predict/");
    image_path = "/code/runs/detect/predict/" + file_name

    result_image = uploader.upload("edit_" + down_image, public_id="pixelpipers")
    image_url = result_image['secure_url']

    return jsonify({
        'count': string_content,
        'image_url' : image_url
    })





@app.route('/frontend', methods=['POST'])
@authenticate
def from_frontend():
    confidence_threshold = .6
    # delete_folder_contents("/code/runs/detect/")
    if "uploadImage" not in request.files:
        return jsonify({
            "Error":"Where is Image ?"
        })
    file = request.files['uploadImage']
    if file.filename == "":
        return jsonify({
            "Error":"No file Selected"
        })
    if file:
        file_extension = ".jpg"
        image_name = str(uuid.uuid4())
        down_image = image_name + str(file_extension)
        file.save(os.path.join('/code', down_image))


    key = 0
    color = '#FFFFFF'

    if 'confidence_threshold' in request.form:
        confidence_threshold = float(request.form.get("confidence_threshold"))

    if 'key' in request.form:
        key = int(request.form.get('key'))

    if 'color' in request.form:
        color = str(request.form.get('color'))

    font_scale = .5
    if 'font_scale' in request.form:
        font_scale = float(request.form.get('font_scale'))


    results = model.predict(source="/code/" + down_image, conf=confidence_threshold, save=True,hide_labels=True, save_txt=True)


    string_content = str(len(results[0]))

    default_path = os.path.join(os.getcwd(), "runs", "detect")
    latest_subdirectory = max([os.path.join(default_path, f) for f in os.listdir(default_path) if
                               os.path.isdir(os.path.join(default_path, f))], key=os.path.getmtime)

    # print("latest dir :",latest_subdirectory)

    if (int(string_content) > 0):
        if key == 0:
            draw_bounding_boxes("/code/" + down_image,latest_subdirectory+"/labels/"+image_name+".txt","/code/"+"edit_"+down_image,color)
        else:
            draw_bounding_boxes_number("/code/" + down_image,latest_subdirectory+"/labels/"+image_name+".txt","/code/"+"edit_"+down_image,color,font_scale)


    if (int(string_content) == 0):
        result_image = cloudinary.uploader.upload('/code/' + down_image, folder='pixelpipers')
    else:
        result_image = cloudinary.uploader.upload("edit_" + down_image, folder='pixelpipers')
        os.remove('/code/edit_' + down_image)

    image_url = result_image['secure_url']

    # if(int(string_content)==0):
    #     result_image = uploader.upload('/code/' + down_image, public_id="pixelpipers")
    # else:
    #     result_image = uploader.upload("edit_" + down_image, public_id="pixelpipers")
    #     os.remove('/code/edit_' + down_image)
    # image_url = result_image['secure_url']

    delete_folder_contents(latest_subdirectory)
    os.rmdir(latest_subdirectory)
    os.remove('/code/' + down_image)

    # delete_folder_contents("/code/runs/detect/")

    return jsonify({
        'count': string_content,
        'image_url': image_url
    })





@app.route('/coordinates', methods=['POST'])
@authenticate
def from_coordinate():
    confidence_threshold = .6
    # delete_folder_contents("/code/runs/detect/")
    if "uploadImage" not in request.files:
        return jsonify({
            "Error":"Where is Image ?"
        })
    file = request.files['uploadImage']
    if file.filename == "":
        return jsonify({
            "Error":"No file Selected"
        })
    if file:
        file_extension = ".jpg"
        image_name = str(uuid.uuid4())
        down_image = image_name+str(file_extension)
        file.save(os.path.join('/code', down_image))



    if 'confidence_threshold' in request.form:
        confidence_threshold = float(request.form.get("confidence_threshold"))

    label_txt_folder = '/code/labels/'

    results = model.predict(source="/code/" + down_image, conf=confidence_threshold ,show_labels=True, save_txt=True)

    os.remove('/code/'+down_image)
    string_content = str(len(results[0]))
    # print(string_content)

    default_path = os.path.join(os.getcwd(), "runs", "detect")
    latest_subdirectory = max([os.path.join(default_path, f) for f in os.listdir(default_path) if
                               os.path.isdir(os.path.join(default_path, f))], key=os.path.getmtime)

    # print("hel : ",latest_subdirectory)
    if(int(string_content) == 0):
        os.rmdir(latest_subdirectory+'/labels')
        os.rmdir(latest_subdirectory)
        return jsonify({
            'count': string_content,
            'coordinates': []
        })

    txt_path = os.path.join(latest_subdirectory, "labels/"+image_name+".txt")
    # print("yea le :",txt_path)

    data = read_lines_from_file(txt_path)

    # print(f"Label txt file saved at: {txt_path}")
    # print(latest_subdirectory)
    delete_folder_contents(latest_subdirectory)
    os.rmdir(latest_subdirectory)



    return jsonify({
        'count': string_content,
        'coordinates': data
    })



import base64


@app.route('/images', methods=['POST'])
@authenticate
def from_frontend_image():
    confidence_threshold = 0.6
    if "uploadImage" not in request.files:
        return jsonify({"Error": "Where is Image ?"})

    file = request.files['uploadImage']
    if file.filename == "":
        return jsonify({"Error": "No file selected"})

    if file:
        file_extension = ".jpg"
        image_name = str(uuid.uuid4())
        down_image = image_name + str(file_extension)
        file.save(os.path.join('/code', down_image))

    key = 0
    if 'confidence_threshold' in request.form:
        confidence_threshold = float(request.form.get("confidence_threshold"))

    if 'key' in request.form:
        key = int(request.form.get('key'))

    results = model.predict(source="/code/" + down_image, conf=confidence_threshold, save=True, hide_labels=True, save_txt=True)
    string_content = str(len(results[0]))

    default_path = os.path.join(os.getcwd(), "runs", "detect")
    latest_subdirectory = max([os.path.join(default_path, f) for f in os.listdir(default_path) if os.path.isdir(os.path.join(default_path, f))], key=os.path.getmtime)

    if int(string_content) > 0:
        if key == 0:
            draw_bounding_boxes("/code/" + down_image, latest_subdirectory + "/labels/" + image_name + ".txt", "/code/" + "edit_" + down_image)
        else:
            draw_bounding_boxes_number("/code/" + down_image, latest_subdirectory + "/labels/" + image_name + ".txt", "/code/" + "edit_" + down_image)

    if int(string_content) == 0:
        with open('/code/' + down_image, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
    else:
        with open('/code/edit_' + down_image, "rb") as img_file:
            image_base64 = base64.b64encode(img_file.read()).decode('utf-8')
        os.remove('/code/edit_' + down_image)

    delete_folder_contents(latest_subdirectory)
    os.rmdir(latest_subdirectory)
    os.remove('/code/' + down_image)

    return jsonify({'count': string_content, 'image_base64': image_base64})











@app.route('/retrain', methods=['POST'])
@authenticate
def retrain():
    # Check if the request contains image and text files
    if "uploadImage" not in request.files:
        return jsonify({
            "Error": "Where is Image File ?"
        })
    if "uploadTxt" not in request.files:
        return jsonify({
            "Error": "Where is Text File ?"
        })

    # Get the files from the request
    image_file = request.files['uploadImage']
    text_file = request.files['uploadTxt']

    # Get the 'x' value from the request or use a default value if not provided
    x_value = count_files_in_folder("/code/collect-retrain/images/")

    # Rename image file
    image_filename = secure_filename(f'annotation_data_{x_value}.' + image_file.filename.rsplit('.', 1)[1])
    # Rename text file
    text_filename = secure_filename(f'annotation_data_{x_value}.' + text_file.filename.rsplit('.', 1)[1])

    # Save image to /code/collect-retrain/images
    image_path = os.path.join('/code/collect-retrain/images', image_filename)
    image_file.save(image_path)

    # Save text to /code/collect-retrain/labels
    text_path = os.path.join('/code/collect-retrain/labels', text_filename)
    text_file.save(text_path)

    return jsonify({
        "Success": "Files uploaded and saved successfully.",
        "Image_path": image_path,
        "Text_path": text_path
    })


def delete_folder_contents(path):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            os.remove(item_path)
        elif os.path.isdir(item_path):
            delete_folder_contents(item_path)
            os.rmdir(item_path)


def get_filename_in_path(path):
    for item in os.listdir(path):
        item_path = os.path.join(path, item)
        if os.path.isfile(item_path):
            return item
    return None


def read_lines_from_file(file_path):
    lines = []
    with open(file_path, 'r') as file:
        for line in file:
            lines.append(line.strip())  # Append each line to the list after stripping newline characters
    return lines


def count_files_in_folder(folder_path):
    # Ensure the folder exists
    if not os.path.exists(folder_path):
        return 0

    # Initialize count variable
    count = 0

    # Iterate over the files in the folder
    for _, _, files in os.walk(folder_path):
        count += len(files)

    return count



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5000)
