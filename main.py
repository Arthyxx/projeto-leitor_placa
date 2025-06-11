import sys
import cv2
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QMessageBox
)
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import QThread
from leitor.plate_reader import PlateReader
from database.database_handler import DatabaseHandler
from utils.qrcode_generator import gerar_qrcode  # <-- IMPORTAÇÃO DO QR CODE

class PlateReaderWorker(QThread):
    def __init__(self, plate_reader):
        super().__init__()
        self.plate_reader = plate_reader

    def run(self):
        self.plate_reader.start()

    def stop(self):
        self.plate_reader.stop()
        self.quit()
        self.wait()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Controle de Acesso - PyQt")
        self.db = DatabaseHandler()

        # Instancia PlateReader e thread
        self.plate_reader = PlateReader()
        self.thread = PlateReaderWorker(self.plate_reader)

        self.init_ui()

        # Conectar sinal para receber frames da thread
        self.plate_reader.frame_ready.connect(self.update_video_frame)

        # Iniciar thread
        self.thread.start()

    def init_ui(self):
        layout = QVBoxLayout()

        # Label para vídeo
        self.video_label = QLabel("Carregando vídeo...")
        self.video_label.setFixedSize(640, 480)
        layout.addWidget(self.video_label)

        # ---- Placa ----
        self.placa_input = QLineEdit()
        self.placa_input.setPlaceholderText("Digite a placa (ex: ABC1234)")

        btn_cadastrar = QPushButton("Cadastrar Placa")
        btn_cadastrar.clicked.connect(self.cadastrar_placa)

        btn_verificar = QPushButton("Verificar Placa")
        btn_verificar.clicked.connect(self.verificar_placa)

        hlayout = QHBoxLayout()
        hlayout.addWidget(self.placa_input)
        hlayout.addWidget(btn_cadastrar)
        hlayout.addWidget(btn_verificar)
        layout.addLayout(hlayout)

        # ---- QR Code ----
        self.qr_input = QLineEdit()
        self.qr_input.setPlaceholderText("Digite o conteúdo do QR Code")

        btn_cadastrar_qr = QPushButton("Cadastrar QR")
        btn_cadastrar_qr.clicked.connect(self.cadastrar_qrcode)

        btn_verificar_qr = QPushButton("Verificar QR")
        btn_verificar_qr.clicked.connect(self.verificar_qrcode)

        btn_gerar_qr = QPushButton("Gerar QR Code")
        btn_gerar_qr.clicked.connect(self.gerar_qrcode_manual)

        qr_layout = QHBoxLayout()
        qr_layout.addWidget(self.qr_input)
        qr_layout.addWidget(btn_cadastrar_qr)
        qr_layout.addWidget(btn_verificar_qr)
        qr_layout.addWidget(btn_gerar_qr)
        layout.addLayout(qr_layout)

        self.setLayout(layout)

    def update_video_frame(self, frame):
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        pix = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pix)

    def cadastrar_placa(self):
        placa = self.placa_input.text().upper().strip()
        if placa:
            nome = "Nome Exemplo"
            self.db.add_autorizados('placa', placa, nome)
            QMessageBox.information(self, "Sucesso", f"Placa {placa} cadastrada para {nome}")
            self.placa_input.clear()
        else:
            QMessageBox.warning(self, "Erro", "Digite uma placa válida.")

    def verificar_placa(self):
        placa = self.placa_input.text().upper().strip()
        if placa:
            resultado = self.db.verificar_autorizado('placa', placa)
            if resultado:
                QMessageBox.information(self, "Autorizado", f"Placa autorizada! Proprietário: {resultado[0]}")
            else:
                QMessageBox.warning(self, "Não autorizado", "Placa NÃO autorizada!")
        else:
            QMessageBox.warning(self, "Erro", "Digite uma placa válida.")

    def cadastrar_qrcode(self):
        conteudo = self.qr_input.text().strip()
        if conteudo:
            nome = "Nome QR"
            self.db.add_autorizados('qrcode', conteudo, nome)
            gerar_qrcode(conteudo)  # <-- Gerar QR Code automaticamente
            QMessageBox.information(self, "Sucesso", f"QR Code '{conteudo}' cadastrado e gerado para {nome}")
            self.qr_input.clear()
        else:
            QMessageBox.warning(self, "Erro", "Digite o conteúdo do QR Code.")


    def verificar_qrcode(self):
        conteudo = self.qr_input.text().strip()
        if conteudo:
            resultado = self.db.verificar_autorizado('qrcode', conteudo)
            if resultado:
                QMessageBox.information(self, "Autorizado", f"QR Code autorizado! Proprietário: {resultado[0]}")
            else:
                QMessageBox.warning(self, "Não autorizado", "QR Code NÃO autorizado!")
        else:
            QMessageBox.warning(self, "Erro", "Digite o conteúdo do QR Code.")

    def gerar_qrcode_manual(self):
        texto = self.qr_input.text().strip()
        if texto:
            gerar_qrcode(texto)
            QMessageBox.information(self, "Sucesso", f"QR Code gerado com o conteúdo: {texto}")
        else:
            QMessageBox.warning(self, "Erro", "Digite um conteúdo válido para gerar o QR Code.")

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

def main():
    app = QApplication(sys.argv)
    janela = MainWindow()
    janela.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
