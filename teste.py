import qrcode

# Gera QR Code com texto "123123"
img = qrcode.make("123456")

# Salva no arquivo
img.save("teste_123456.png")

print("QR Code '123456' criado no arquivo teste_123456.png")
