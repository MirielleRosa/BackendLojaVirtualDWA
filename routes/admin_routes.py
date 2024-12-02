import asyncio
from io import BytesIO
from typing import List, Optional
from fastapi import APIRouter, File, Form, Path, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image

from dtos.alterar_pedido_dto import AlterarPedidoDto
from dtos.alterar_produto_dto import AlterarProdutoDto
from dtos.inserir_produto_dto import InserirProdutoDto
from dtos.problem_details_dto import ProblemDetailsDto
from models.categoria_model import Categoria
from models.pedido_model import EstadoPedido
from models.produto_model import Produto
from models.usuario_model import Usuario
from repositories.categoria_repo import CategoriaRepo
from repositories.item_pedido_repo import ItemPedidoRepo
from repositories.pedido_repo import PedidoRepo
from repositories.produto_repo import ProdutoRepo
from repositories.usuario_repo import UsuarioRepo
from util.images import transformar_em_quadrada

SLEEP_TIME = 0.2
router = APIRouter(prefix="/admin")

@router.get("/obter_produtos")
async def obter_produtos():
    await asyncio.sleep(SLEEP_TIME)
    produtos = ProdutoRepo.obter_todos()
    for produto in produtos:
        print(f"Produto: {produto.nome}, Categoria ID: {produto.categoria_id}, Categoria: {produto.categoria_nome}, Categoria Ativo: {produto.categoria_ativo}")
    return produtos

@router.post("/inserir_produto", status_code=201)
async def inserir_produto(
    nome: str = Form(...),
    preco: float = Form(...),
    descricao: str = Form(...),
    estoque: int = Form(...),
    categoria_id: int = Form(...),
    imagem: Optional[UploadFile] = File(None)
):    
    produto_dto = InserirProdutoDto(
        nome=nome,
        preco=preco,
        descricao=descricao,
        estoque=estoque,
        categoria_id=categoria_id 
    )

    if imagem:
        conteudo_arquivo = await imagem.read()
        imagem_obj = Image.open(BytesIO(conteudo_arquivo))
        if not imagem_obj:
            pd = {
                "title": "imagem",
                "detail": "O arquivo enviado não é uma imagem válida.",
                "type": "invalid_file",
                "path": ["body", "imagem"],
            }
            return JSONResponse(pd, status_code=422)

        # Salvando a imagem
        imagem_quadrada = transformar_em_quadrada(imagem_obj)
        imagem_quadrada.save(f"static/img/produtos/{produto_dto.categoria_id:04d}.jpg", "JPEG")

    # Inserindo o produto no banco de dados
    await asyncio.sleep(SLEEP_TIME)  # Simulando atraso
    novo_produto = Produto(
        None, produto_dto.nome, produto_dto.preco, produto_dto.descricao, produto_dto.estoque,
        produto_dto.categoria_id
    )
    novo_produto = await ProdutoRepo.inserir(novo_produto)

    if novo_produto:
        return novo_produto
    else:
        pd = {
            "title": "erro_insercao",
            "detail": "O produto não pôde ser inserido.",
            "type": "database_error",
            "path": ["body"],
        }
        return JSONResponse(pd, status_code=500)

@router.post("/excluir_produto", status_code=204)
async def excluir_produto(id_produto: int = Form(..., title="Id do Produto", ge=1)):
    await asyncio.sleep(SLEEP_TIME)
    if ProdutoRepo.excluir(id_produto):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"O produto com id <b>{id_produto}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id_produto"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.get("/obter_produto/{id_produto}")
async def obter_produto(id_produto: int = Path(..., title="Id do Produto", ge=1)):
    await asyncio.sleep(SLEEP_TIME)
    produto = ProdutoRepo.obter_um(id_produto)
    if produto:
        return produto
    pd = ProblemDetailsDto(
        "int",
        f"O produto com id <b>{id_produto}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id_produto"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.post("/alterar_produto", status_code=204)
async def alterar_produto(inputDto: AlterarProdutoDto):
    await asyncio.sleep(SLEEP_TIME)
    produto = Produto(
        inputDto.id, inputDto.nome, inputDto.preco, inputDto.descricao, inputDto.estoque
    )
    if ProdutoRepo.alterar(produto):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"O produto com id <b>{inputDto.id}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.post("/alterar_pedido", status_code=204)
async def alterar_pedido(inputDto: AlterarPedidoDto):
    await asyncio.sleep(SLEEP_TIME)
    if PedidoRepo.alterar_estado(inputDto.id, inputDto.estado.value):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"O pedido com id <b>{inputDto.id}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.post("/cancelar_pedido", status_code=204)
async def cancelar_pedido(id_pedido: int = Form(..., title="Id do Pedido", ge=1)):
    await asyncio.sleep(SLEEP_TIME)
    if PedidoRepo.alterar_estado(id_pedido, EstadoPedido.CANCELADO.value):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"O pedido com id <b>{id_pedido}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.post("/evoluir_pedido", status_code=204)
async def evoluir_pedido(id_pedido: int = Form(..., title="Id do Pedido", ge=1)):
    await asyncio.sleep(SLEEP_TIME)
    pedido = PedidoRepo.obter_por_id(id_pedido)
    if not pedido:
        pd = ProblemDetailsDto(
            "int",
            f"O pedido com id <b>{id_pedido}</b> não foi encontrado.",
            "value_not_found",
            ["body", "id"],
        )
        return JSONResponse(pd.to_dict(), status_code=404)
    estado_atual = pedido.estado
    estados = [e.value for e in list(EstadoPedido) if e != EstadoPedido.CANCELADO]
    indice = estados.index(estado_atual)
    indice += 1
    if indice < len(estados):
        novo_estado = estados[indice]
        if PedidoRepo.alterar_estado(id_pedido, novo_estado):
            return None
    pd = ProblemDetailsDto(
        "int",
        f"O pedido com id <b>{id_pedido}</b> não pode ter seu estado evoluído para <b>cancelado</b>.",
        "state_change_invalid",
        ["body", "id"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.get("/obter_pedido/{id_pedido}")
async def obter_pedido(id_pedido: int = Path(..., title="Id do Pedido", ge=1)):
    # TODO: refatorar criando Dto com resultado específico
    await asyncio.sleep(SLEEP_TIME)
    pedido = PedidoRepo.obter_por_id(id_pedido)
    if pedido:
        itens = ItemPedidoRepo.obter_por_pedido(pedido.id)
        cliente = UsuarioRepo.obter_por_id(pedido.id_cliente)
        pedido.itens = itens
        pedido.cliente = cliente
        return pedido
    pd = ProblemDetailsDto(
        "int",
        f"O pedido com id <b>{id_pedido}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)


@router.get("/obter_pedidos_por_estado/{estado}")
async def obter_pedidos_por_estado(
    estado: EstadoPedido = Path(..., title="Estado do Pedido")
):
    await asyncio.sleep(SLEEP_TIME)
    pedidos = PedidoRepo.obter_todos_por_estado(estado.value)
    return pedidos


@router.get("/obter_usuarios")
async def obter_usuarios() -> List[Usuario]:
    await asyncio.sleep(SLEEP_TIME)
    usuarios = UsuarioRepo.obter_todos()
    return usuarios


@router.post("/excluir_usuario", status_code=204)
async def excluir_usuario(id_usuario: int = Form(...)):
    await asyncio.sleep(SLEEP_TIME)
    if UsuarioRepo.excluir(id_usuario):
        return None
    pd = ProblemDetailsDto(
        "int",
        f"O usuario com id <b>{id_usuario}</b> não foi encontrado.",
        "value_not_found",
        ["body", "id_produto"],
    )
    return JSONResponse(pd.to_dict(), status_code=404)

@router.get("/listar_categorias")
async def listar_categorias():
    categorias = CategoriaRepo.obter_todos()
    return categorias

@router.get("/listar_categorias_ativas")
async def listar_categorias_ativas():
    categorias = CategoriaRepo.obter_todos_ativos()
    return categorias

@router.get("/listar_categoria/{categoria_id}")
async def listar_categoria(categoria_id: int):
    categoria = CategoriaRepo.obter_um(categoria_id)
    if not categoria:
        pd = ProblemDetailsDto(
            "int",
            f"A categoria com id <b>{categoria_id}</b> não foi encontrada.",
            "value_not_found",
            ["path", "categoria_id"],
        )
        return JSONResponse(pd.to_dict(), status_code=404)
    return categoria

@router.post("/inserir_categoria", status_code=201)
async def inserir_categoria(nome: str = Form(..., title="Nome da Categoria")):
    categorias_existentes = {categoria.nome for categoria in CategoriaRepo.obter_todos()}
    
    if nome in categorias_existentes:
        pd = ProblemDetailsDto(
            "categoria",
            f"A categoria com o nome <b>{nome}</b> já existe.",
            "category_exists",
            ["body", "nome"],
        )
        return JSONResponse(pd.to_dict(), status_code=400)
    
    nova_categoria = Categoria(nome=nome)
    categoria_criada = CategoriaRepo.inserir(nova_categoria)

    if categoria_criada:
        return categoria_criada

    pd = ProblemDetailsDto(
        "categoria",
        "Não foi possível inserir a categoria.",
        "creation_failed",
        ["body", "nome"],
    )
    return JSONResponse(pd.to_dict(), status_code=500)

@router.post("/alterar_categoria", status_code=204)
async def alterar_categoria(
    categoria_id: int = Form(..., title="Id da Categoria"),
    nome: str = Form(..., title="Novo Nome da Categoria"),
    ativo: int = Form(..., title="Status da Categoria") 
):
    categoria = CategoriaRepo.obter_um(categoria_id)
    if not categoria:
        pd = ProblemDetailsDto(
            "int",
            f"A categoria com id <b>{categoria_id}</b> não foi encontrada.",
            "value_not_found",
            ["body", "categoria_id"],
        )
        return JSONResponse(pd.to_dict(), status_code=404)
    
    categorias_existentes = {categoria.nome for categoria in CategoriaRepo.obter_todos()}
    if nome in categorias_existentes and nome != categoria.nome:
        pd = ProblemDetailsDto(
            "categoria",
            f"Já existe uma categoria com o nome <b>{nome}</b>.",
            "category_exists",
            ["body", "nome"],
        )
        return JSONResponse(pd.to_dict(), status_code=400)
    
    categoria.nome = nome
    categoria.ativo = ativo  # Atualiza o status da categoria
    
    categoria_alterada = CategoriaRepo.alterar(categoria)
    
    if categoria_alterada:
        return None

    pd = ProblemDetailsDto(
        "int",
        f"Erro ao alterar a categoria com id <b>{categoria_id}</b>.",
        "update_failed",
        ["body", "categoria_id"],
    )
    return JSONResponse(pd.to_dict(), status_code=500)

@router.post("/excluir_categoria", status_code=204)
async def excluir_categoria(categoria_id: int = Form(..., title="Id da Categoria", ge=1)):
    categoria = CategoriaRepo.obter_um(categoria_id)
    if not categoria:
        pd = ProblemDetailsDto(
            "int",
            f"A categoria com id <b>{categoria_id}</b> não foi encontrada.",
            "value_not_found",
            ["body", "categoria_id"],
        )
        return JSONResponse(pd.to_dict(), status_code=404)
    
    categoria.ativo = 0 
    categoria_alterada = CategoriaRepo.alterar(categoria)
    
    if categoria_alterada:
        return None

    pd = ProblemDetailsDto(
        "int",
        f"Erro ao desativar a categoria com id <b>{categoria_id}</b>.",
        "deletion_failed",
        ["body", "categoria_id"],
    )
    return JSONResponse(pd.to_dict(), status_code=500)

# @router.post("/reativar_categoria", status_code=204)
# async def reativar_categoria(categoria_id: int = Form(..., title="Id da Categoria", ge=1)):
#     categoria = CategoriaRepo.obter_um(categoria_id)
#     if not categoria:
#         pd = ProblemDetailsDto(
#             "int",
#             f"A categoria com id <b>{categoria_id}</b> não foi encontrada.",
#             "value_not_found",
#             ["body", "categoria_id"],
#         )
#         return JSONResponse(pd.to_dict(), status_code=404)
    
#     if CategoriaRepo.reativar(categoria_id):
#         return None

#     pd = ProblemDetailsDto(
#         "int",
#         f"Erro ao reativar a categoria com id <b>{categoria_id}</b>.",
#         "update_failed",
#         ["body", "categoria_id"],
#     )
#     return JSONResponse(pd.to_dict(), status_code=500)
