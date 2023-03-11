import threading
import socket
import json
from dao import DAO

HOST = '127.0.0.1'
TCP_PORT = 50000
UDP_PORT = 60000
BUFFER_SIZE = 2048

clients = []

# Taxa de consumo de energia
CONSUMPTION_RATE = 3

def main():
    # Cria um socket com conexão TCP e outro com conexão UDP
    server_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    try:
        # Fornece o endereço e as portas para "escutar" as conexões
        # com os sockets dos clientes
        server_tcp.bind(('', TCP_PORT))
        server_tcp.listen()

        server_udp.bind(('', UDP_PORT))
        print("Aguardando conexão de um cliente")
    except:
        return print("Não foi possível iniciar o servidor")

    while True:
        # Aceita a conexão com os sockets dos clientes
        # conn_client é do tipo 'socket.socket' e addr_client é do tipo 'tupla'
        conn_client_tcp, addr_client_tcp = server_tcp.accept()
        print("Conectado em", addr_client_tcp)
        clients.append(conn_client_tcp)
        
        # Recebe mensagens dos clientes através da conexão TCP
        thread_tcp = threading.Thread(target=messagesTreatment, args=[conn_client_tcp])
        thread_tcp.start()

        # Recebe mensagens dos clientes através da conexão UDP
        message_udp, addr_client_udp = server_udp.recvfrom(BUFFER_SIZE)
        print("Conectado em", addr_client_udp)

def messagesTreatment(client):
    """
    Faz o tratamento dos "requests" dos clientes

        Parâmetros:
            client (socket.socket): cliente conectado
        
        Retornos:

    """
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
                    
                    # Consulta se o cliente está registrado na base de dados
                    dao_inst = DAO()
                    validation_client = dao_inst.getClient(username, registration_number)

                    if (validation_client == True):
                        request = assembleResponse("200", "OK")
                        sendMessages(client, request)

                    elif (validation_client == False):
                        request = assembleResponse("404", "Not Found")
                        sendMessages(request, client)
                        deleteClient(client)
                
                elif (data["url_content"] == "/medicoes/ultima-medicao"):
                    registration_number = data["body_content"]["registration"]

                    # Consulta a última medição associada a determinado número de matrícula
                    dao_inst = DAO()
                    last_measurement = dao_inst.getLastMeasurement(registration_number)

                    if (last_measurement != (0, 0)):
                        # Retorna a data, a hora e o consumo registrado na última medição
                        date_time = last_measurement[0]
                        consumption = last_measurement[1]
                        dic_last_measurement = { "date_time" : date_time, "consumption" : consumption}
                        
                        request = assembleResponse("200", json.dumps(dic_last_measurement))
                        sendMessages(client, request)
                    else:
                        request = assembleResponse("404", "Not Found")
                        sendMessages(client, request)

                elif (data["url_content"] == "/gerar-fatura"):
                    registration_number = data["body_content"]["registration"]

                    # Consulta as 2 últimas medições associadas a determinado número de matrícula
                    dao_inst = DAO()
                    last_2_measurements = dao_inst.get2LastMeasurements(registration_number)
                    print(last_2_measurements)
                    if (last_2_measurements[0] != ('0', '0') and last_2_measurements[1] != ('0', '0')):
                        date, final_consumption = last_2_measurements[0]
                        date, inicial_consumption = last_2_measurements[1]
                        total_consumption = int(final_consumption) - int(inicial_consumption)
                        
                        # Multiplica o total de consumo do último período registrado
                        # pelo valor da taxa de consumo
                        amount_payment = total_consumption * CONSUMPTION_RATE
                        
                        dic_invoice = { "consumption" : total_consumption , "amount_payment" : amount_payment}
                        
                        request = assembleResponse("202", json.dumps(dic_invoice))
                        sendMessages(client, request)
                    else:
                        request = assembleResponse("404", "Not Found")
                        sendMessages(client, request)

                elif (data["url_content"] == "/alerta-consumo"):
                    registration_number = data["body_content"]["registration"]
                    
                    # Consulta as 5 últimas medições associadas a determinado número de matrícula
                    dao_inst = DAO()
                    last_5_measurements = dao_inst.get5LastMeasurements(registration_number)

                    if (last_5_measurements[0] != (0, 0) and last_5_measurements[1] != (0, 0)):
                        variation_consumption_list = []
                        i = 4
                        while i > 0:
                            date, final_consumption = last_5_measurements[i-1]
                            date, inicial_consumption = last_5_measurements[i]
                            total_consumption = int(final_consumption) - int(inicial_consumption)
                            # Calcula e salva a variação de consumo dos último 4 meses
                            variation_consumption_list.append(total_consumption)
                            i -= 1
                        
                        # Calcula a média de consumo dos últimos 3 meses anteriores
                        media = (variation_consumption_list[0] + 
                                variation_consumption_list[1] +
                                variation_consumption_list[2])/3
                        
                        if (variation_consumption_list[3] >= media*(1,5)):
                            # Calcula a diferença de consumo do último mês em relação
                            # à média de consumo dos últimos 3 meses anteriores
                            overconsumption = variation_consumption_list[3] - media
                            dic_invoice = { "overconsumption" : overconsumption }

                            request = assembleResponse("200", json.dumps(dic_invoice))
                            sendMessages(client, request)
                        else:
                            request = assembleResponse("200", "Sem consumo excessivo")
                            print(request)
                            sendMessages(client, request)
                    else:
                        request = assembleResponse("404", "Not Found")
                        sendMessages(client, request)

            elif (data["method"] == "POST"):
                pass

            elif (data["method"] == "PUT"):
                pass

        except:
            deleteClient(client)
            break

def sendMessages(client, message):
    """
    Envia mensagens para determinado cliente

        Parâmetros:
            message (str): mensagem a ser enviada ("response")
            client (socket.socket): cliente conectado
        
        Retornos:

    """
    try:
        client.send(message.encode('utf-8'))
    except:
        deleteClient(client) 

def broadcast(client, message):
    """
    Envia mensagens para todos os clientes na lista de clientes, exceto
    para o que enviou a mensagem

        Parâmetros:
            message (str): mensagem a ser enviada ("response")
            client (socket.socket): cliente conectado
        
        Retornos:

    """
    for client_item in clients:
        if (client_item != client):
            try:
                client_item.send(message.encode('utf-8'))
            except:
                deleteClient(client_item)

def deleteClient(client):
    """
    Remove um cliente da lista de clientes

        Parâmetros:
            client (socket.socket): cliente conectado
        
        Retornos:

    """
    clients.remove(client)

def getMessageData(message):
    """
    Obtém os dados de uma "request"

        Parâmetros:
            message (str): mensagem recebida ("request")
        
        Retornos:
            um dicionário com o "method", o "url_content" e o "body_content" da "request"
    """
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
    """
    Monta a "response" a ser enviada

        Parâmetros:
            status_code (str): código de status da resposta HTTP do servidor
            status_message (str): mensagem de status da resposta do servidor
        
        Retornos:
            response (str): resposta HTTP do servidor
    """
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
