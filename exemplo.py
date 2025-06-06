import cv2
import threading
import time
from ultralytics import YOLO
from pyzbar.pyzbar import decode as pyzbar_decode
from database.database_handler import DatabaseHandler

def montar_placa(detections):
    # Recebe a lista de detecções dos caracteres (com classes e caixas)
    # Ordena os caracteres pela posição horizontal (x)
    # Junta os caracteres para formar a placa
    # Retorna string da placa
    chars = sorted(detections, key=lambda d: d['x'])
    placa = ''.join([d['class_name'] for d in chars])
    return placa

def processar_frame(frame, model_placa, model_chars, db):
    results_placa = model_placa(frame)[0]
    results_chars = model_chars(frame)[0]

    placas = []
    for placa_det in results_placa.boxes:
        x1, y1, x2, y2 = map(int, placa_det.xyxy[0])
        # crop da região da placa
        placa_crop = frame[y1:y2, x1:x2]

        # Detecta caracteres dentro da placa_crop
        chars_det = model_chars(placa_crop)[0].boxes
        
        # Monta lista de caracteres com coordenadas relativas (ajuste necessário)
        detections_chars = []
        for char_det in chars_det:
            x_c, y_c = (char_det.xyxy[0][0] + char_det.xyxy[0][2]) / 2, (char_det.xyxy[0][1] + char_det.xyxy[0][3]) / 2
            class_id = int(char_det.cls[0])
            class_name = model_chars.names[class_id]
            detections_chars.append({'class_name': class_name, 'x': x_c})

        placa_texto = montar_placa(detections_chars)
        autorizado = db.verificar_autorizado('placa', placa_texto)
        placas.append({'bbox': (x1, y1, x2, y2), 'texto': placa_texto, 'autorizado': autorizado})

    # Leitura do QR code com pyzbar
    qr_codes = pyzbar_decode(frame)
    qrcodes_detectados = []
    for qr in qr_codes:
        qr_data = qr.data.decode('utf-8')
        autorizado = db.verificar_autorizado('qrcode', qr_data)
        qrcodes_detectados.append({'bbox': qr.rect, 'data': qr_data, 'autorizado': autorizado})

    return placas, qrcodes_detectados

def desenhar_resultados(frame, placas, qrcodes):
    # Placas
    for p in placas:
        x1, y1, x2, y2 = p['bbox']
        cor = (0, 255, 0) if p['autorizado'] else (0, 0, 255)
        cv2.rectangle(frame, (x1, y1), (x2, y2), cor, 2)
        cv2.putText(frame, p['texto'], (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)
        status = "AUTORIZADO" if p['autorizado'] else "NÃO AUTORIZADO"
        cv2.putText(frame, status, (x1, y2 + 30), cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)

    # QR Codes
    for qr in qrcodes:
        x, y, w, h = qr['bbox']
        cor = (0, 255, 0) if qr['autorizado'] else (0, 0, 255)
        cv2.rectangle(frame, (x, y), (x + w, y + h), cor, 2)
        cv2.putText(frame, qr['data'], (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)
        status = "AUTORIZADO" if qr['autorizado'] else "NÃO AUTORIZADO"
        cv2.putText(frame, status, (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, cor, 2)

def main():
    db = DatabaseHandler()
    model_placa = YOLO('best_placa.pt')      # Modelo treinado para placas
    model_chars = YOLO('best_chars.pt')      # Modelo treinado para caracteres

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        placas, qrcodes = processar_frame(frame, model_placa, model_chars, db)
        desenhar_resultados(frame, placas, qrcodes)

        cv2.imshow("Detecção Placa + QR Code", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
