from datetime import datetime
from fastapi import APIRouter, Form, HTTPException, Path, Query, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
import mercadopago as mp
import os

from dtos.alterar_usuario_dto import AlterarUsuarioDTO
from dtos.alterar_senha_dto import AlterarSenhaDTO
from models.usuario_model import Usuario
from models.item_pedido_model import ItemPedido
from models.pedido_model import EstadoPedido, Pedido
from repositories.usuario_repo import UsuarioRepo
from repositories.item_pedido_repo import ItemPedidoRepo
from repositories.pedido_repo import PedidoRepo
from repositories.produto_repo import ProdutoRepo
from util.auth import conferir_senha, obter_hash_senha
from util.cookies import (
    adicionar_mensagem_alerta,
    adicionar_mensagem_erro,
    adicionar_mensagem_sucesso,
    excluir_cookie_auth,
)
from util.templates import obter_jinja_templates

router = APIRouter(prefix="/pedido")
templates = obter_jinja_templates("templates/pedido")

@router.get("/pagamento/{id_pedido:int}", response_class=HTMLResponse)
async def get_pagamento(request: Request, id_pedido: int = Path(...)):
    if not request.state.usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    pedido = PedidoRepo.obter_por_id(id_pedido)
    if pedido and (pedido.id_usuario != request.state.usuario.id):
        pedido = None
    if pedido.estado not in ["carrinho", "pendente"]:
        pedido = None
    if not pedido:
        response = RedirectResponse(url="/carrinho", status_code=status.HTTP_302_FOUND)
        criar_cookie_mensagem(
            response,
            "Pedido não encontrado. Pode ser que seu carrinho tenha expirado. Confira o carrinho de compras e clique em <b>Continuar Comprando</b> para iniciar uma nova compra.",
        )
        return response
    itens = ItemPedidoRepo.obter_por_pedido(pedido.id)
    total_carrinho = sum([item.valor_total for item in itens])
    pedido.itens = itens
    PedidoRepo.alterar_valor_total(pedido.id, total_carrinho)
    access_token = os.getenv("ACCESS_TOKEN_MP_PROD")
    # access_token = os.getenv("ACCESS_TOKEN_MP_TEST")
    print(f"\n\n\nTOKEN: {access_token}\n\n\n")
    sdk = mp.SDK(access_token=access_token)
    back_url_base = os.getenv("URL_TEST")
    preference = {
        "items": [
            {
                "title": f"Pedido {'{:06d}'.format(pedido.id)}",
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": total_carrinho,
            }
        ],
        "payer": {
            "name": request.state.usuario.nome,
            "email": request.state.usuario.email,
        },
        # "payer": {
        #     "name": "Test",
        #     "surname": "Test",
        #     "email": "test_user_1218031040@testuser.com",
        # },
        "back_urls": {
            "success": f"{back_url_base}/pedido/mp/sucesso/{pedido.id}",
            "failure": f"{back_url_base}/pedido/mp/falha/{pedido.id}",
            "pending": f"{back_url_base}/pedido/mp/pedente/{pedido.id}",
        },
        "auto_return": "approved",
    }
    preferenceResult = sdk.preference().create(preference)
    print(f"\n\nDados: {preferenceResult}")
    if preferenceResult:
        url_pagamento_mercado_pago = preferenceResult["response"]["init_point"]
        # url_pagamento_mercado_pago = preferenceResult["response"]["sandbox_init_point"]
        return RedirectResponse(
            url=url_pagamento_mercado_pago, status_code=status.HTTP_302_FOUND
        )


@router.get("/mp/sucesso/{id_pedido:int}", response_class=HTMLResponse)
async def get_mp_sucesso(
    request: Request,
    id_pedido: int = Path(...),
):
    pedido = PedidoRepo.obter_por_id(id_pedido)
    PedidoRepo.alterar_estado(id_pedido, EstadoPedido.PAGO.value)
    return RedirectResponse(f"/pedido/confirmado/{id_pedido}")


@router.get("/mp/falha/{id_pedido:int}", response_class=HTMLResponse)
async def get_mp_falha(
    request: Request,
    id_pedido: int = Path(...),
):
    response = RedirectResponse(f"/pedido/resumo?id_pedido={id_pedido}")
    criar_cookie_mensagem(
        response,
        "Houve alguma falha ao processar seu pagamento. Por favor, tente novamente.",
    )
    return response


@router.get("/mp/pendente/{id_pedido:int}", response_class=HTMLResponse)
async def get_mp_pendente(
    request: Request,
    id_pedido: int = Path(...),
):
    pedido = PedidoRepo.obter_por_id(id_pedido)
    PedidoRepo.alterar_estado(id_pedido, EstadoPedido.PAGO.value)
    return RedirectResponse(f"/pedido/detalhes/{id_pedido}")
