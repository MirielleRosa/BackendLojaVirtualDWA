import json
import sqlite3
from typing import List, Optional
from models.categoria_model import Categoria
from sql.categoria_sql import *
from util.database import obter_conexao

class CategoriaRepo:
    @classmethod
    def criar_tabela(cls):
        with obter_conexao() as conexao:
            cursor = conexao.cursor()
            cursor.execute(SQL_CRIAR_TABELA)
            
    @classmethod
    def inserir_categorias_json(cls, arquivo_json: str):
        try:
            with open(arquivo_json, "r") as f:
                categorias_data = json.load(f)

            for categoria_data in categorias_data:
                nome_categoria = categoria_data["nome"]

                # Verificar se a categoria já existe no banco
                if not cls.categoria_existe(nome_categoria):
                    categoria = Categoria(nome=nome_categoria)
                    cls.inserir(categoria)
                else:
                    print(f"A categoria '{nome_categoria}' já existe. Ignorando inserção.")
                    
        except FileNotFoundError:
            print(f"Arquivo {arquivo_json} não encontrado.")
        except json.JSONDecodeError:
            print("Erro ao decodificar o JSON.")
        except Exception as ex:
            print(f"Erro ao inserir categorias: {ex}")

    @classmethod
    def categoria_existe(cls, nome_categoria: str) -> bool:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute("SELECT 1 FROM categoria WHERE nome = ?", (nome_categoria,))
                return cursor.fetchone() is not None
        except sqlite3.Error as ex:
            print(f"Erro ao verificar categoria: {ex}")
            return False
        
    @classmethod
    def inserir(cls, categoria: Categoria) -> Optional[Categoria]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_INSERIR, (categoria.nome,))
                if cursor.rowcount > 0:
                    categoria.id = cursor.lastrowid
                    return categoria
        except sqlite3.Error as ex:
            print(ex)
            return None

    @classmethod
    def obter_todos(cls) -> List[Categoria]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tuplas = cursor.execute(SQL_OBTER_TODOS).fetchall()
                categorias = [Categoria(*t) for t in tuplas]
                return categorias
        except sqlite3.Error as ex:
            print(ex)
            return []
        
    @classmethod
    def obter_todos_ativos(cls) -> List[Categoria]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tuplas = cursor.execute(SQL_OBTER_TODOS_ATIVOS).fetchall()
                categorias = [Categoria(*t) for t in tuplas]
                return categorias
        except sqlite3.Error as ex:
            print(ex)
            return []

    @classmethod
    def alterar(cls, categoria: Categoria) -> bool:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_ALTERAR, (categoria.nome, categoria.ativo, categoria.id))
                return cursor.rowcount > 0
        except sqlite3.Error as ex:
            print(ex)
            return False

    @classmethod
    def excluir(cls, id: int) -> bool:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_DESATIVAR, (id,))
                return cursor.rowcount > 0
        except sqlite3.Error as ex:
            print(ex)
            return False

    @classmethod
    def obter_um(cls, id: int) -> Optional[Categoria]:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                tupla = cursor.execute(SQL_OBTER_UM, (id,)).fetchone()
                if not tupla: 
                    return None
                categoria = Categoria(*tupla)
                return categoria
        except sqlite3.Error as ex:
            print(ex)
            return None

    @classmethod
    def reativar(cls, id: int) -> bool:
        try:
            with obter_conexao() as conexao:
                cursor = conexao.cursor()
                cursor.execute(SQL_REATIVAR, (id,))
                return cursor.rowcount > 0
        except sqlite3.Error as ex:
            print(ex)
            return False