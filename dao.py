class DAO:

    def __init__(self):
        pass

    
    def getClient(username, registration_number):
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
        
    def getLastMeasurement(registration_number):
        if (registration_number != ""):
            file = open("database/medicoes.txt")
            lines = file.readlines()
            for line in lines:
                registration_line = line.split(";")[1]
                if (registration_line == registration_number):
                    date_time = line.split(";")[0]
                    consumption = line.split(";")[2]
                    return (date_time, consumption)
            file.close()
            return (0, 0)
    
    def get5LastMeasurements(registration_number):
        measurement_list = []
        list_itens = 0
        while list_itens < 6:
            if (registration_number != ""):
                file = open("database/medicoes.txt")
                lines = file.readlines()
                for line in lines:
                    registration_line = line.split(";")[1]
                    if (registration_line == registration_number):
                        date_time = line.split(";")[0]
                        consumption = line.split(";")[2]
                        measurement_list.append((date_time, consumption))
                file.close()
                return measurement_list
    