# Importando banco de dados

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os


# criação de um dataframe

caminho_basededados = os.getcwd()
lista_arquivos = os.listdir(caminho_basededados)

dicionario = {}
contador = 0
for arquivo in lista_arquivos:
    if 'csv' in arquivo:
        contador += 1
        print(f'{contador} - {arquivo}')
        df = pd.read_csv(fr'{caminho_basededados}\{arquivo}', sep=';')
        dicionario[f'{arquivo}'] = df
        
        for chave, valor in dicionario.items():
            print(chave)
            display(chave, valor)
         
# unir todos os dfs em um só

df = pd.DataFrame()

df = pd.concat([df, dicionario['Contoso - Vendas - 2017.csv']])
df = df.merge(dicionario['Contoso - Cadastro Produtos.csv'], on='ID Produto')
df = df.drop(['Numero da Venda', 'ID Canal', 'Nome da Marca', 'Tipo'], axis=1)
df = df.merge(dicionario['Contoso - Clientes.csv'], on='ID Cliente')
df = df.drop(['Primeiro Nome','Sobrenome', 'Genero', 'Numero de Filhos', 'Data de Nascimento', 'Unnamed: 7', 'Unnamed: 8', 'Unnamed: 9', 'Unnamed: 10'], axis=1)
df = df.merge(dicionario['Contoso - Lojas.csv'], on='ID Loja')
df = df.drop(['Quantidade Colaboradores','País'], axis=1)
df = df.merge(dicionario['Contoso - Promocoes.csv'], on='ID Promocao')
df = df.drop(['Nome Promocao', 'Unnamed: 5', 'Unnamed: 6'], axis=1)
display(df)

# tratamento dos dados
df.info()
df[['Data da Venda', 'Data do Envio', 'Data Inicio', 'Data Termino']] = df[['Data da Venda', 'Data do Envio', 'Data Inicio', 'Data Termino']].astype('datetime64')
df['Custo Unitario'] = df['Custo Unitario'].str.replace(',','.').astype('float')
df['Preco Unitario'] = df['Preco Unitario'].str.replace(',','.').astype('float')
df['Percentual Desconto'] = df['Percentual Desconto'].str.replace(',','.').astype('float')

df.info()
# ##### Análises de Dados:
# quais lojas mais venderam no período?
# quanto cada loja gastou em promoções? 
# há correlação?
# criar uma coluna no df com o VALOR FINAL DA VENDA
df['Valor Final sem Promocao'] = df['Preco Unitario'] * (df['Quantidade Vendida'] - df['Quantidade Devolvida'])
df['Valor Final com Promocao'] = df['Valor Final sem Promocao'] - (df['Valor Final sem Promocao'] * df['Percentual Desconto'])

df_vendas_lojas = df[['Nome da Loja', 'Valor Final com Promocao']].groupby('Nome da Loja').sum()
df_vendas_lojas = df_vendas_lojas.sort_values(by='Valor Final com Promocao', ascending=False)
display(df_vendas_lojas)

df_vendas_lojas = df_vendas_lojas.head(30)
plt.figure(figsize=(15,5))
plt.title('Lojas que mais venderam no período')
grafico = sns.barplot(data=df_vendas_lojas, x=df_vendas_lojas.index, y=df_vendas_lojas['Valor Final com Promocao'])
grafico.tick_params(axis='x', rotation=90) 

# o valor total gasto com promoções por loja
df['Gasto com Promocao'] = df['Valor Final sem Promocao'] - df['Valor Final com Promocao']

df_promocoes_lojas = df[['Nome da Loja', 'Gasto com Promocao']].groupby('Nome da Loja').sum()
df_promocoes_lojas = df_promocoes_lojas.sort_values(by='Gasto com Promocao', ascending=False)
display(df_promocoes_lojas)

df_promocoes_lojas = df_promocoes_lojas.head(30)
plt.figure(figsize=(15,5))
plt.title('Lojas que mais investiram em promoção')
grafico = sns.barplot(data=df_promocoes_lojas, x=df_promocoes_lojas.index, y=df_promocoes_lojas['Gasto com Promocao'])
grafico.tick_params(axis='x', rotation=90) 

# há correlação entre o faturamento e o investimento em promoções?
df_correlacao = df.corr()

plt.figure(figsize=(15,15))
plt.title('Correlação entre as colunas do dataframe')
grafico = sns.heatmap(data=df_correlacao, annot=True, fmt=".1f")
grafico.tick_params(axis='x', rotation=90) 

print(f'De acordo com o gráfico há uma correlação de 70% entre o faturamento e o investimento em promoções.')

# ##### Análise de Dados:
# qual o lucro líquido da rede de lojas Contoso no período?

df['Lucro Líquido da Venda'] = df['Valor Final com Promocao'] - df['Custo Unitario']
lucro_liquido_total = df['Lucro Líquido da Venda'].sum()

print(f'O lucro líquido da rede de lojas Contoso no período é de R$ {lucro_liquido_total:,.2f}')
display(df)

#  Análise de Dados:
# quais os produtos mais vendidos em toda a rede em quantidade e em valor? há correlação?
# os produtos mais vendidos em quantidade na rede
df_produtos_rede = df[['Categoria', 'Quantidade Vendida', 'Quantidade Devolvida', 'Valor Final sem Promocao']].groupby('Categoria').sum()
df_produtos_rede['Quantidade Final'] = df_produtos_rede['Quantidade Vendida'] - df_produtos_rede['Quantidade Devolvida']
df_produtos_rede = df_produtos_rede.sort_values(by='Quantidade Final', ascending=False)
display(df_produtos_rede)

fig, ax = plt.subplots(figsize=(15,10))
plt.title('Comparação dos produtos mais vendidos e suas respectivas devoluções')
grafico = sns.barplot(data=df_produtos_rede, x=df_produtos_rede.index, y='Quantidade Final', ax=ax)
grafico.tick_params(axis='x', rotation=90) 
grafico = sns.lineplot(data=df_produtos_rede, x=df_produtos_rede.index, y=df_produtos_rede['Quantidade Devolvida']*10, marker="o", ax=ax)
grafico.tick_params(axis='x', rotation=90) 

# os lucros de cada produto da rede
df_produtos_rede = df_produtos_rede.sort_values(by='Valor Final sem Promocao', ascending=False)
display(df_produtos_rede)

plt.figure(figsize=(15,5))
plt.title('Valores de venda total de cada produto na rede')
grafico = sns.barplot(data=df_produtos_rede, x=df_produtos_rede.index, y='Valor Final sem Promocao')
grafico.tick_params(axis='x', rotation=90) 

# há correlação entre a quantidade vendida e o valor das vendas?
df_correlacao2 = df_produtos_rede.corr()

plt.figure(figsize=(5,5))
plt.title('Correlação entre as colunas do dataframe')
grafico = sns.heatmap(data=df_correlacao2, annot=True, fmt=".1f")
grafico.tick_params(axis='x', rotation=90) 

print(f'De acordo com o gráfico há uma correlação de 20% entre a quantidade de unidades vendidas e o valor das vendas.')

# gráfico comparativo da quantidade vendida e do valor das vendas
fig, ax = plt.subplots(figsize=(15,10))
plt.title('Comparação da quantidade vendida e do valor das vendas de cada produto na rede')
grafico = sns.lineplot(data=df_produtos_rede, x=df_produtos_rede.index, y=df_produtos_rede['Quantidade Final']*100, marker='x', ax=ax)
grafico = sns.barplot(data=df_produtos_rede, x=df_produtos_rede.index, y='Valor Final sem Promocao', ax=ax)
grafico.tick_params(axis='x', rotation=90) 

# ##### Análise de Dados:
# quais os clientes mais fiéis?

df_clientes_fieis = df[['ID Cliente', 'Quantidade Vendida', 'Quantidade Devolvida', 'Valor Final com Promocao']].groupby('ID Cliente').sum()
df_clientes_fieis['Quantidade Final'] = df_clientes_fieis['Quantidade Vendida'] - df_clientes_fieis['Quantidade Devolvida']
df_clientes_fieis = df_clientes_fieis.drop(['Quantidade Vendida', 'Quantidade Devolvida'], axis=1)

print(f'Os clientes mais fiéis por QUANTIDADE DE PRODUTOS:')
df_clientes_fieis = df_clientes_fieis.sort_values(by='Quantidade Final', ascending=False)
display(df_clientes_fieis)

print(f'Os clientes mais fiéis por VALOR GASTO COM PRODUTOS:')
df_clientes_fieis = df_clientes_fieis.sort_values(by='Valor Final com Promocao', ascending=False)
display(df_clientes_fieis)

# gráfico comparativo dos cliente mais fiéis pelas 2 categorias
df_clientes_fieis = df_clientes_fieis.head(30)

fig, ax = plt.subplots(figsize=(15,15))
plt.title('Comparação da quantidade e do valor dos produtos adquiridos pelos clientes mais fiéis da rede')
grafico = sns.barplot(data=df_clientes_fieis, x=df_clientes_fieis.index, y=df_clientes_fieis['Valor Final com Promocao'], ax=ax)
grafico = sns.lineplot(data=df_clientes_fieis, x=df_clientes_fieis.index, y=df_clientes_fieis['Quantidade Final']*10, marker='o', ax=ax)
grafico.tick_params(axis='x', rotation=90) 

# ##### Integração com o Power BI

# importar o df ao Power BI

# No Power BI: página inicial, obter dados, mais, outro, script do python, conectar, no script colocar o código python, ok

# editar o df no Power BI por meio de códigos Python

# aba Página inicial, Transformar dados (Power Querry), aba Transformar, Executar script Python
# o Power BI, por meio do Power Querry, chama o df de 'dataset'
# criar os códigos no Python e, depois, exportá-lo ao Power BI





