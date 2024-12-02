SQL_CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    ativo INTEGER DEFAULT 1
    );
"""

SQL_INSERIR= """
    INSERT INTO categoria(nome)
    VALUES (?)
"""

SQL_OBTER_TODOS = """
    SELECT id, nome, ativo
    FROM categoria
    ORDER BY nome
"""

SQL_OBTER_TODOS_ATIVOS = """
    SELECT id, nome, ativo
    FROM categoria
    WHERE Ativo = 1
    ORDER BY nome
"""

SQL_ALTERAR = """
    UPDATE categoria
    SET nome=?, ativo=?
    WHERE id=?
"""

SQL_DESATIVAR = """
UPDATE categorias
SET ativo = 0
WHERE id = ?
"""

SQL_OBTER_UM = """
    SELECT id, nome
    FROM categoria
    WHERE id=?
"""

SQL_REATIVAR = """
    UPDATE categoria
    SET ativo = 1
    WHERE id = ?
"""