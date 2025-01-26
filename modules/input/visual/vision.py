import cv2
print(cv2.getBuildInformation())
import torch
from yolov5 import YOLOv5

def handle_jarvisVision():
    # Check if CUDA is available for GPU acceleration
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    # Load YOLOv5 model (you need to download the weights first)
    model = YOLOv5('yolov5s.pt')

    # Open webcam (1) - secondary camera
    cap = cv2.VideoCapture(1)

    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    # Set the resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        # Convert the image from BGR to RGB since YOLO expects RGB
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Inference
        # Note: Check if 'predict' is the correct method for your version of YOLOv5
        # If 'predict' doesn't work, refer to documentation for the correct method
        results = model.predict(img)

        # Process results
        for *xyxy, conf, cls in results.xyxy[0].cpu().numpy():
            # Draw a rectangle around the detected objects
            x1, y1, x2, y2 = map(int, xyxy)
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Display the resulting frame
        cv2.imshow('Object Detection', frame)

        # Press 'q' to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the capture
    cap.release()
    cv2.destroyAllWindows()
    return True

# To use the function
if __name__ == "__main__":
    handle_jarvisVision()  # Changed to match the function name