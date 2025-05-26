import qrcode
import os

def gerar_qrcode(texto, nome_arquivo = None, pasta='qrcodes'):
    if not os.path.exists(pasta):
        os.makedirs(pasta)

    if nome_arquivo is None:
        nome_arquivo = texto

    caminho = os.path.join(pasta, f"{nome_arquivo}.png")

    img = qrcode.make(texto)
    img.save(caminho)

    print(f"QR Code gerado e salvo em: {caminho}")
    