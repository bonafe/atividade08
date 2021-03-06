#!/bin/env python3
# https://neo4j.com/docs/cypher-manual/current/clauses/
# install pip3 install neo4j

#Grupo Python na Veia
#Daniela Jardini
#Luis Eduardo Moreira Saran
#Fernando Bonafé
#João Batista Barros Bittencourt
#Marcos Edson Cornelio

from neo4j import GraphDatabase
import re

session = None
driver = None

lista_ips = []


def lerLinhas():
    f = open('iproute-router-ic.txt', "r")
    linhas = f.readlines()
    f.close()
    return linhas


def abrirConexao():
    global driver
    global session
    print("Abrindo conexao\n")
    uri = 'neo4j://localhost:7687'
    driver = GraphDatabase.driver(uri, auth=("neo4j", "neo4j2021"), max_connection_lifetime=1000)
    session = driver.session()


def fecharConexao():
    global driver
    global session
    print("Fechando conexao\n")
    session.close()
    driver.close()

def limparNeo4J():
    global session
    print ("Limpando linhas\n")
    session.run("match(n) detach  delete  n;")

def processarLinhas(linhas):
    for linha in linhas[1:]:
        ips = re.findall(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", linha)
        ip_rede_destino = ips[0]
        ip_gateway = ips[1]

        verificaECria(ip_rede_destino, "REDE_DESTINO")
        verificaECria(ip_gateway, "GATEWAY")
        criarArestaNeo4J(ip_gateway, ip_rede_destino)

def verificaECria(ip, tipo):
    # Verificar na lista local se o ip exite
    if not existeIP(ip):
        print(f'IP não encontrado! Criando ip: {ip}')
        # Caso não exista cria um novo nó no Neo4j
        criarVerticeNeo4J(ip, tipo)
    else:
        print(f"********************** IP ENCONTRADO!!!!!!!!!!!!! {ip}")


def criarVerticeNeo4J(ip, tipo):
    global session
    session.run("CREATE(novo_ip: " + tipo + " {ip: '" + ip + "'});")

def criarArestaNeo4J(ip_gateway, ip_destino):
    global session
    print(f'Criando aresta: {ip_gateway} -> {ip_destino}')
    session.run(
        "match(ip_destino: REDE_DESTINO {ip: '" + ip_destino + "'}) match(ip_gateway: GATEWAY {ip: '" + ip_gateway + "'})" +
        "create(ip_gateway) - [variavel_conexao: CONEXAO] -> (ip_destino)" +
        "return ID(variavel_conexao);")


def existeIP(ip):
    global lista_ips
    try:
        lista_ips.index(ip)
        return True
    except:
        lista_ips.append(ip)
        return False


abrirConexao()
limparNeo4J()
processarLinhas(lerLinhas())
fecharConexao()
