# Projeto ETL Pipeline na AWS para Criação de Conjunto de Dados
Veja o vídeo do teste na cloud aqui : [Teste na cloud AWS](https://www.youtube.com/watch?v=U8mbIapwUy4)

## Visão Geral

Este projeto consiste em desenvolver uma pipeline ETL na AWS para preparar um conjunto de dados destinado à modelagem de machine learning. A pipeline foi desenvolvida utilizando serviços da AWS, incluindo Glue, S3, CloudWatch, IAM e Redshift.

## Desenvolvimento da Solução

### 1. Entendimento do Problema - [Notebook](https://github.com/cinthialet/etl-aws-pipeline/blob/main/transformacao_dados_aws.ipynb)

**Objetivo:** A pedido de um Cientista de Dados, o objetivo é desenvolver um conjunto de dados que inclua determinadas informações para o modelo de machine learning que será construído.

> A pipeline deve ser feita em cloud AWS,com execução manual e o destino dos dados é o Redshift

### 2. Entendimento dos Dados - [Notebook](https://github.com/cinthialet/etl-aws-pipeline/blob/main/transformacao_dados_aws.ipynb)
[**Dados Originais**](https://github.com/cinthialet/etl-aws-pipeline/blob/main/WA_Fn-UseC_-Telco-Customer-Churn.csv)

Análise exploratória dos dados para compreender as características, distribuições e possíveis desafios associados ao conjunto de dados.

### 3. Decomposição do Problema - [Notebook](https://github.com/cinthialet/etl-aws-pipeline/blob/main/transformacao_dados_aws.ipynb)

Identificar e dividir as tarefas em demandas menores para simplificar a implementação (Demandas 1-4)

### 4. Realização das Transformações - [Notebook](https://github.com/cinthialet/etl-aws-pipeline/blob/main/transformacao_dados_aws.ipynb)

Aplicar as transformações necessárias nos dados para obter a estrutura desejada.

### 5. Script para o Job do Glue - [Notebook](https://github.com/cinthialet/etl-aws-pipeline/blob/main/transformacao_dados_aws.ipynb)

Desenvolvimento do script Python para o job do AWS Glue, que será responsável pelo processo ETL.

### 6. Criação dos Recursos na AWS - [AWS](https://github.com/cinthialet/etl-aws-pipeline/blob/main/arquitetura%20aws.png)

Configuração dos recursos na AWS necessários para a execução da pipeline.

### 7. Teste da Solução - [Vídeo do teste](https://www.youtube.com/watch?v=U8mbIapwUy4)

Testes end-to-end para garantir que a pipeline está funcionando corretamente e os dados são transformados e armazenados conforme esperado no Amazon Redshift.
Este vídeo é a parte 3 de uma playlist explicando o desenvolvimento do projeto. Abaixo, as outras partes :
- [PARTE 1](https://www.youtube.com/watch?v=a1faKmcerBw)
- [PARTE 2](https://www.youtube.com/watch?v=8C3lr3TETu8)

# Arquitetura AWS para ETL Pipeline

Esta arquitetura é projetada para extrair, transformar e carregar dados usando os serviços AWS, incluindo Amazon S3, AWS Glue, Amazon Redshift e Amazon CloudWatch.

![Arquitetura AWS ETL Pipeline](https://github.com/cinthialet/etl-aws-pipeline/blob/main/arquitetura%20aws.png?raw=true)

## Descrição da Arquitetura:

1. **Amazon S3 (1)**: Utilizado como armazenamento de origem para os dados brutos.
2. **IAM (2)**: Fornece permissões para que o AWS Glue possa acessar os recursos necessários.
3. **Amazon Redshift (3)**: Banco de dados de armazenamento final para os dados transformados.
4. **Amazon CloudWatch (4)**: Monitora e registra os logs do job do AWS Glue.
5. **AWS Glue (5)**: Realiza a extração, transformação e carregamento (ETL) dos dados.

## Implementação

### **Passo 1: Configuração do Amazon S3**
1. No console AWS, navegue até o Amazon S3.
2. Crie um novo bucket chamado `fonte-pipeline-etl`.
3. Faça upload do arquivo `WA_Fn-UseC_-Telco-Customer-Churn.csv` no bucket criado.

### **Passo 2: Configuração da IAM Role**
1. Acesse o IAM (Identity and Access Management) no console AWS.
2. Crie uma nova função chamada `permissao-pipeline-etl` destinada ao AWS Glue.
3. Adicione as seguintes políticas à função:
    - AmazonS3ReadOnlyAccess
    - CloudWatchLogsFullAccess
    - AmazonRedshiftFullAccess

### **Passo 3: Configuração do Amazon Redshift**
1. No console AWS, vá para o Amazon Redshift.
2. Crie um novo cluster chamado `redshift-pipeline` do tipo `dc2.large free tier`.
3. Configure o banco de dados chamado `dev` com o usuário `admin`. Defina uma senha e guarde-a com segurança.
4. No EC2, configure o grupo de segurança para permitir que o AWS Glue se conecte ao Redshift.

### **Passo 4: Amazon CloudWatch**
O CloudWatch criará automaticamente grupos de logs para o job do AWS Glue. Haverá um grupo para logs de erro (`/aws-glue/python-jobs/error`) e outro para logs de output (`/aws-glue/python-jobs/output`).

### **Passo 5: Configuração do AWS Glue ETL Job**
1. No console AWS, vá para o AWS Glue e crie um novo ETL job chamado `etl-pipeline-to-redshift`.
2. Use o Script Editor para inserir o script ETL desenvolvido localmente.
3. Selecione o IAM Role `permissao-pipeline-etl`.
4. Configure o job para Python, carregue as bibliotecas de análise comuns, defina DPU como 1/16 e timeout como 5 minutos.
5. Em propriedades avançadas:
    - Defina o nome do script como `transformacao-pipeline-etl.py`.
    - Adicione os parâmetros do job para conexão com o Redshift, para que os dados sensíveis não estejam no código:
![Parametros Glue Job](https://github.com/cinthialet/etl-aws-pipeline/blob/main/img/glue-parameters.png)

6. Execute o job manualmente. O output esperado é: logs publicados no CloudWatch, criação da tabela `dados_finais` no Redshift e inserção dos dados na tabela.
![Output Logs](https://github.com/cinthialet/etl-aws-pipeline/blob/main/img/cloudwatch-result.png)
![Tabela Redshift](https://github.com/cinthialet/etl-aws-pipeline/blob/main/img/redshift-result.png) 
 
## Bibliotecas Utilizadas

- **boto3**: SDK da Amazon para Python que manipula recursos da AWS.
  
- **BytesIO (da biblioteca io)**: Interface para sequências de bytes que facilita manipulação de arquivos do S3 como arquivos em memória.

- **psycopg2**: Biblioteca para conexão com PostgreSQL que permite interação com instâncias Redshift.
  
- **sys**: Biblioteca embutida do Python para interagir com o interpretador e passar argumentos de linha de comando.
  
- **getResolvedOptions (da biblioteca awsglue.utils)**: Função do SDK do AWS Glue que recupera parâmetros de um GlueJob.
