# import cv2
# # pip install opencv-python
# # pip install opencv-python --trusted-host pypi.org --trusted-host files.pythonhosted.org

# print(cv2.__version__)


# face_detector = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

# video_capture = cv2.VideoCapture(0)

# while True:
#     # Capture frame-by-frame
#     ret, frame = video_capture.read()

#     image_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#     detections = face_detector.detectMultiScale(image_gray, minSize=(100,100))

#     # Draw a rectangle around the faces
#     for (x, y, w, h) in detections:
#         print(w, h)
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

#     # Display the resulting frame
#     cv2.imshow('Video', frame)

#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # When everything is done, release the capture
# video_capture.release()
# cv2.destroyAllWindows()



import cv2

video_capture = cv2.VideoCapture(0)

face_detector = cv2.CascadeClassifier(
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
)

while True:
    ret, frame = video_capture.read()
    if not ret:
        break

    image_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    detections = face_detector.detectMultiScale(image_gray, minSize=(100, 100))

    for (x, y, w, h) in detections:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

    cv2.imshow("Video", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

video_capture.release()
cv2.destroyAllWindows()