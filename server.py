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
TAXA_CONSUMO = 3

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
        print("Conectado com um cliente em:", addr_client_tcp)
        clients.append(conn_client_tcp)
        
        # Recebe mensagens dos clientes através da conexão TCP
        thread_tcp = threading.Thread(target=tratadorRequests, args=[conn_client_tcp])
        thread_tcp.start()

        # Recebe mensagens dos clientes através da conexão UDP
        mensagem_udp, addr_client_udp = server_udp.recvfrom(BUFFER_SIZE)
        print("Conectado em", addr_client_udp)

def tratadorRequests(client):
    """
    Faz o tratamento dos "requests" dos clientes

        Parâmetros:
            client (socket.socket): cliente conectado
        
        Retornos:

    """
    while True:
        try:
            mensagem = client.recv(BUFFER_SIZE)
            dados = obterDadosMensagem(mensagem.decode('utf-8'))
            print("Mensagem recebida:", mensagem)
            print("data", dados)
            
            if (dados["method"] == "GET"):
                pass

            elif (dados["method"] == "POST"):
                if (dados["url_content"] == "/validacao-usuario"):
                    username = dados["body_content"]["username"]
                    matricula = dados["body_content"]["matricula"]
                    
                    # Consulta se o cliente está registrado na base de dados
                    dao_inst = DAO()
                    validacao_client = dao_inst.getClient(username, matricula)

                    if (validacao_client == True):
                        request = montarResponse("200", "OK")
                        enviarMensagem(client, request)

                    elif (validacao_client == False):
                        request = montarResponse("404", "Not Found")
                        enviarMensagem(client, request)
                        detelarClient(client)
                
                elif (dados["url_content"] == "/medicoes/ultima-medicao"):
                    matricula = dados["body_content"]["matricula"]

                    # Consulta a última medição associada a determinado número de matrícula
                    dao_inst = DAO()
                    ultima_medicao = dao_inst.getUltimaMedicao(matricula)

                    if (ultima_medicao != (0, 0)):
                        # Retorna a data, a hora e o consumo registrado na última medição
                        data_hora = ultima_medicao[0]
                        consumo = ultima_medicao[1]
                        dic_ultima_medicao = { "data_hora" : data_hora, "consumo" : consumo}
                        
                        request = montarResponse("200", json.dumps(dic_ultima_medicao))
                        enviarMensagem(client, request)
                    else:
                        request = montarResponse("404", "Not Found")
                        enviarMensagem(client, request)

                elif (dados["url_content"] == "/gerar-fatura"):
                    matricula = dados["body_content"]["matricula"]

                    # Consulta as 2 últimas medições associadas a determinado número de matrícula
                    dao_inst = DAO()
                    ultimas_2_medicoes = dao_inst.get2UltimasMedicoes(matricula)
                    print(ultimas_2_medicoes)
                    if (ultimas_2_medicoes[0] != ('0', '0') and ultimas_2_medicoes[1] != ('0', '0')):
                        data, consumo_final= ultimas_2_medicoes[0]
                        data, consumo_inicial = ultimas_2_medicoes[1]
                        consumo_total = int(consumo_final) - int(consumo_inicial)
                        
                        # Multiplica o total de consumo do último período registrado
                        # pelo valor da taxa de consumo
                        valor_pagamento = consumo_total * TAXA_CONSUMO
                        
                        dic_fatura = { "consumo" : consumo_total , "valor_pagamento" : valor_pagamento}
                        
                        request = montarResponse("202", json.dumps(dic_fatura))
                        enviarMensagem(client, request)
                    else:
                        request = montarResponse("404", "Not Found")
                        enviarMensagem(client, request)

                elif (dados["url_content"] == "/alerta-consumo"):
                    matricula = dados["body_content"]["matricula"]
                    
                    # Consulta as 5 últimas medições associadas a determinado número de matrícula
                    dao_inst = DAO()
                    ultimas_5_medicoes = dao_inst.get5UltimasMedicoes(matricula)

                    if (ultimas_5_medicoes[0] != (0, 0) and ultimas_5_medicoes[1] != (0, 0)):
                        lista_variacao_consumo = []
                        i = 4
                        while i > 0:
                            data, consumo_final = ultimas_5_medicoes[i-1]
                            data, consumo_inicial = ultimas_5_medicoes[i]
                            consumo_total = int(consumo_final) - int(consumo_inicial)
                            # Calcula e salva a variação de consumo dos último 4 meses
                            lista_variacao_consumo.append(consumo_total)
                            i -= 1
                        
                        # Calcula a média de consumo dos últimos 3 meses anteriores
                        media = (lista_variacao_consumo[0] + 
                                lista_variacao_consumo[1] +
                                lista_variacao_consumo[2])/3
                        
                        if (lista_variacao_consumo[3] >= media*(1,5)):
                            # Calcula a diferença de consumo do último mês em relação
                            # à média de consumo dos últimos 3 meses anteriores
                            excesso_consumo = lista_variacao_consumo[3] - media
                            dic_exc_consumo = { "excesso_consumo" : excesso_consumo }

                            request = montarResponse("200", json.dumps(dic_exc_consumo))
                            enviarMensagem(client, request)
                        else:
                            request = montarResponse("200", "Sem consumo excessivo")
                            print(request)
                            enviarMensagem(client, request)
                    else:
                        request = montarResponse("404", "Not Found")
                        enviarMensagem(client, request)

            elif (data["method"] == "PUT"):
                pass

        except:
            detelarClient(client)
            break

def enviarMensagem(client, mensagem):
    """
    Envia mensagens para determinado cliente

        Parâmetros:
            mensagem (str): mensagem a ser enviada ("response")
            client (socket.socket): cliente conectado
        
        Retornos:

    """
    try:
        client.send(mensagem.encode('utf-8'))
    except:
        detelarClient(client) 

def broadcast(client, mensagem):
    """
    Envia mensagens para todos os clientes na lista de clientes, exceto
    para o que enviou a mensagem

        Parâmetros:
            mensagem (str): mensagem a ser enviada ("response")
            client (socket.socket): cliente conectado
        
        Retornos:

    """
    for client_item in clients:
        if (client_item != client):
            try:
                client_item.send(mensagem.encode('utf-8'))
            except:
                detelarClient(client_item)

def detelarClient(client):
    """
    Remove um cliente da lista de clientes

        Parâmetros:
            client (socket.socket): cliente conectado
        
        Retornos:

    """
    clients.remove(client)

def obterDadosMensagem(mensagem):
    """
    Obtém os dados de uma "request"

        Parâmetros:
            mensagem (str): mensagem recebida de um cliente ("request")
        
        Retornos:
            um dicionário com o "method", o "url_content" e o "body_content" da "request"
    """
    method = mensagem.split(" ")[0]
    url_content = mensagem.split(" ")[1]

    try:    
        # Prepara as mensagens no padrão JSON
        mensagem = mensagem.replace("{","{dir") 
        mensagem = mensagem.replace("}","esq}")
        mensagem = mensagem.split("{")[1].split("}")[0]
        mensagem = mensagem.replace("dir","{")
        mensagem = mensagem.replace("esq","}")

        body_content = json.loads(mensagem)

    except:
        body_content = "{}"

    return {
        "method": method,
        "url_content": url_content,
        "body_content": body_content
    }

def montarResponse(status_code, status_mensagem):
    """
    Monta a "response" a ser enviada

        Parâmetros:
            status_code (str): código de status da resposta HTTP do servidor
            status_mensagem (str): mensagem de status da resposta do servidor
        
        Retornos:
            response (str): resposta HTTP do servidor
    """
    http_version = "HTTP/1.1"
    host = "127.0.0.1:50000"
    user_agent = "server-conces-energia"
    content_type = "text/html"
    content_length = len(status_mensagem)

    response = "{0} {1} {2}\r\nHost: {3}\r\nUser-Agent: {4}\r\nContent-Type: {5}\r\nContent-Length: {6}" .format(http_version, 
                                                                                                                status_code, 
                                                                                                                status_mensagem, 
                                                                                                                host, 
                                                                                                                user_agent, 
                                                                                                                content_type, 
                                                                                                                content_length)
    
    return response

main()
