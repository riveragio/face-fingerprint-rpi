import cv2

cam_port = 0
cam = cv2.VideoCapture(cam_port)

inp = input('Enter person name: ')

# Warm up the camera (optional but helps)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    ret, frame = cam.read()
    
    if not ret:
        print("No image detected. Please try again.")
        break

    cv2.imshow(inp, frame)

    key = cv2.waitKey(1) & 0xFF

    # Press 's' to save the image
    if key == ord('s'):
        cv2.imwrite(inp + ".png", frame)
        print("Image saved as", inp + ".png")
        break

    # Press 'q' to quit without saving
    elif key == ord('q'):
        print("Exiting without saving.")
        break

cam.release()
cv2.destroyAllWindows()

