from PyQt6.QtCore import QObject, pyqtSignal
import cv2
import numpy as np
from ultralytics import YOLO
from pyzbar import pyzbar
from database.database_handler import DatabaseHandler

class PlateReader(QObject):
    frame_ready = pyqtSignal(np.ndarray)  # sinal que envia frame processado para GUI

    def __init__(self, camera_index=1):
        super().__init__()
        self.db = DatabaseHandler()
        self.modelo_placa = YOLO('treino/placa/placa.pt')
        self.modelo_caracteres = YOLO('treino/caracter/caracter.pt')
        self.camera_index = camera_index
        self.cap = None
        self.running = False

    def verificar_autorizacao(self, tipo, valor):
        return self.db.verificar_autorizado(tipo, valor)

    def desenhar_status(self, frame, texto, pos, autorizado):
        cor = (0, 255, 0) if autorizado else (0, 0, 255)
        cv2.putText(frame, texto, pos, cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)

    def processar_frame(self, frame):
        resultados_placa = self.modelo_placa(frame)
        placa_bbox = None
        img_with_boxes = frame.copy()

        for result in resultados_placa:
            for box in result.boxes:
                cls = int(box.cls[0])
                xyxy = box.xyxy[0].cpu().numpy().astype(int)

                if cls == 0:
                    x1, y1, x2, y2 = xyxy
                    placa_bbox = (x1, y1, x2, y2)
                    cv2.rectangle(img_with_boxes, (x1, y1), (x2, y2), (0, 255, 255), 2)
                    break  # só uma placa por frame

        placa_montada = ''
        if placa_bbox:
            x1, y1, x2, y2 = placa_bbox
            placa_crop = frame[y1:y2, x1:x2]
            resultados_chars = self.modelo_caracteres(placa_crop)

            caracteres = []
            for result in resultados_chars:
                for box in result.boxes:
                    char_cls = int(box.cls[0])
                    char_label = self.modelo_caracteres.names[char_cls]
                    xyxy_char = box.xyxy[0].cpu().numpy().astype(int)
                    x_c1, y_c1, x_c2, y_c2 = xyxy_char
                    centro_x = (x_c1 + x_c2) // 2
                    caracteres.append({'bbox': (x_c1, y_c1, x_c2, y_c2), 'centro_x': centro_x, 'char': char_label})

            if caracteres:
                caracteres_ordenados = sorted(caracteres, key=lambda c: c['centro_x'])
                placa_montada = ''.join([c['char'] for c in caracteres_ordenados])
                autorizado = self.verificar_autorizacao('placa', placa_montada)
                self.desenhar_status(img_with_boxes,
                                     f"{'AUTORIZADO' if autorizado else 'NÃO AUTORIZADO'}: {placa_montada}",
                                     (10, 30), autorizado)

        # QR CODE
        qr_codes = pyzbar.decode(frame)
        for qr in qr_codes:
            (x, y, w, h) = qr.rect
            cv2.rectangle(img_with_boxes, (x, y), (x + w, y + h), (255, 0, 0), 2)
            qr_data = qr.data.decode('utf-8')
            autorizado_qr = self.verificar_autorizacao('qrcode', qr_data)
            self.desenhar_status(img_with_boxes,
                                 f"{'AUTORIZADO' if autorizado_qr else 'NÃO AUTORIZADO'} QR: {qr_data}",
                                 (x, y - 10), autorizado_qr)

        return img_with_boxes

    def start(self):
        self.cap = cv2.VideoCapture(self.camera_index)
        self.running = True

        while self.running:
            ret, frame = self.cap.read()
            if not ret:
                break

            frame_processado = self.processar_frame(frame)
            self.frame_ready.emit(frame_processado)
            cv2.waitKey(1)

        self.cap.release()

    def stop(self):
        self.running = False
