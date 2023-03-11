class DAO:

    def __init__(self):
        pass

    @staticmethod
    def getClient(username, registration_number):
        """
        Confere se o cliente está cadastrado ou não na base de dados

            Parâmetros:
                username (str): nome de usuário
                registration_number (str): número de matrícula do usuário
            
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
        
        elif (registration_number != ""):
            file = open("database/dados_clientes.txt")
            lines = file.readlines()
            for line in lines:
                registration_line = line.split(";")[1]
                if (registration_line == registration_number):
                    file.close()
                    return True
            file.close()
            return False
        
        elif (username == "" and registration_number == ""):
            return False

    @staticmethod        
    def getLastMeasurement(registration_number):
        """
        Retorna os dados da última medição associada a determinada matrícula

            Parâmetros:
                registration_number (str): número de matrícula do usuário
            
            Retornos:
                (date_time, consumption) (tuple): data, hora e consumo registrados na última medição
                (0, 0) (tuple): caso não tenha nenhuma medição associada ao número de matrícula
        """
        if (registration_number != ""):
            file = open("database/medicoes.txt")
            lines = file.readlines()
            for line in lines:
                registration_line = line.split(";")[1]
                if (registration_line == registration_number):
                    date_time = line.split(";")[0]
                    consumption = line.split(";")[2]
                    consumption = consumption.split("\n")[0]
                    return (date_time, consumption)
            file.close()
            return (0, 0)

    @staticmethod    
    def get2LastMeasurements(registration_number):
        """
        Retorna os dados das 2 últimas medições associadas a determinada matrícula

            Parâmetros:
                registration_number (str): número de matrícula do usuário
            
            Retornos:
               measurement_list (list[tuple]): lista contendo as 2 últimas medições
        """
        measurement_list = []
        list_itens = 0
        if (registration_number != ""):
            file = open("database/medicoes.txt")
            lines = file.readlines()
            for line in lines:
                registration_line = line.split(";")[1]
                if (registration_line == registration_number):
                    date_time = line.split(";")[0]
                    consumption = line.split(";")[2]
                    consumption = consumption.split("\n")[0]
                    measurement_list.append((date_time, consumption))
                    
                    list_itens += 1
                    if (list_itens == 2):
                        break;
        file.close()
        return measurement_list

    @staticmethod    
    def get5LastMeasurements(registration_number):
        """
        Retorna os dados das 5 últimas medições associadas a determinada matrícula

            Parâmetros:
                registration_number (str): número de matrícula do usuário
            
            Retornos:
               measurement_list (list[tuple]): lista contendo as 5 últimas medições
        """
        measurement_list = []
        list_itens = 0
        if (registration_number != ""):
            file = open("database/medicoes.txt")
            lines = file.readlines()
            for line in lines:
                registration_line = line.split(";")[1]
                if (registration_line == registration_number):
                    date_time = line.split(";")[0]
                    consumption = line.split(";")[2]
                    consumption = consumption.split("\n")[0]
                    measurement_list.append((date_time, consumption))

                    list_itens += 1
                    if (list_itens == 5):
                        break;
        file.close()
        return measurement_list
    