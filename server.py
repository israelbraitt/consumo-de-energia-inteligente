import threading
import socket
import json
from dao import *

HOST = 'localhost'
PORT = 50000
BUFFER_SIZE = 2048

clients = []

def main():
    # os parâmetros do método socket indicam a família de protocolo (IPV4)
    # e o tipo do protocolo (TCP)
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server.bind(('', PORT))
        server.listen()
        print("Aguardando conexão de um cliente")
    except:
        return print("Não foi possível iniciar o servidor")

    while True:
        # conn_client é do tipo 'socket.socket' e addr_client é do tipo 'tupla'
        conn_client, addr_client = server.accept()
        print("Conectado em", addr_client)
        clients.append(conn_client)

        thread = threading.Thread(target=messagesTreatment, args=[conn_client])
        thread.start()         


def messagesTreatment(client):
    while True:
        try:
            message = client.recv(BUFFER_SIZE)
            data = messageData(str(message.decode('utf-8')))
            print("Mensagem recebida:", message)

            if (data["method"] == "GET"):
                if (data["url_content"] == "/validacao-usuario"):
                    username = data["body_content"]["username"]
                    registration_number = data["body_content"]["registration"]
                    
                    dao_inst = DAO()
                    validation_client = dao_inst.getClient(username, registration_number)

                    if (validation_client == True):
                        pass
                        # enviar mensagem com status code 200
                    elif (validation_client == False):
                        pass
                        deleteClient(client)
                        # enviar mensagem com status code
                
                elif (data["url_content"] == "/medicoes/ultima-medicao"):
                    pass
                elif (data["url_content"] == "/gerar-fatura"):
                    pass
                elif (data["url_content"] == "/alerta-consumo"):
                    pass

            elif (data["method"] == "POST"):
                pass

            elif (data["method"] == "PUT"):
                pass

        except:
            deleteClient(client)
            break


def sendMessages(msg, client):
    try:
        client.send(msg.encode('utf-8'))
    except:
        deleteClient(client) 


def broadcast(msg, client):
    for client_item in clients:
        if (client_item != client):
            try:
                client_item.send(msg)
            except:
                deleteClient(client_item)


def deleteClient(client):
    clients.remove(client)


def messageData(message):
    method = message.split(" ")[0]
    url_content = message.split(" ")[1]
    body_content = ""

    try:    
        # Prepara as mensagens
        message = message.replace("{","{dir") 
        message = message.replace("}","esq}")
        message = message.split("{")[1].split("}")[0]
        message = message.replace("dir","{")
        message = message.replace("esq","}")

        body_content = json.loads(message)

    except:
        body_content = "{}"

    return { "method" : method, "url_content" : url_content, "body_content" : body_content }


main()