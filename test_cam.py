import cv2

def test_camera_indices(max_indices=5):
    for i in range(max_indices):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            print(f"Câmera encontrada no índice {i}")
            cap.release()
        else:
            print(f"Nenhuma câmera no índice {i}")

if __name__ == "__main__":
    test_camera_indices()
