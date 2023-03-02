import threading
import socket
import json
from time import sleep

HOST = '127.0.0.1'
PORT = 50000
BUFFER_SIZE = 2048
username = ''
registration = ''

def main():
    # os parâmetros do método socket indicam a família de protocolo (IPV4)
    # e o tipo do protocolo (TCP)
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.connect((HOST, PORT))
        print("Conectado")
    except:
        return print("Não foi possível se conectar ao servidor")
    
    userValidation(client)

    thread1 = threading.Thread(target=receiveMessages, args=[client])
    thread2 = threading.Thread(target=sendMessages, args=[client, username])

    thread1.start()
    thread2.start()


def receiveMessages(client):
    while True:
        try:
            message = client.recv(BUFFER_SIZE).decode('utf-8')
            print("Mensagem recebida: " + message + "/n")
            messagesTreatment()
        except:
            print("Não foi possível permanecer conectado ao servidor")
            print("Pressione <Enter> para continuar...")
            client.close()
            break


def sendMessages(client, message):
    while True:
        try:
            client.send(f'{message}'.encode('utf-8'))
            print("Mensagem enviada")
        except:
            return


def userValidation(client):
    try:
        print("Digite seu nome de usuário")
        username = input("Usuário: ")
        print("Digite seu número de matrícula")
        registration = input("Matrícula: ")

        dic_user = { "username" : username , "registration" : registration }

        request = f'GET /validacao-usuario HTTP/1.1 {json.dumps(dic_user)}'
        sendMessages(client, request)
    except:
        print("Usuário não encontrado")


def selectionMenu(client):
    while True:
        try:
            print("==========Menu==========")
            print("1 - Requisitar última medição")
            print("2 - Solicitar fatura")
            print("3 - Ver alertas de consumo")
            print("4 - Sair")
            choice = input()

            dic_user = { "username" : username }

            if (choice == 1):
                request = f'GET /medicoes/ultima-medicao HTTP/1.1 {json.dumps(dic_user)}'
            elif (choice == 2):
                request = f'GET /gerar-fatura HTTP/1.1 {json.dumps(dic_user)}'
            elif (choice == 3):
                request = f'GET /alerta-consumo HTTP/1.1 {json.dumps(dic_user)}'
            elif (choice == 4):
                client.close()
                return
            else:
                print("Digite uma opção válida")
                pass
        
            client.send(f'{request}'.encode('utf-8'))


        except:
            pass


def messagesTreatment(message):
    while True:
        try:
           data = messageData(str(message.decode('utf-8')))

           if (data["status_code"] == "200"):
                   print(data["status_message"])
           elif (data["status_code"] == ""):
               pass
            
        except:
            break


def messageData(message):
    http_version = message.split(" ")[0]
    status_code = message.split(" ")[1]
    status_message = ""

    try:    
        # Prepara as mensagens no padrão JSON
        message = message.replace("{","{dir") 
        message = message.replace("}","esq}")
        message = message.split("{")[1].split("}")[0]
        message = message.replace("dir","{")
        message = message.replace("esq","}")

        body_content = json.loads(message)

    except:
        body_content = "{}"

    return { "http_version" : http_version , "status_code" : status_code, "status_message" : status_message }


main()