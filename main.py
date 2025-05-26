from database.database_handler import DatabaseHandler
from utils.qrcode_generator import gerar_qrcode

def menu():
    print("\nControle de Acesso - Menu")
    print("1. Cadastrar Placa")
    print("2. Cadastrar QR Code")
    print("3. Verificar Placa")
    print("4. Verificar QR Code")
    print("5. Sair")

def main():
    db = DatabaseHandler()

    while True:
        menu()
        opcao = input("Escolha uma opção: ")

        if opcao == '1':
            nome = input("Digite o nome da pessoa: ")
            valor = input("Digite a placa (ex: ABC12345): ").upper()
            db.add_autorizados('placa', valor, nome)

        elif opcao == '2':
            nome = input("Digite o nome da pessoa: ")
            valor = input("Digite o conteúdo do QR Code: ")
            db.add_autorizados('qrcode', valor, nome)
            gerar_qrcode(valor, f"{valor}_qrcode.png")

        elif opcao == '3':
            valor = input("Digite a placa para verificação: ").upper()
            resultado = db.verificar_autorizado('placa', valor)
            if resultado:
                print(f"Autorizado! Proprietário: {resultado[0]}")
            else:
                print("Placa NÃO autorizada!")

        elif opcao == '4':
            valor = input("Digite o QR Code para verificação: ")
            resultado = db.verificar_autorizado('qrcode', valor)
            if resultado:
                print(f"QR Code AUTORIZADO! Proprietário: {resultado[0]}")
            else:
                print("QR Code NÃO autorizado!")

        elif opcao == '5':
            print("Saindo...")
            break

        else:
            print("Opção inválida. Tente novamente.")

if __name__ == '__main__':
    main()
