class DAO:
    """
    Data Acess Object para acessar e manipular a base de dados
    """
    def __init__(self):
        pass

    @staticmethod
    def getClient(username, matricula):
        """
        Confere se o cliente está cadastrado ou não na base de dados

            Parâmetros:
                username (str): nome de usuário
                matricula (str): número de matrícula do usuário
            
            Retornos:
                True (bool): caso os dados do cliente estejam cadastrados
                False (bool): caso os dados do cliente não estejam cadastrados
        """
        if (username != ""):
            file = open("database/dados_clientes.txt")
            lines = file.readlines()
            for line in lines:
                username_line = line.split(";")[0]
                if (username_line == username):
                    file.close()
                    return True
            file.close()
            return False
        
        elif (matricula != ""):
            file = open("database/dados_clientes.txt")
            lines = file.readlines()
            for line in lines:
                matricula_line = line.split(";")[1]
                if (matricula_line == matricula):
                    file.close()
                    return True
            file.close()
            return False
        
        elif (username == "" and matricula == ""):
            return False

    @staticmethod        
    def getUltimaMedicao(matricula):
        """
        Retorna os dados da última medição associada a determinada matrícula

            Parâmetros:
                matricula (str): número de matrícula do usuário
            
            Retornos:
                (data_hora, consumo) (tuple): data, hora e consumo registrados na última medição
                (0, 0) (tuple): caso não tenha nenhuma medição associada ao número de matrícula
        """
        if (matricula != ""):
            file = open("database/medicoes.txt")
            lines = file.readlines()
            for line in lines:
                matricula_line = line.split(";")[1]
                if (matricula_line == matricula):
                    data_hora = line.split(";")[0]
                    consumo = line.split(";")[2]
                    consumo = consumo.split("\n")[0]
                    return (data_hora, consumo)
            file.close()
            return (0, 0)

    @staticmethod    
    def get2UltimasMedicoes(matricula):
        """
        Retorna os dados das 2 últimas medições associadas a determinada matrícula

            Parâmetros:
                matricula (str): número de matrícula do usuário
            
            Retornos:
               lista_medicoes (list[tuple]): lista contendo as 2 últimas medições
        """
        lista_medicoes = []
        list_itens = 0
        if (matricula != ""):
            file = open("database/medicoes.txt")
            lines = file.readlines()
            for line in lines:
                matricula_line = line.split(";")[1]
                if (matricula_line == matricula):
                    data_hora = line.split(";")[0]
                    consumo = line.split(";")[2]
                    consumo = consumo.split("\n")[0]
                    lista_medicoes.append((data_hora, consumo))
                    
                    list_itens += 1
                    if (list_itens == 2):
                        break;
        file.close()
        return lista_medicoes

    @staticmethod    
    def get5UltimasMedicoes(matricula):
        """
        Retorna os dados das 5 últimas medições associadas a determinada matrícula

            Parâmetros:
                matricula (str): número de matrícula do usuário
            
            Retornos:
               lista_medicoes (list[tuple]): lista contendo as 5 últimas medições
        """
        lista_medicoes = []
        list_itens = 0
        if (matricula != ""):
            file = open("database/medicoes.txt")
            lines = file.readlines()
            for line in lines:
                matricula_line = line.split(";")[1]
                if (matricula_line == matricula):
                    data_hora = line.split(";")[0]
                    consumo = line.split(";")[2]
                    consumo = consumo.split("\n")[0]
                    lista_medicoes.append((data_hora, consumo))

                    list_itens += 1
                    if (list_itens == 5):
                        break;
        file.close()
        return lista_medicoes
    
    @staticmethod
    def addMedicao(matricula, consumo, data_hora):
        """
        Adiciona uma medição de consumo (recebida por um medidor) na base de dados

            Parâmetros:
                matricula (str): número de matrícula do usuário
                consumo (str): consumo registrado pelo medidor
                data_hora (str): data e hora do registro do consumo
        """
        file = open("database/medicoes.txt", 'r')
        lines = file.readlines()
        file.close()

        medicao = str(data_hora + ";" + matricula + ";" + consumo + "\n")
        lines.insert(0, medicao)

        file = open("database/medicoes.txt", 'w')
        file.writelines(lines)
        file.close()
