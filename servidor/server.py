import threading
import socket
import json
from DAO import DAO

class server:
    """
    Servidor de requisções do sistema de consumo inteligente

        Atributos:
            HOST (str): endereço de acesso do servidor
            TCP_PORT (int): porta de acesso do socket TCP
            UDP_PORT (int): porta de acesso do socket UDP
            BUFFER_SIZE (int): tamanho do buffer para recebimento de mensagens UDP
            TAXA_CONSUMO (int):  taxa de consumo de energia (usada para calcular o valor da fatura)
            clients (list): lista de clientes TCP conectados ao servidor
    """
    def __init__(self):
        self.HOST = '127.0.0.1'
        self.TCP_PORT = 50000
        self.UDP_PORT = 60000
        self.BUFFER_SIZE = 2048

        self.TAXA_CONSUMO = 3

        self.clients = []

    def main(self):
        """
        Executa os códigos do server
        """
        # Cria um socket com conexão TCP e outro com conexão UDP
        socket_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        socket_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        try:
            # Fornece o endereço e as portas para "escutar" as conexões
            # com os sockets dos clientes
            socket_tcp.bind((self.HOST, self.TCP_PORT))
            socket_tcp.listen()

            socket_udp.bind((self.HOST, self.UDP_PORT))
            print("Aguardando conexão de um cliente")
        except:
            return print("Não foi possível iniciar o servidor")

        thread1 = threading.Thread(target=self.conexaoTCP, args=[socket_tcp])
        thread2 = threading.Thread(target=self.conexaoUDP, args=[socket_udp])
        thread1.start()
        thread2.start()


    def conexaoTCP(self, socket_tcp):
        """
        Faz conexão com clientes TCP e executa uma thread para receber as mensagens

            Parâmetros:
                socket_tcp (socket): socket para conexão TCP
        """
        while True:
            # Aceita a conexão com os sockets dos clientes
            conn_client_tcp, addr_client_tcp = socket_tcp.accept()
            print("Conectado com um cliente TCP em: ", addr_client_tcp)
            self.clients.append(conn_client_tcp)
            
            # Recebe mensagens dos clientes através da conexão TCP
            thread_tcp = threading.Thread(target=self.tratarRequests, args=[conn_client_tcp])
            thread_tcp.start()

    def conexaoUDP(self, socket_udp):
        """
        Faz conexão com clientes UDP e executa uma thread para receber as mensagens

            Parâmetros:
                socket_tcp (socket): socket para conexão UDP
        """
        while True:
            # Recebe mensagens dos clientes através da conexão UDP
            mensagem_udp, HOST_client_udp = socket_udp.recvfrom(self.BUFFER_SIZE)
            print("Conectado com um cliente UDP em: ", HOST_client_udp)
            self.guardarMedicao(mensagem_udp)

    def tratarRequests(self, client):
        """
        Faz o tratamento dos "requests" dos clientes

            Parâmetros:
                client (socket): cliente conectado
            
            Retornos:

        """
        while True:
            try:
                mensagem = client.recv(self.BUFFER_SIZE)
                dados = self.obterDadosMensagem(mensagem.decode('utf-8'))
                print("Mensagem recebida:", mensagem)
                
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
                            request = self.montarResponse("200", "OK", json.dumps("Usuário cadastrado"))
                            self.enviarMensagem(client, request)

                        elif (validacao_client == False):
                            request = self.montarResponse("404", "Not Found", json.dumps("Usuário não cadastrado"))
                            self.enviarMensagem(client, request)
                            self.detelarClient(client)
                    
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
                            
                            request = self.montarResponse("200", "OK", json.dumps(dic_ultima_medicao))
                            self.enviarMensagem(client, request)
                        else:
                            request = self.montarResponse("404", "Not Found", json.dumps(""))
                            self.enviarMensagem(client, request)

                    elif (dados["url_content"] == "/gerar-fatura"):
                        matricula = dados["body_content"]["matricula"]

                        # Consulta as 2 últimas medições associadas a determinado número de matrícula
                        dao_inst = DAO()
                        ultimas_2_medicoes = dao_inst.get2UltimasMedicoes(matricula)
                        
                        if (ultimas_2_medicoes[0] != ('0', '0') and ultimas_2_medicoes[1] != ('0', '0')):
                            data, consumo_final= ultimas_2_medicoes[0]
                            data, consumo_inicial = ultimas_2_medicoes[1]
                            consumo_total = int(consumo_final) - int(consumo_inicial)
                            
                            # Multiplica o total de consumo do último período registrado
                            # pelo valor da taxa de consumo
                            valor_pagamento = consumo_total * self.TAXA_CONSUMO
                            
                            dic_fatura = { "consumo" : consumo_total , "valor_pagamento" : valor_pagamento}
                            
                            request = self.montarResponse("200", "OK", json.dumps(dic_fatura))
                            self.enviarMensagem(client, request)
                        else:
                            request = self.montarResponse("404", "Not Found", json.dumps(""))
                            self.enviarMensagem(client, request)

                    elif (dados["url_content"] == "/alerta-consumo"):
                        matricula = dados["body_content"]["matricula"]
                        
                        # Consulta as 5 últimas medições associadas a determinado número de matrícula
                        dao_inst = DAO()
                        ultimas_5_medicoes = dao_inst.get5UltimasMedicoes(matricula)
                        
                        if (ultimas_5_medicoes):
                            lista_variacao_consumo = []
                            
                            i = 4
                            while i > 0:
                                data, consumo_final = ultimas_5_medicoes[i-1]
                                data, consumo_inicial = ultimas_5_medicoes[i]
                                consumo_total = int(consumo_final) - int(consumo_inicial)
                                # Calcula e salva a variação de consumo dos último 4 períodos
                                lista_variacao_consumo.append(consumo_total)
                                i -= 1
                            
                            # Calcula a média de consumo dos últimos 3 períodos anteriores
                            media = (lista_variacao_consumo[0] + 
                                    lista_variacao_consumo[1] +
                                    lista_variacao_consumo[2])/3
                            
                            # Caso o consumo do último período seja maior que a média
                            # de consumo dos últimos 3 períodos vezes 1,5
                            if (lista_variacao_consumo[3] >= (media*1.5)):
                                # Calcula a diferença de consumo do último período em relação
                                # à média de consumo dos últimos 3 períodos anteriores
                                excesso_consumo = lista_variacao_consumo[3] - media
                                dic_exc_consumo = { "excesso_consumo" : excesso_consumo }

                                request = self.montarResponse("200", "OK", json.dumps(dic_exc_consumo))
                                self.enviarMensagem(client, request)
                            
                            # Caso não seja identificado consumo excessivo em relação à
                            # média dos períodos anteriores
                            else:
                                request = self.montarResponse("200", "OK", json.dumps("Sem consumo excessivo"))
                                self.enviarMensagem(client, request)
                        
                        else:
                            request = self.montarResponse("404", "Not Found", "")
                            self.enviarMensagem(client, request)

                elif (data["method"] == "PUT"):
                    pass

            except:
                self.detelarClient(client)
                break

    def guardarMedicao(self, dados_medidor):
        """
        Salva os dados das medições (recebidas pelos medidores) na base de dados

            Parâmetros:
                dados_medidor (bytes): dados codificados do medidor
        """
        dados_medidor = json.loads(dados_medidor.decode('utf-8'))
        
        matricula = dados_medidor["matricula"]
        consumo = dados_medidor["consumo_atual"]
        data_hora = dados_medidor["data_hora"]
        
        DAO.addMedicao(str(matricula), str(consumo), str(data_hora))

    def enviarMensagem(self, client, mensagem):
        """
        Envia mensagens para determinado cliente

            Parâmetros:
                mensagem (str): mensagem a ser enviada ("response")
                client (socket): cliente conectado
            
            Retornos:

        """
        try:
            client.send(mensagem.encode('utf-8'))
        except:
            self.detelarClient(client) 

    def broadcast(self, client, mensagem):
        """
        Envia mensagens para todos os clientes na lista de clientes, exceto
        para o que enviou a mensagem

            Parâmetros:
                mensagem (str): mensagem a ser enviada ("response")
                client (socket): cliente conectado
            
            Retornos:

        """
        for client_item in self.clients:
            if (client_item != client):
                try:
                    client_item.send(mensagem.encode('utf-8'))
                except:
                    self.detelarClient(client_item)

    def detelarClient(self, client):
        """
        Remove um cliente da lista de clientes

            Parâmetros:
                client (socket): cliente conectado
            
            Retornos:

        """
        self.clients.remove(client)

    def obterDadosMensagem(self, mensagem):
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

    def montarResponse(self, status_code, status_message, body):
        """
        Monta a "response" a ser enviada

            Parâmetros:
                status_code (str): código de status da resposta HTTP do servidor
                status_message (str): mensagem de status da resposta do servidor
                body (str): corpo da mensagem de retorno
            
            Retornos:
                response (str): resposta HTTP do servidor
        """
        http_version = "HTTP/1.1"
        HOST = "127.0.0.1:50000"
        user_agent = "server-conces-energia"
        content_type = "text/html"
        content_length = len(body)

        response = "{0} {1} {2}\nHOST: {3}\nUser-Agent: {4}\nContent-Type: {5}\nContent-Length: {6}\n\n{7}" .format(http_version, 
                                                                                                                    status_code, 
                                                                                                                    status_message, 
                                                                                                                    HOST, 
                                                                                                                    user_agent, 
                                                                                                                    content_type, 
                                                                                                                    content_length,
                                                                                                                    body)
        
        return response

server_inst = server()
server_inst.main()
