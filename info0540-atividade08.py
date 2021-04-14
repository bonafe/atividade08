#!/bin/env python3
# https://neo4j.com/docs/cypher-manual/current/clauses/
# install pip3 install neo4j

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
    uri = 'neo4j://localhost:7687'
    driver = GraphDatabase.driver(uri, auth=("neo4j", "neo4j2021"), max_connection_lifetime=1000)
    session = driver.session()


def fecharConexao():
    global driver
    global session
    session.close()
    driver.close()


def processarLinhas(linhas):
    for linha in linhas[1:]:
        ips = re.findall(r"[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}", linha)
        ip_rede_destino = ips[0]
        ip_gateway = ips[1]

        verificaECria(ip_rede_destino)
        verificaECria(ip_gateway)
        criarArestaNeo4J(ip_rede_destino, ip_gateway)

def verificaECria(ip):
    # Verificar na lista local se o ip exite
    if not existeIP(ip):
        # Caso não exista cria um novo nó no Neo4j
        criarVerticeNeo4J(ip)


def criarVerticeNeo4J(ip):
    global session
    session.run("CREATE(novo_ip: IP {ip: '" + ip + "'});")

def criarArestaNeo4J(ip_destino, ip_gateway):
    global session
    session.run(
        "match(ip_origem: IP {ip: '" + ip_destino + "'}) match(ip_destino: IP {ip: '" + ip_gateway + "'})" +
        "create(ip_origem) - [variavel_conexao: CONEXAO] -> (ip_destino)" +
        "return ID(variavel_conexao);")


def existeIP(ip):
    global lista_ips
    try:
        lista_ips.index("ip")
        return True
    except:
        return False


abrirConexao()
processarLinhas(lerLinhas())
fecharConexao()
