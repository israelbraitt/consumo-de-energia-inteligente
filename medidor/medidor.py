import threading
import socket
import json
from random import randint
from time import sleep
from datetime import datetime

class medidor:
    """
    Simula o funcionamento de um medidor de energia elétrica

        Atributos:
            matrícula (str): matrícula do medidor (relacionada à um usuário)
            consumo (int): valor do consumo registrado pelo medidor
            bloqueado (bool): estado atual do medidor (se está ativo ou bloqueado)
    """
    def __init__(self):
        # Gera um número aleatório de 8 dígitos para a matrícula
        self.matricula = randint(9999999, 99999999)
        self.consumo = 0
        self.bloqueado = False

        self.HOST = '127.0.0.1'
        self.PORT = 60000
        self.INTERVALO_INCREM = 1
        self.INTERVALO_ENVIO = 15

        # Cria um socket com conexão UDP
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    def getMatricula(self):
        """
        Retorna a matrícula do medidor

            Retornos:
                Matrícula do medidor
        """
        return self.matricula
    
    def setMatricula(self, nova_matricula):
        """
        Altera a matrícula do medidor

            Parâmetros:
                nova_matricula (str): nova matrícula do medidor
        """
        self.matricula = nova_matricula
    
    def getConsumo(self):
        """
        Retorna o consumo atual registrado pelo medidor

            Retornos:
                Consumo atual registrado pelo medidor
        """
        return self.consumo
    
    def incrementarConsumo(self):
        """
        Incrementa o consumo do medidor através de um número aleatório

        """
        while True:
            self.consumo += randint(0, 20)
            sleep(self.INTERVALO_INCREM)
            print("Consumo: ", self.consumo)
    
    def getBloqueio(self):
        """
        Retorna o estado de "bloqueio" do medidor

            Retornos:
                False (bool): indica que o medidor está bloqueado
                True (bool): indica que o medidor está ativo
        """
        return self.bloqueado
    
    def setBloqueio(self):
        """
        Altera o estado de "bloqueio" do medidor

        """
        if (self.bloqueado == False):
            self.bloqueado == True
            self.taxa_consumo = 1
        elif (self.bloqueado == True):
            self.bloqueado == False
            self.taxa_consumo = 0

    def enviarMedicoes(self, client):
        """
        Envia dados do valor atual do consumo do medidor via conexão UDP
        
            Parâmetros:
                client (socket): socket para conexão UDP
        """
        while True:
            sleep(self.INTERVALO_ENVIO)
            
            data_hora_atuais = datetime.now()
            data_hora = data_hora_atuais.strftime('%d-%m-%Y %H:%M:%S')
            
            dic_medicao = { "matricula" : self.matricula, 
                            "consumo_atual" : self.consumo, 
                            "data_hora" : data_hora }
            dic_medicao_bytes = json.dumps(dic_medicao).encode('utf-8')
            
            client.sendto(dic_medicao_bytes, (self.HOST, self.PORT))
            print("Mensagem enviada: ", dic_medicao)
    
    def main(self):
        """
        Executa os códigos do medidor
        """
        
        print("Medidor com a matrícula {0} iniciado" .format(self.matricula))
       
        # Envia mensagens através da conexão UDP
        thread1 = threading.Thread(target=self.enviarMedicoes, args=[self.client])
        thread1.start()

        # Incrementa o consumo do medidor
        thread2 = threading.Thread(target=self.incrementarConsumo())
        thread2.start()

medidor_inst = medidor()
medidor_inst.main()