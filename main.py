from database.database_handler import DatabaseHandler

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
        opcao = input("Escula uma opção: ")

        if opcao == '1':
            valor = input("Digite a placa (ex: ABC12345): ").upper()
            db.add_autorizados('placa', valor)

        elif opcao == '2':
            valor = input("Digite o QR Code: ")
            db.add_autorizados('qrcode', valor)

        elif opcao == '3':
            valor = input("Digite a placa para verificação: ").upper()
            if db.verificar_autorizado('placa', valor):
                print("Autorizado!")
            else:
                print("Placa NÃO autorizada!")

        elif opcao == '4':
            valor = input("Digite o QR Code para verificação: ")
            if db.verificar_autorizado('qrcode', valor):
                print("QR Code AUTORIZADO!")
            else:
                print("QR Code NÃO autorizado!")

        elif opcao == '5':
            print("Saindo...")
            break

        else:
            print("Opção inválida. Tente novamente.")

if __name__ == '__main__':
    main()
