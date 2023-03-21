import socket
import json
from DAO import DAO

class API:
    
    def __init__(self, taxa_consumo):
        self.TAXA_CONSUMO = taxa_consumo

    def getTaxaConsumo(self):
        return self.TAXA_CONSUMO
    
    def setTaxaConsumo(self, nova_taxa_consumo):
        self.TAXA_CONSUMO = nova_taxa_consumo

    def tratarRequests(self, mensagem):
        """
        Faz o tratamento dos "requests" dos clientes

            Parâmetros:
                client (socket.socket): cliente conectado
            
            Retornos:

        """
        try:
            dados = self.obterDadosMensagem(mensagem.decode('utf-8'))
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
                        request = self.montarResponse("200", "OK", json.dumps("Usuário cadastrado"))
                        return request

                    elif (validacao_client == False):
                        request = self.montarResponse("404", "Not Found", json.dumps("Usuário não cadastrado"))
                        return request
                
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
                        return request
                    else:
                        request = self.montarResponse("404", "Not Found", json.dumps(""))
                        return request

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
                        valor_pagamento = consumo_total * self.TAXA_CONSUMO
                        
                        dic_fatura = { "consumo" : consumo_total , "valor_pagamento" : valor_pagamento}
                        
                        request = self.montarResponse("200", "OK", json.dumps(dic_fatura))
                        return request
                    else:
                        request = self.montarResponse("404", "Not Found", json.dumps(""))
                        return request

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
                            return request
                        
                        # Caso não seja identificado consumo excessivo em relação à
                        # média dos períodos anteriores
                        else:
                            request = self.montarResponse("200", "OK", json.dumps("Sem consumo excessivo"))
                            return request
                    
                    else:
                        request = self.montarResponse("404", "Not Found", "")
                        return request

            elif (data["method"] == "PUT"):
                pass

        except:
            pass

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