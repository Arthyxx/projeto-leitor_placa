import cv2
from pyzbar import pyzbar
from database.database_handler import DatabaseHandler

def ler_qr_code():
    db = DatabaseHandler()
    cap = cv2.VideoCapture(1)

    print("Abrindo câmera... Pressione 'q' para sair.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Erro ao capturar o vídeo")
            break

        decoded_objs = pyzbar.decode(frame)

        for obj in decoded_objs:
            qr_data = obj.data.decode('utf-8')
            autorizado = db.verificar_autorizado('qrcode', qr_data)
            status = "AUTORIZADO" if autorizado else "NÃO AUTORIZADO"

            (x, y, w, h) = obj.rect
            color = (0, 255, 0) if autorizado else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, f"{status}: {qr_data}", (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            
            print(f"QR Code detectado: {qr_data} - {status}")

        cv2.imshow("Leitor de QR Code", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    ler_qr_code()
