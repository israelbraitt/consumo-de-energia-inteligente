# Sistema de controle e monitoramento de consumo para redes de energia elétrica
Sistema que automatiza a coleta de dados de energia elétrica das residências dos consumidores, a partir de um dispositivo medidor inteligente simulado em código. Esse dispositivo tem capacidade de enviar informações pela rede, possibilitando que os dados sejam agregados remotamente em uma nuvem da concessionária elétrica, ficando também disponível on-line. Esse dados são usados para fazer certos cálculos e consultas, provendo funcionalidades acerca da situação do seu consumo da residência dos clientes.

## 2. Solução do problema
Para desenvolver o sistema foi utilizada a linguagem de programação Python na versão 3.11, bem como funcionalidades incluídas nas bilbiotecas nativas da linguagem, como a utilização de sockets para comunicação em rede e recursos para codificação e decodificação de strings no formato JSON.

Para a comunicação do [medidor](https://github.com/israelbraitt/consumo-de-energia-inteligente/blob/main/medidor/medidor.py) com o [servidor](https://github.com/israelbraitt/consumo-de-energia-inteligente/blob/main/servidor/server.py) foi utilizado um padrão de comunicação utilizando strings, que será descrito mais adiante.

Para a comunicação do cliente (representado por um software que faz requisições para uma API, como [Insomnia](https://insomnia.rest/) ou [Postman](https://www.postman.com/)) com o servidor foi utilizado o padrão REST de comunicação, com o objetivo de construir uma API que utiliza-se o protocolo HTTP efetuar requisições.

A imagem abaixo representa o diagrama do sistema:

![Diagrama do sistema](https://github.com/israelbraitt/consumo-de-energia-inteligente/blob/main/resources/diagrama%20do%20sistema.png)

## 2.1 O que é API REST?
API REST é um conjunto de definições e protocolos usado no desenvolvimento e na integração de aplicações que está em conformidade com as restrições do estilo de arquitetura REST (Representational State Transfer).

REST não é um protocolo ou padrão, mas sim um conjunto de restrições de arquitetura.

Quando um cliente faz uma solicitação usando uma API RESTful, essa API transfere uma representação do estado do recurso ao solicitante. Essa informação é entregue via HTTP utilizando um dos vários formatos possíveis: Javascript Object Notation (JSON), HTML, texto sem formatação, entre outros.

Para a API ser considerada RESTful ela precisa seguir 6 constraints (restições):
1. Arquitetura client-server: deve aver uma seaparação entre o cliente da aplicação (usuários) e o servidor (armazenamento de dados);

2. Comunicação stateless: nenhuma referência ou informação sobre transações antigas são armazenadas, com isso, cada requisição (REQUEST) que o cliente faz ao servidor precisa conter todas as informações necessárias para o servidor entender e responder (RESPONSE), dessa forma, cada uma delas é feita do zero;

3. Cacheable: as respostas para cada requisição deve informar se podem ou não ser armazenadas em cache para otimizar as interações entre cliente e servidor;

4. Comunicação padronizada: é preciso existir uma interface uniforme entre os componentes para que as informações sejam transferidas em um formato padronizado;

5. Layered System: o sistema deve permitir o cliente deve poder acessar o endpoint sem precisar saber da complexidade ou dos passos necessários para que a requisição seja respondida;

6. Código sob demanda (opcional): a capacidade de enviar um código executável do servidor para o cliente quando solicitado para ampliar a funcionalidade disponível ao cliente.

## 2.2 Protocolos TCP e UDP
Nesse projeto foram utilizados 2 tipos de protocolos de comunicação:
- Protocolo TCP: protocolo orientado à conexão, que fornece uma comunicação confiável, com garantia de entrega dos dados enviados. Ele utiliza a técnica conehcida como **"three way handshake"**, também chamada de SYN, SYN-ACK, ACK.
A conexão entre dois hosts começa com o primeiro enviando ao segundo um pacote de sincronização (SYNchronize). O segundo host recebe esse pacote e responde com a confirmação do sincronização (SYNchronize-ACKnowledgment). O primeiro host, por fim, manda uma confirmação (ACKnowledge) para o segundo, assim estabelecendo a conexão. Isso permite a segurança no envio de dados.

- Protocolo UDP: protocolo não voltado à conexão, sendo que é necessário apenas um envio para que posso ocorrer a comunicação, tecnicamente ocorre apenas um **"handshake"**. Como não existe método para confirmação do estabelimento da conexão e nem do recebimento de dados, não temos certeza se o destinatário da mensagem conseguirá ouvi-la.

Comparando os dois protocolos, o UDP fornece uma comunicação mais rápida e menos custosa, pois não necessita de confirmação de recebimento, porém isso também o faz ter baixa confiabilidade para transmissão de dados; enquanto o TCP possibilita uma maior confibialidade na transmissão de dados, garantindo a integridade dos dados, porém faz com que a comunicação se torne mais lenta e inclusive mais custosa.

## 2.3 Threads
Os códigos do servidor e do medidor utilizam threads para receber as mensagens enviadas através da comunicação TCP e UDP respectivamente.

Um thread pode ser definido como uma linha de execução de um processo, que executa alguma atividade relacionada à uma aplicação principal. A utilização de threads para essa solução possibilita que várias tarefas sejam executadas concorrentemente, fazendo com que diversas atividades de ambas as partes do sistema sejam executadas quase que paralelamente (gerando ma noção de falso paralelismo).

No código do servidor, as threads ajudam a receber as mensagens da comunicação UDP e TCP sem gerar conflitos. Já no código do medidor elas ajudam a incrementar o cosumo e enviar o consumo atual via conexão UDP.


## 2.4 Servidor
O [server](https://github.com/israelbraitt/consumo-de-energia-inteligente/blob/main/servidor/server.py) é responsável por receber as requisições (requests) dos clientes, fazer o processamento devido das informações e enviar a resposta adequada para cada solicitação. Ele pode se conectar tanto com aplicações de usuários que fazem requisções HTTP (comunicação TCP), quanto com medidores que enviam informações através de strings (comunicação UDP).

As rotas possíveis para comunicação com as aplicações de usuários são:

- **/validacao-usuario**
    
    Usada para validar se o usuário está cadastrado na base de dados do sistema.

    É necessário indicar o **username** e a **matrícula** do usuário para conferir se o mesmo está validado no sistema.

- **/medicoes/ultima-medicao**

    Usada para requisitar ma última medição associada à uma matrícula.
    
    É necessário indicar o número de matrícula associado a um medidor para ser feita a busca pela última medição que foi salva na base de dados.

- **/gerar-fatura**
    
    Usada para calcular o valor da fatura do último período de consumo registrado.
    
    É necessário indicar o número de matrícula associado a um medidor para que seja calculada a diferença de consumo do último período registrado na base de dados, representado pela diferença entre a última e a penúltima medições registradas na base de dados.
    
    O valor do pagamento é calculado multiplicando-se o consumo do último período registrado pela taxa de consumo, que representa o custo por cada unidade de consumo.

- **/alerta-consumo**

    Usada para indicar se houve consumo excessivo no último período de medição registrado.
    
    É necessário indicar o número de matrícula associado a um medidor para que sejam buscadas as 5 últimas medições registradas na base de dados, então é calculado o consumo nos 4 últimos períodos registrados. Após isso é calculada a média aritmética entre o consumo dos 3 penúltimos períodos e caso o consumo do último período seja 1,5 vezes superior à média calculada, é indicado um aviso de consumo excessivo para a requisição do cliente.
    
    A imagem abaixo esquematiza a lógica desse cálculo:
   
   ![Cálculo do excesso de consumo](https://github.com/israelbraitt/consumo-de-energia-inteligente/blob/main/resources/c%C3%A1lculo%20de%20excesso%20de%20consumo.png)


O servidor é conectado a uma base de dados ([database](https://github.com/israelbraitt/consumo-de-energia-inteligente/tree/main/servidor/database)), onde as informações são armazenadas. Nessa representação, as informações ficam armazenadas em arquivos de texto (.txt) e outro para armazenar as medições.

O arquivo [**dados_clientes**](https://github.com/israelbraitt/consumo-de-energia-inteligente/blob/main/servidor/database/dados_clientes.txt) armazena os dados dos clientes, sendo a primeira informação da coluna o **username** e a segundo coluna o **número de matricula**.

O arquivo [**medicoes**](https://github.com/israelbraitt/consumo-de-energia-inteligente/blob/main/servidor/database/medicoes.txt) aramzena os dados das medições enviados pelos medidores, sendo a informaçãoda primeira coluna a **data e a hora** que o consumo foi registrado, a segunda coluna a **matrícula** relacionada ao medidor e a terceira coluna o **valor do consumo**.

Os arquivos da base de dados presentes nesse repositório já estão povoados com alguns dados que servem de exemplo.

## 2.5 Medidor
O [medidor](https://github.com/israelbraitt/consumo-de-energia-inteligente/blob/main/medidor/medidor.py) é responsável por simular o funcionamento de um medidor de energia elétrica, incrementando o consumo com valores aleatórios.


## 3. Melhorias futuras
O sistema é totalemente funcional, porém pode ser melhorado para se tornar mais eficiente. Entre as melhorias possíveis podem ser citadas:
- Adicionar variáveis de sessão para salvar informações dos usuários como *matrícula*;
- Modularizar ainda mais o código, de forma que seja criado um arquivo unicamente com a função de tratar as requests;
- Criar uma nova base de dados, conectando um banco de dados ao servidor, substituindo os arquivos de texto.
