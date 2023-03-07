import threading
import socket
import json
from dao import *

HOST = '127.0.0.1'
PORT = 50000
BUFFER_SIZE = 2048

clients = []

# taxa de consumo de energia
CONSUMPTION_RATE = 3

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
            data = getMessageData(str(message.decode('utf-8')))
            print("Mensagem recebida:", message)

            if (data["method"] == "GET"):
                if (data["url_content"] == "/validacao-usuario"):
                    username = data["body_content"]["username"]
                    registration_number = data["body_content"]["registration"]
                    
                    dao_inst = DAO()
                    validation_client = dao_inst.getClient(username, registration_number)

                    if (validation_client == True):
                        request = f'HTTP/1.1 200 OK'
                    elif (validation_client == False):
                        deleteClient(client)
                        request = f'HTTP/1.1 404 Not Found'
                
                elif (data["url_content"] == "/medicoes/ultima-medicao"):
                    registration_number = data["body_content"]["registration"]

                    dao_inst = DAO()
                    last_measurement = dao_inst.getLastMeasurement(registration_number)

                    if (last_measurement != (0, 0)):
                        date_time = last_measurement[0]
                        consumption = last_measurement[1]
                        dic_last_measurement = { "date_time" : date_time, "consumption" : consumption}
                        request = f'HTTP/1.1 200 {json.dumps(dic_last_measurement)}'
                    else:
                        request = f'HTTP/1.1 404 Not Found'

                elif (data["url_content"] == "/gerar-fatura"):
                    registration_number = data["body_content"]["registration"]

                    dao_inst = DAO()
                    last_measurements = dao_inst.get5LastMeasurements(registration_number)

                    
                    if (last_measurements[0] != (0, 0) and last_measurements[1] != (0, 0)):
                        consumption_final = last_measurements[0][1]
                        consumption_inicial = last_measurements[1][1]
                        consumption_total = consumption_final - consumption_inicial

                        amount_payment = consumption_total * CONSUMPTION_RATE
                        
                        dic_invoice = { "consumption" : consumption_total , "amount_payment" : amount_payment}
                        request = f'HTTP/1.1 200 {json.dumps(dic_invoice)}'
                    else:
                        request = f'HTTP/1.1 404 Not Found'

                elif (data["url_content"] == "/alerta-consumo"):
                    registration_number = data["body_content"]["registration"]

                    dao_inst = DAO()
                    last_measurements = dao_inst.get5LastMeasurements(registration_number)

                    
                    if (last_measurements[0] != (0, 0) and last_measurements[1] != (0, 0)):
                        variation_consumption_list = []
                        i = 4
                        while i > 0:
                            consumption_final = last_measurements[i][1]
                            consumption_inicial = last_measurements[i-1][1]
                            consumption_total = consumption_final - consumption_inicial
                            variation_consumption_list.append(consumption_total)
                            i -= 1
                        
                        dic_invoice = { "consumption" : consumption_total }
                        request = f'HTTP/1.1 200 {json.dumps(dic_invoice)}'
                    else:
                        request = f'HTTP/1.1 404 Not Found'

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


def getMessageData(message):
    method = message.split(" ")[0]
    url_content = message.split(" ")[1]
    http_version = message.split(" ")[2]
    body_content = ""

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

    return { "method" : method, "url_content" : url_content, "http_version" : http_version, "body_content" : body_content }


main()
