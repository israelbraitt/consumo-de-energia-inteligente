import threading
import socket
import json

HOST = '127.0.0.1'
PORT = 50000
BUFFER_SIZE = 2048
username = ''
matricula = ''

def main():
    # Cria um socket com conexão TCP
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        client.bind((HOST, PORT))
        print("Conectado")
    except:
        return print("Não foi possível se conectar ao servidor")
    
    #validarUsuario(client)
    username = "amancio123"
    maricula = "13456789"
    selectionMenu(client)

    # Recebe mensagens através da conexão TCP
    thread1 = threading.Thread(target=receivemensagems, args=[client])
    # Envia mensagens através da conexão TCP
    thread2 = threading.Thread(target=enviarMensagem, args=[client, username])

    thread1.start()
    thread2.start()


def receivemensagems(client):
    """
    Recebe mensagens

        Parâmetros:
            client (socket.socket): cliente conectado
        
        Retornos:

    """
    while True:
        try:
            mensagem = client.recv(BUFFER_SIZE).decode('utf-8')
            print("Mensagem recebida: " + mensagem + "/n")
            tratadorResponses()
        except:
            print("Não foi possível permanecer conectado ao servidor")
            print("Pressione <Enter> para continuar...")
            client.close()
            break


def enviarMensagem(client, mensagem):
    """
    Envia mensagens

        Parâmetros:
            client (socket.socket): cliente conectado
            mensagem (str): mensagem a ser enviada
        
        Retornos:

    """
    while True:
        try:
            client.send(mensagem.encode('utf-8'))
            
        except:
            return


def validarUsuario(client):
    """
    Valida se o usuário está cadastrado na base de dados

        Parâmetros:
            client (socket.socket): cliente conectado
        
        Retornos:

    """
    try:
        print("Digite seu nome de usuário")
        username = input("Usuário: ")
        print("Digite seu número de matrícula")
        matricula = input("Matrícula: ")

        dic_user = { "username" : username, "matricula" : matricula }

        request = f'GET /validacao-usuario HTTP/1.1 {json.dumps(dic_user)}'
        enviarMensagem(client, request)
    except:
        print("Usuário não encontrado")


def selectionMenu(client):
    """
    Menu de seleção das opções de requisição

        Parâmetros:
            client (socket.socket): cliente conectado
        
        Retornos:

    """
    while True:
        request = ""
        print("==========Menu==========")
        print("1 - Requisitar última medição")
        print("2 - Solicitar fatura")
        print("3 - Ver alertas de consumo")
        print("4 - Sair")
        escolha = input()

        dic_user = { "username" : username, "matricula" : matricula }

        if (escolha == "1"):
            request = f'POST /medicoes/ultima-medicao HTTP/1.1 {json.dumps(dic_user)}'
            print("enviando sua mensagi, zé mané")
        elif (escolha == 2):
            request = f'POST /gerar-fatura HTTP/1.1 {json.dumps(dic_user)}'
        elif (escolha == 3):
            request = f'POST /alerta-consumo HTTP/1.1 {json.dumps(dic_user)}'
        elif (escolha == 4):
            client.close()
            return
        else:
            print("Digite uma opção válida")
    
        enviarMensagem(client, request)


def tratadorResponses(mensagem):
    """
    Trata as mensagens recebidas

        Parâmetros:
            mensagem (str): mensagem a ser enviada
        
        Retornos:

    """
    while True:
        try:
           dados = obterDadosMensagem(str(mensagem.decode('utf-8')))

           if (dados["status_code"] == "200"):
                   print(dados["status_mensagem"])
           elif (dados["status_code"] == ""):
               pass
            
        except:
            break


def obterDadosMensagem(mensagem):
    """
    Obtém os dados de uma "response" do servidor

        Parâmetros:
            mensagem (str): mensagem recebida do servidor ("response")
        
        Retornos:
            um dicionário com o "status_code" e a "status_menssage" da "response"
    """
    status_code = mensagem.split(" ")[1]
    status_mensagem = mensagem.split(" ")[2]
    status_mensagem = status_mensagem.split("\r\n")[0]

    return { "status_code" : status_code, "status_mensagem" : status_mensagem }


main()
