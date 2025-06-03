import csv, boto3, io, cv2, re, os
from PIL import Image, ImageDraw

access_key_id = os.environ.get('AWS_ACCESS_KEY_ID')
secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')

if not access_key_id or not secret_access_key:
    try:
        with open('trafficproject_accessKeys.csv', 'r') as file:
            next(file)
            reader = csv.reader(file)
            for line in reader:
                access_key_id = line[0]
                secret_access_key = line[1]
    except FileNotFoundError:
        print("❌ Credentials not found in environment or CSV.")
        exit(1)

client = boto3.client(
    'rekognition',
    region_name='ap-south-1',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key
)

dynamodb = boto3.resource(
    'dynamodb',
    region_name='ap-south-1',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key
)

sns = boto3.client(
    'sns',
    region_name='ap-south-1',
    aws_access_key_id=access_key_id,
    aws_secret_access_key=secret_access_key
)

def send_violation_sms(phone_number, message):
    response = sns.publish(
        PhoneNumber='+' + str(phone_number),
        Message=message
    )
    print("📤 SMS sent! Message ID:", response['MessageId'])

def lookup_phone_number(plate_number):
    table = dynamodb.Table('trafficproj')
    response = table.get_item(Key={'license': plate_number})
    if 'Item' in response:
        phone = response['Item']['phone']
        print(f"📞 Phone number linked to {plate_number}: {phone}")
        return phone
    else:
        print(f"License plate {plate_number} not found in database.")
        return None

def detect_license_plate(image_bytes):
    response = client.detect_text(Image={'Bytes': image_bytes})
    for text_detail in response['TextDetections']:
        text = text_detail['DetectedText']
        if re.match(r'^[A-Z]{2}\d{1,2}[A-Z]{1,2}\d{4}$', text):
            print(f"🔍 Possible plate number: {text}")
            return text
    print("⚠️ No valid license plate detected.")
    return None

def analyze_frame(src):
    detect = client.detect_labels(Image={'Bytes': src})
    image = Image.open(io.BytesIO(src))
    draw = ImageDraw.Draw(image)
    
    people_centers = []
    motorcycle_centers = []
    has_helmet = False
    has_motorcycle = False
    has_person = False
    has_phone = False

    for label in detect['Labels']:
        if label['Name'] in ['Helmet', 'Crash Helmet', 'Hardhat'] and label['Confidence'] > 86:
            has_helmet = True
        if label['Name'] == 'Mobile Phone':
            has_phone = True

        for inst in label.get('Instances', []):
            if 'BoundingBox' in inst:
                box = inst['BoundingBox']
                left = image.width * box['Left']
                top = image.height * box['Top']
                width = image.width * box['Width']
                height = image.height * box['Height']

                center_x = box['Left'] + box['Width'] / 2
                if label['Name'] in ['Person', 'Man', 'Woman', 'Human', 'Teen']:
                    has_person = True
                    people_centers.append(center_x)
                elif label['Name'] in ['Motorcycle', 'Scooter', 'Moped', 'Bike']:
                    has_motorcycle = True
                    motorcycle_centers.append(center_x)

                draw.rectangle([(left, top), (left + width, top + height)], outline='red', width=3)
                draw.text((left, top - 15), label['Name'], fill='black')

    plate_number = detect_license_plate(src)
    phone_number = None
    if plate_number:
        phone_number = lookup_phone_number(plate_number)

    violation_messages = []

    if has_person and has_motorcycle and not has_helmet:
        msg = "🚨 Helmet violation detected."
        print(msg)
        violation_messages.append(msg)
    else:
        print("✅ No helmet violation detected.")

    violation_found = False
    for moto_center in motorcycle_centers:
        nearby_people = [p for p in people_centers if abs(p - moto_center) < 0.4]
        if len(nearby_people) >= 3:
            msg = "🚨 Triple riding violation detected."
            print(msg)
            violation_messages.append(msg)
            violation_found = True
            break
    if not violation_found:
        print("✅ No triple riding detected.")

    if has_phone:
        msg = "🚨 Phone usage while riding detected."
        print(msg)
        violation_messages.append(msg)
    else:
        print("✅ No phone usage detected.")

    if phone_number and violation_messages:
        send_violation_sms(phone_number, "\n".join(violation_messages))

    image.show()

def process_video(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    interval = 150

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % interval == 0:
            success, encoded_image = cv2.imencode('.jpg', frame)
            if success:
                src = encoded_image.tobytes()
                print(f"\nAnalyzing frame {frame_count}...")
                analyze_frame(src)
        frame_count += 1

    cap.release()

def process_webcam():
    cap = cv2.VideoCapture(0)  # 0 = default webcam
    if not cap.isOpened():
        print("❌ Cannot access webcam.")
        return

    print("📸 Press 's' to analyze frame, or 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break
        cv2.imshow("Webcam - Press 's' to Analyze", frame)

        key = cv2.waitKey(1)
        if key == ord('s'):
            success, encoded_image = cv2.imencode('.jpg', frame)
            if success:
                src = encoded_image.tobytes()
                print("✅ Analyzing captured webcam frame...")
                analyze_frame(src)
            break
        elif key == ord('q'):
            print("Exiting webcam...")
            break

    cap.release()
    cv2.destroyAllWindows()

def process_image(photo_path):
    with open(photo_path, 'rb') as img:
        src = img.read()
    analyze_frame(src)

#input_type = int(input("Enter 1 for image, 2 for webcam or 3 for video: "))
import sys
def get_user_input():
    try:
        # If args are passed, use them
        if len(sys.argv) >= 2:
            input_type = int(sys.argv[1])
            input_path = sys.argv[2] if len(sys.argv) > 2 else None
        else:
            # Fallback to interactive input
            input_type = int(input("Enter 1 for image, 2 for webcam or 3 for video: "))
            input_path = input("Enter path to input file (or leave blank for webcam): ") if input_type in [1, 3] else None
        return input_type, input_path
    except Exception as e:
        print(f"❌ Invalid input: {e}")
        sys.exit(1)

if __name__ == "__main__":
    input_type, path = get_user_input()

    if input_type == 1:
        print(f"📷 Processing image: {path}")
        process_image(path)
    elif input_type == 2:
        print("🎥 Accessing webcam...")
        process_webcam()
    elif input_type == 3:
        print(f"🎞️ Processing video: {path}")
        process_video(path)
    else:
        print("❌ Invalid input type. Choose 1 (image), 2 (webcam), or 3 (video).")