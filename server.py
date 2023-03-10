import threading
import socket
import json
from dao import DAO

HOST = '127.0.0.1'
TCP_PORT = 50000
UDP_PORT = 60000
BUFFER_SIZE = 2048

clients = []

# taxa de consumo de energia
CONSUMPTION_RATE = 3

def main():
    # os parâmetros do método socket indicam a família de protocolo (IPV4)
    # e o tipo do protocolo (TCP)
    server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # vinculado os sockets dos clientes ao endereço do servidor
        server_tcp.bind(('', TCP_PORT))
        server_tcp.listen()

        server_udp.bind(('', UDP_PORT))
        print("Aguardando conexão de um cliente")
    except:
        return print("Não foi possível iniciar o servidor")

    while True:
        # aceita a conexão com os sockets dos clientes
        # conn_client é do tipo 'socket.socket' e addr_client é do tipo 'tupla'
        conn_client_tcp, addr_client_tcp = server_tcp.accept()
        print("Conectado em", addr_client_tcp)
        clients.append(conn_client_tcp)

        conn_client_udp, addr_client_udp = server_udp.accept()
        print("Conectado em", addr_client_udp)
        clients.append(conn_client_udp)

        thread1 = threading.Thread(target=messagesTreatment, args=[conn_client_tcp])
        thread2 = threading.Thread(target=messagesTreatment, args=[conn_client_udp])
        
        thread1.start()
        thread2.start()

def messagesTreatment(client):
    while True:
        try:
            message = client.recv(BUFFER_SIZE)
            data = getMessageData(message.decode('utf-8'))
            print("Mensagem recebida:", message)
            print("data", data)
            

            if (data["method"] == "GET"):
                if (data["url_content"] == "/validacao-usuario"):
                    username = data["body_content"]["username"]
                    registration_number = data["body_content"]["registration"]
                    
                    dao_inst = DAO()
                    validation_client = dao_inst.getClient(username, registration_number)

                    if (validation_client == True):
                        request = assembleResponse(200, "OK")
                        sendMessages(request, client)

                    elif (validation_client == False):
                        request = assembleResponse(404, "Not Found")
                        sendMessages(request, client)
                        deleteClient(client)
                
                elif (data["url_content"] == "/medicoes/ultima-medicao"):
                    registration_number = data["body_content"]["registration"]

                    dao_inst = DAO()
                    last_measurement = dao_inst.getLastMeasurement(registration_number)

                    if (last_measurement != (0, 0)):
                        date_time = last_measurement[0]
                        consumption = last_measurement[1]
                        dic_last_measurement = { "date_time" : date_time, "consumption" : consumption}
                        
                        request = assembleResponse(200, json.dumps(dic_last_measurement))
                        sendMessages(request, client)
                    else:
                        request = assembleResponse(404, "Not Found")
                        sendMessages(request, client)

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

                        request = assembleResponse(202, json.dumps(dic_invoice))
                        sendMessages(request, client)
                    else:
                        request = assembleResponse(404, "Not Found")
                        sendMessages(request, client)

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

                        request = assembleResponse(200, json.dumps(dic_invoice))
                        sendMessages(request, client)
                    else:
                        request = assembleResponse(404, "Not Found")
                        sendMessages(request, client)

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

    return {
        "method": method,
        "url_content": url_content,
        "body_content": body_content
    }

def assembleResponse(status_code, status_message):
    http_version = "HTTP/1.1"
    host = "127.0.0.1:50000"
    user_agent = "server-conces-energia"
    content_type = "text/html"
    content_length = len(status_message)

    response = "{0} {1} {2}\r\nHost: {3}\r\nUser-Agent: {4}\r\nContent-Type: {5}\r\nContent-Length: {6}" .format(http_version, 
                                                                                                                status_code, 
                                                                                                                status_message, 
                                                                                                                host, 
                                                                                                                user_agent, 
                                                                                                                content_type, 
                                                                                                                content_length)
    
    return response

main()
