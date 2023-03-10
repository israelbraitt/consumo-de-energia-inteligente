import threading
import socket
import json
from time import sleep

HOST = '127.0.0.1'
PORT = 60000
BUFFER_SIZE = 2048
SENDING_INTERVAL = 15
username = ''
registration = ''

def main():
    # os parâmetros do método socket indicam a família de protocolo (IPV4)
    # e o tipo do protocolo (TCP)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        client.connect((HOST, PORT))
        print("Conectado")
    except:
        return print("Não foi possível se conectar ao servidor")
    
    userValidation(client)

    thread1 = threading.Thread(target=sendMessages, args=[client, username])

    thread1.start()


def sendMessages(client, message):
    while True:
        try:
            client.send('123'.encode('utf-8'))
            print("Mensagem enviada")
        except:
            return
        sleep(SENDING_INTERVAL)


def userValidation(client):
    try:
        print("Digite seu nome de usuário")
        username = input("Usuário: ")
        print("Digite seu número de matrícula")
        registration = input("Matrícula: ")

        dic_user = { "username" : username, "registration" : registration }

        request = f'GET /validacao-usuario HTTP/1.1 {json.dumps(dic_user)}'
        sendMessages(client, request)
    except:
        print("Usuário não encontrado")


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
