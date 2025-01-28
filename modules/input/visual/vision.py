import cv2
import torch

def handle_jarvisVision():
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")

    try:
        model = torch.hub.load('ultralytics/yolov5', 'custom', path='yolov5s.pt', force_reload=True)
        model = model.to(device)
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    while True:
        try:
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Preprocess the image
            img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (640, 640))
            img_tensor = torch.from_numpy(img).permute(2, 0, 1).float() / 255.0
            img_tensor = img_tensor.unsqueeze(0).to(device)
            print("Image tensor shape before model:", img_tensor.shape)

            with torch.no_grad():
                results = model(img_tensor)
            
            # Check if results is a tensor
            if isinstance(results, torch.Tensor):
                # Assuming the tensor has the shape [batch, num_detections, attributes]
                # Where attributes should at least include [x1, y1, x2, y2, conf, cls]
                for detection in results[0]:  # Accessing first (and only) batch item
                    try:
                        if detection.numel() >= 6:  # Check if we have at least 6 items
                            x1, y1, x2, y2, conf, cls = detection[:6]
                            x1, y1, x2, y2 = map(int, [x1.item(), y1.item(), x2.item(), y2.item()])
                            conf = conf.item()
                            cls = cls.item()
                            
                            #cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            label = f'{model.names[int(cls)]} {conf:.2f}'
                            #cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (36,255,12), 2)
                        else:
                            print(f"Detection does not have enough elements: {detection.numel()}")
                    except Exception as e:
                        print(f"Error processing detection tensor: {e}")
            else:
                print("Unexpected results format:", type(results))

            cv2.imshow('Object Detection', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        except Exception as e:
            print(f"An error occurred in the main loop: {e}")
            continue

    cap.release()
    cv2.destroyAllWindows()
    return True

if __name__ == "__main__":
    try:
        if handle_jarvisVision():
            print("Vision handling completed successfully.")
        else:
            print("Vision handling failed.")
    except Exception as e:
        print(f"An error occurred outside the main loop: {e}")