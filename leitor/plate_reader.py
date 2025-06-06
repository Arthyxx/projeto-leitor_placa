import cv2
import numpy as np
from ultralytics import YOLO
from pyzbar import pyzbar
from database.database_handler import DatabaseHandler  # ajuste conforme seu projeto

def verificar_autorizacao(db, tipo, valor):
    return db.verificar_autorizado(tipo, valor)

def desenhar_status(frame, texto, pos, autorizado):
    cor = (0, 255, 0) if autorizado else (0, 0, 255)
    cv2.putText(frame, texto, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)

def main():
    db = DatabaseHandler()
    
    # Carrega os dois modelos
    modelo_placa = YOLO('treino/placa/placa.pt')         # Ex: detecta a placa completa
    modelo_caracteres = YOLO('treino/caracter/caracter.pt')  # Ex: detecta letras/números da placa

    cap = cv2.VideoCapture(0)  # Ajuste a fonte da câmera

    print("Pressione 'q' para sair.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        resultados_placa = modelo_placa(frame)

        placa_bbox = None
        img_with_boxes = frame.copy()

        # 1. DETECÇÃO DA PLACA
        for result in resultados_placa:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].cpu().numpy().astype(int)

                if cls == 0:  # Ajuste conforme a classe de placa
                    x1, y1, x2, y2 = xyxy
                    placa_bbox = (x1, y1, x2, y2)
                    cv2.rectangle(img_with_boxes, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    break  # Assume só uma placa por frame

        # 2. DETECÇÃO DOS CARACTERES DENTRO DA PLACA
        placa_montada = ''
        if placa_bbox:
            x1, y1, x2, y2 = placa_bbox
            placa_crop = frame[y1:y2, x1:x2]
            resultados_chars = modelo_caracteres(placa_crop)

            caracteres = []
            for result in resultados_chars:
                for box in result.boxes:
                    char_cls = int(box.cls[0])
                    xyxy_char = box.xyxy[0].cpu().numpy().astype(int)
                    x_c1, y_c1, x_c2, y_c2 = xyxy_char
                    centro_x = (x_c1 + x_c2) // 2
                    char_label = box.cls_name  # Requer que o modelo esteja treinado com nomes

                    caracteres.append({'bbox': (x_c1, y_c1, x_c2, y_c2), 'centro_x': centro_x, 'char': char_label})

            if caracteres:
                caracteres_ordenados = sorted(caracteres, key=lambda c: c['centro_x'])
                placa_montada = ''.join([c['char'] for c in caracteres_ordenados])

                autorizado = verificar_autorizacao(db, 'placa', placa_montada)
                desenhar_status(img_with_boxes,
                                f"{'AUTORIZADO' if autorizado else 'NÃO AUTORIZADO'}: {placa_montada}",
                                (10, 30), autorizado)

        # 3. DETECÇÃO DE QR CODES COM PYZBAR
        qr_codes = pyzbar.decode(frame)

        for qr in qr_codes:
            (x, y, w, h) = qr.rect
            cv2.rectangle(img_with_boxes, (x, y), (x + w, y + h), (255, 0, 0), 2)
            qr_data = qr.data.decode('utf-8')
            autorizado_qr = verificar_autorizacao(db, 'qrcode', qr_data)

            desenhar_status(img_with_boxes,
                            f"{'AUTORIZADO' if autorizado_qr else 'NÃO AUTORIZADO'} QR: {qr_data}",
                            (x, y - 10), autorizado_qr)

        # 4. EXIBIR
        cv2.imshow("YOLOv8 - Placas + Caracteres + QRCode", img_with_boxes)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
