SQL_CRIAR_TABELA = """
    CREATE TABLE IF NOT EXISTS produto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco FLOAT NOT NULL,
        descricao TEXT NOT NULL,
        estoque INTEGER NOT NULL,
        categoria_id INTEGER,
        FOREIGN KEY (categoria_id) REFERENCES categoria (id)
    )
"""

SQL_INSERIR = """
    INSERT INTO produto(nome, preco, descricao, estoque, categoria_id)
    VALUES (?, ?, ?, ?, ?)
"""

SQL_OBTER_TODOS = """
    SELECT p.id, p.nome, p.preco, p.descricao, p.estoque, c.id AS categoria_id, c.nome AS categoria_nome, c.ativo AS categoria_ativo
    FROM produto p
    LEFT JOIN categoria c ON p.categoria_id = c.id
    WHERE c.ativo = 1
    ORDER BY p.nome
"""

SQL_ALTERAR = """
    UPDATE produto
    SET nome=?, preco=?, descricao=?, estoque=?, categoria_id=?
    WHERE id=?
"""

SQL_EXCLUIR = """
    DELETE FROM produto    
    WHERE id=?
"""

SQL_OBTER_UM = """
    SELECT p.id, p.nome, p.preco, p.descricao, p.estoque, c.nome AS categoria
    FROM produto p
    LEFT JOIN categoria c ON p.categoria_id = c.id
    WHERE p.id=?
"""

SQL_OBTER_QUANTIDADE = """
    SELECT COUNT(*) FROM produto
"""

SQL_OBTER_BUSCA = """
    SELECT p.id, p.nome, p.preco, p.descricao, p.estoque, c.nome AS categoria
    FROM produto p
    LEFT JOIN categoria c ON p.categoria_id = c.id
    WHERE (p.nome LIKE ? OR p.descricao LIKE ?)
      AND (? IS NULL OR c.id = ?)
    ORDER BY #1
    LIMIT ? OFFSET ?
"""

SQL_OBTER_QUANTIDADE_BUSCA = """
    SELECT COUNT(*)
    FROM produto p
    LEFT JOIN categoria c ON p.categoria_id = c.id
    WHERE (p.nome LIKE ? OR p.descricao LIKE ?)
      AND (? IS NULL OR c.id = ?)
"""