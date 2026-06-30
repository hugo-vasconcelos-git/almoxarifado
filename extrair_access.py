#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair dados do arquivo Access (.accdb)
Salva tudo em JSON para análise
"""

import pyodbc
import json
import os
from pathlib import Path

# ============ CONFIGURAÇÃO ============
CAMINHO_ACCESS = r"Z:\COMUM\ETIQUETA\Etiquetas\Etiquetas V.02-.accdb"
SAIDA_JSON = "dados_etiquetas.json"

# ============ FUNÇÕES ============
def conectar_access(caminho):
    """Conecta ao arquivo Access"""
    try:
        conn = pyodbc.connect(
            f'Driver={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={caminho};'
        )
        print(f"✅ Conectado ao Access: {caminho}")
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        return None

def listar_tabelas(conn):
    """Lista todas as tabelas do Access"""
    try:
        cursor = conn.cursor()
        tabelas = cursor.tables(tableType='TABLE')
        nomes = [table.table_name for table in tabelas]
        print(f"📋 Tabelas encontradas: {len(nomes)}")
        for nome in nomes:
            print(f"   - {nome}")
        return nomes
    except Exception as e:
        print(f"❌ Erro ao listar tabelas: {e}")
        return []

def extrair_estrutura_tabela(conn, nome_tabela):
    """Extrai estrutura (colunas) de uma tabela"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM [{nome_tabela}] WHERE 1=0")
        colunas = [desc[0] for desc in cursor.description]
        return colunas
    except Exception as e:
        print(f"❌ Erro ao extrair estrutura de {nome_tabela}: {e}")
        return []

def extrair_dados_tabela(conn, nome_tabela):
    """Extrai todos os dados de uma tabela"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM [{nome_tabela}]")
        colunas = [desc[0] for desc in cursor.description]

        dados = []
        for row in cursor.fetchall():
            registro = dict(zip(colunas, row))
            dados.append(registro)

        print(f"✅ {nome_tabela}: {len(dados)} registros extraídos")
        return colunas, dados
    except Exception as e:
        print(f"❌ Erro ao extrair dados de {nome_tabela}: {e}")
        return [], []

def listar_queries(conn):
    """Lista todas as queries do Access"""
    try:
        cursor = conn.cursor()
        # Consultar tabela de sistema do Access
        cursor.execute("SELECT Name FROM MSysObjects WHERE Type=5 AND Flags=0")
        queries = [row[0] for row in cursor.fetchall()]
        if queries:
            print(f"🔍 Queries encontradas: {len(queries)}")
            for nome in queries:
                print(f"   - {nome}")
        return queries
    except Exception as e:
        print(f"⚠️  Não foi possível listar queries: {e}")
        return []

def main():
    """Função principal"""
    print("=" * 60)
    print("🗂️  EXTRATOR DE DADOS - MS ACCESS")
    print("=" * 60)

    # Verificar se arquivo existe
    if not os.path.exists(CAMINHO_ACCESS):
        print(f"❌ Arquivo não encontrado: {CAMINHO_ACCESS}")
        return

    # Conectar
    conn = conectar_access(CAMINHO_ACCESS)
    if not conn:
        return

    # Estrutura final
    dados_completos = {
        "arquivo": CAMINHO_ACCESS,
        "tabelas": {},
        "queries": []
    }

    # Extrair tabelas
    print("\n📊 EXTRAINDO TABELAS...")
    print("-" * 60)
    tabelas = listar_tabelas(conn)

    for nome_tabela in tabelas:
        colunas, dados = extrair_dados_tabela(conn, nome_tabela)
        if colunas:
            dados_completos["tabelas"][nome_tabela] = {
                "colunas": colunas,
                "total_registros": len(dados),
                "dados": dados
            }

    # Extrair queries
    print("\n🔍 EXTRAINDO QUERIES...")
    print("-" * 60)
    queries = listar_queries(conn)
    dados_completos["queries"] = queries

    # Salvar JSON
    print("\n💾 SALVANDO JSON...")
    print("-" * 60)
    try:
        with open(SAIDA_JSON, 'w', encoding='utf-8') as f:
            json.dump(dados_completos, f, ensure_ascii=False, indent=2, default=str)
        print(f"✅ Arquivo salvo: {SAIDA_JSON}")
        print(f"📁 Localização: {os.path.abspath(SAIDA_JSON)}")
    except Exception as e:
        print(f"❌ Erro ao salvar JSON: {e}")

    # Fechar conexão
    conn.close()
    print("\n✅ EXTRAÇÃO CONCLUÍDA!")
    print("=" * 60)

if __name__ == "__main__":
    main()
