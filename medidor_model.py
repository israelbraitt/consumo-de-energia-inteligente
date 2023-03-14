class medidor_model:
    """
    Classe que representa simula o funcionamento de um medidor de energia elétrica

        Atributos:
            matrícula (str): matrícula do medidor (relacionada à um usuário)
            consumo (int): valor do consumo registrado pelo medidor
            taxa_consumo (int): taxa de consumo, usada para incrementar o consumo
            bloqueado (bool): estado atual do medidor (se está ativo ou bloqueado)
    """
    def __init__(self, matricula):
        self.matricula = matricula
        self.consumo = 0
        self.taxa_consumo = 1
        self.bloqueado = False
    
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
        Incrementa o consumo do medidor

        """
        self.consumo += self.taxa_consumo
    
    def getTaxaConsumo(self):
        """
        Retorna a taxa de consumo atual do medidor
        Essa taxa é utilizada para incrementar o consumo

            Retornos:
                Valor da taxa de consumo atual do medidor
        """
        return self.taxa_consumo
    
    def setTaxaConsumo(self, nova_taxa_consumo):
        """
        Altera a taxa de consumo do medidor

            Parâmetros:
                nova_taxa_consumo (str): nova taxa de consumo do medidor
        """
        self.taxa_consumo = nova_taxa_consumo
    
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
    

