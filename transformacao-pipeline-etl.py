import pandas as pd # para manipulação de dados
import boto3   # Importando o boto3, ele permite que os desenvolvedores Python interajam com serviços AWS, como S3.
from io import BytesIO  # Permite tratar bytes em memória como um "arquivo virtual" para leitura.
import psycopg2 # Para conectar e interagir com o banco de dados Redshift
import sys # Acesso a funções e variáveis do sistema.
from awsglue.utils import getResolvedOptions # Recupera parâmetros definidos no GlueJob.

########## Extração
print('Iniciando extração de dados')
# Inicializa o cliente do boto3 para interagir com o serviço Amazon S3
s3 = boto3.client('s3')

# Define o nome do bucket S3 onde o arquivo CSV está armazenado e o caminho (chave) do objeto dentro do bucket S3 que será acessado
bucket_name = "fonte-pipeline-etl"
object_key = "WA_Fn-UseC_-Telco-Customer-Churn.csv"

# Obtenção do objeto CSV do S3
response = s3.get_object(Bucket=bucket_name, Key=object_key)

# Lendo o conteúdo do objeto obtido em um buffer temporário.
buffer = BytesIO(response['Body'].read())

# Lendo o buffer diretamente com o pandas para obter um DataFrame.
print(f'Iniciando leitura dos dados do arquivo {object_key} no bucket {bucket_name}')
df = pd.read_csv(buffer)
print('Dados lidos com sucesso')

########## Transformação
print('Iniciando Transformações de dados')
# Demanda 1
df = df[['customerID', 'gender', 'SeniorCitizen', 'Partner', 'Dependents', 'tenure']]
print('Demanda 1 DONE')
# Demanda 2
df['SeniorCitizen'] = df['SeniorCitizen'].replace({0: False, 1: True})
print('Demanda 2 DONE')
# Demanda 3
df['Partner'] = df['Partner'].replace({'Yes': True, 'No': False})
df['Dependents'] = df['Dependents'].replace({'Yes': True, 'No': False})
print('Demanda 3 DONE')
# Demanda 4
def classificar_clientes(tenure):
    if tenure <= 6:
        return 'new'
    elif tenure <= 12:
        return 'bronze'
    elif tenure <= 36:
        return 'silver'
    elif tenure <= 60:
        return 'gold'
    else:
        return 'platinum'
df['classificacao'] = df['tenure'].apply(classificar_clientes)
print('Demanda 4 DONE')
print(f'Visualizando amostra de dados a serem inseridos no Redshift \n {df.head()}')

# Limitando para 100 registros para economizar tempo de processamento
df = df.head(100)

########## Carregamento(Load)
print('Iniciando Carregamento de dados no Redshift')

# Informações de Conexão com o Redshift
args = getResolvedOptions(sys.argv, [
    'REDSHIFT_HOST',
    'REDSHIFT_DBNAME',
    'REDSHIFT_PORT',
    'REDSHIFT_USER',
    'REDSHIFT_PASSWORD'
])

redshift_host = args['REDSHIFT_HOST']
redshift_dbname = args['REDSHIFT_DBNAME']
redshift_port = args['REDSHIFT_PORT']
redshift_user = args['REDSHIFT_USER']
redshift_password = args['REDSHIFT_PASSWORD']

# Estabelecendo uma conexão com o banco de dados usando a biblioteca psycopg2.
conn = psycopg2.connect(
    host=redshift_host,         # Endereço do servidor do banco de dados.
    dbname=redshift_dbname,     # Nome do banco de dados.
    user=redshift_user,         # Nome de usuário para conexão.
    password=redshift_password, # Senha do usuário.
    port=redshift_port          # Porta para conexão.
)

# Criando um objeto cursor que permite executar comandos SQL no banco de dados.
cursor = conn.cursor()

# Query SQL para excluir a tabela 'dados_finais' se ela já existir no banco de dados.
# Esta ação é irreversível e, em cenários de produção, pode não ser o desejado.É apenas para fins didáticos
drop_table_query = """
DROP TABLE IF EXISTS dados_finais;
"""

# Executando o comando de exclusão
cursor.execute(drop_table_query)

# Query SQL para criar uma nova tabela chamada 'dados_finais' com determinadas colunas e tipos.
create_table_query = """
CREATE TABLE dados_finais (
    customerID VARCHAR(255),
    gender VARCHAR(50),
    SeniorCitizen BOOLEAN,
    Partner BOOLEAN,
    Dependents BOOLEAN,
    tenure INT,
    classificacao VARCHAR(50)
);
"""

# Executando o comando de criar a tabela
cursor.execute(create_table_query)

# Confirmando (commit) as alterações no banco de dados
conn.commit()

# Inserindo dados do DataFrame na tabel, linha a linha
print('Inserindo dados no Redshift')
for index, row in df.iterrows():
    insert_query = """
    INSERT INTO dados_finais (
        customerID, gender, SeniorCitizen, Partner, Dependents, tenure, classificacao
    ) VALUES (%s, %s, %s, %s, %s, %s, %s);
    """
    cursor.execute(insert_query, tuple(row))
    conn.commit()

# Fechando o cursor e a conexão com o banco de dados, para liberar os recursos.
cursor.close()
conn.close()

print(f'Carregamento de dados no Redshift concluído com sucesso!Foram carregados {df.shape[0]} registros na tabela')
