import threading
import socket
import json
from time import sleep
from datetime import datetime
import medidor_model

HOST = '127.0.0.1'
PORT = 60000
BUFFER_SIZE = 2048
SENDING_INTERVAL = 15
username = ''
matricula = ''

def main():
    # Cria um socket com conexão UDP
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    
    matricula = input("Digite a matrícula do medidor")
    medidor_inst = medidor_model(matricula)

    try:
        client.connect((HOST, PORT))
        print("Conectado")
    except:
        return print("Não foi possível se conectar ao servidor")
    
    validarUsuario(client)
    
    while True:

        # Envia mensagens através da conexão UDP
        thread1 = threading.Thread(target=enviarMensagem, args=[client, username])

        thread1.start()


def enviarMensagem(client, mensagem):
    """
    Envia mensagens

        Parâmetros:
            client (socket.socket): cliente conectado
            mensagem (str): mensagem a ser enviada
        
        Retornos:

    """
    try:
        client.sendto(bytes(mensagem, "utf-8"), (HOST, PORT))
        print("Mensagem enviada")
    except:
        return
    sleep(SENDING_INTERVAL)


def validarUsuario(client):
    try:
        dic_user = { "username" : username, "matricula" : matricula }

        request = f'POST /validacao-usuario HTTP/1.1 {json.dumps(dic_user)}'
        enviarMensagem(client, request)
    except:
        print("Usuário não encontrado")


def enviarMedicoes(consumo_atual):
    data_hora_atuais = datetime.now()
    data_hora = data_hora_atuais.strftime('%d/%m/%Y %H:%M:%S')

    return { "consumo_atual" : consumo_atual , "data_hora" : data_hora }


main()
