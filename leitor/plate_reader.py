import cv2
import easyocr
import re
import threading
import time
from database.database_handler import DatabaseHandler

def filtrar_placa(texto):
    padrao = r'[A-Z]{3}[0-9][A-Z0-9][0-9]{2}'
    match = re.search(padrao, texto.replace(' ', '').upper())
    return match.group(0) if match else None

class VideoStream:
    def __init__(self, src=1):
        self.cap = cv2.VideoCapture(src)
        self.ret, self.frame = self.cap.read()
        self.stopped = False
        self.lock = threading.Lock()

    def start(self):
        threading.Thread(target=self.update, daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            ret, frame = self.cap.read()
            if not ret:
                self.stop()
                break
            with self.lock:
                self.ret = ret
                self.frame = frame

    def read(self):
        with self.lock:
            if self.frame is None:
                return False, None
            return self.ret, self.frame.copy()



    def stop(self):
        self.stopped = True
        self.cap.release()

def ocr_thread_func(vs, db, reader, lock, resultados_ocr, frame_skip=5):
    frame_count = 0
    while not vs.stopped:
        ret, frame = vs.read()
        if not ret:
            time.sleep(0.1)
            continue

        frame_count += 1
        if frame_count % frame_skip != 0:
            time.sleep(0.01)
            continue
        
        frame_resized = cv2.resize(frame, (640, 480))
        frame_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)

        ocr_results = reader.readtext(frame_rgb)

        placas_detectadas = []

        for _, texto, conf_ocr in ocr_results:
            placa = filtrar_placa(texto)
            if placa and conf_ocr > 0.5:
                autorizado = db.verificar_autorizado('placa', placa)
                placas_detectadas.append((placa, autorizado))

        with lock:
            resultados_ocr.clear()
            resultados_ocr.extend(placas_detectadas)

        time.sleep(0.1)

def ler_placa():
    db = DatabaseHandler()
    reader = easyocr.Reader(['pt'], gpu=False)

    vs = VideoStream(src=1).start()
    lock = threading.Lock()
    resultados_ocr = []

    print("Abrindo a câmera... Pressione 'q' para sair.")

    t_ocr = threading.Thread(target=ocr_thread_func, args=(vs, db, reader, lock, resultados_ocr), daemon=True)
    t_ocr.start()

    while True:
        ret, frame = vs.read()
        if not ret or frame is None:
            print("Erro ao capturar o vídeo")
            break

        with lock:
            y0 = 30
            for i, (placa, autorizado) in enumerate(resultados_ocr):
                cor = (0, 255, 0) if autorizado else (0, 0, 255)
                status = "AUTORIZADO" if autorizado else "NÃO AUTORIZADO"
                text = f"{status}: {placa}"
                cv2.putText(frame, text, (10, y0 + i*30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, cor, 2)

        cv2.imshow("Leitor de Placa", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vs.stop()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    ler_placa()
