from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import json
import os
from datetime import datetime

# ========== MODELOS DE DADOS ==========

class Produto(BaseModel):
    id: Optional[int] = None
    nome: str
    preco: float
    estoque: int

class Cliente(BaseModel):
    id: Optional[int] = None
    nome: str
    telefone: str = ""
    limite: float = 0
    divida: float = 0

class ItemVenda(BaseModel):
    produto_id: int
    nome: str
    preco: float
    quantidade: int

class Venda(BaseModel):
    cliente_id: Optional[int] = None
    itens: List[ItemVenda]
    tipo: str

class Pagamento(BaseModel):
    cliente_id: int
    valor: float

# ========== FUNÇÕES PARA LER/ESCREVER DADOS ==========

ARQUIVO_DADOS = "dados.json"

def ler_dados():
    if not os.path.exists(ARQUIVO_DADOS):
        dados_iniciais = {
            "produtos": [],
            "clientes": [],
            "vendas": []
        }
        with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
            json.dump(dados_iniciais, f, ensure_ascii=False, indent=2)
        return dados_iniciais
    
    with open(ARQUIVO_DADOS, "r", encoding="utf-8") as f:
        return json.load(f)

def salvar_dados(dados):
    with open(ARQUIVO_DADOS, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

# ========== CRIAR APLICAÇÃO ==========

app = FastAPI(title="Mercearia do João API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========== ROTAS DE PRODUTOS ==========

@app.get("/api/produtos")
def listar_produtos():
    dados = ler_dados()
    return dados["produtos"]

@app.post("/api/produtos")
def criar_produto(produto: Produto):
    dados = ler_dados()
    
    novo_id = 1
    if dados["produtos"]:
        novo_id = max(p["id"] for p in dados["produtos"]) + 1
    
    novo_produto = {
        "id": novo_id,
        "nome": produto.nome,
        "preco": produto.preco,
        "estoque": produto.estoque
    }
    
    dados["produtos"].append(novo_produto)
    salvar_dados(dados)
    return novo_produto

@app.put("/api/produtos/{produto_id}")
def atualizar_produto(produto_id: int, produto: Produto):
    dados = ler_dados()
    
    for i, p in enumerate(dados["produtos"]):
        if p["id"] == produto_id:
            dados["produtos"][i] = {
                "id": produto_id,
                "nome": produto.nome,
                "preco": produto.preco,
                "estoque": produto.estoque
            }
            salvar_dados(dados)
            return dados["produtos"][i]
    
    raise HTTPException(status_code=404, detail="Produto não encontrado")

@app.delete("/api/produtos/{produto_id}")
def deletar_produto(produto_id: int):
    dados = ler_dados()
    dados["produtos"] = [p for p in dados["produtos"] if p["id"] != produto_id]
    salvar_dados(dados)
    return {"mensagem": "Produto removido"}

# ========== ROTAS DE CLIENTES ==========

@app.get("/api/clientes")
def listar_clientes():
    dados = ler_dados()
    return dados["clientes"]

@app.post("/api/clientes")
def criar_cliente(cliente: Cliente):
    dados = ler_dados()
    
    novo_id = 1
    if dados["clientes"]:
        novo_id = max(c["id"] for c in dados["clientes"]) + 1
    
    novo_cliente = {
        "id": novo_id,
        "nome": cliente.nome,
        "telefone": cliente.telefone,
        "limite": cliente.limite,
        "divida": 0
    }
    
    dados["clientes"].append(novo_cliente)
    salvar_dados(dados)
    return novo_cliente

@app.put("/api/clientes/{cliente_id}")
def atualizar_cliente(cliente_id: int, cliente: Cliente):
    dados = ler_dados()
    
    for i, c in enumerate(dados["clientes"]):
        if c["id"] == cliente_id:
            dados["clientes"][i] = {
                "id": cliente_id,
                "nome": cliente.nome,
                "telefone": cliente.telefone,
                "limite": cliente.limite,
                "divida": c["divida"]
            }
            salvar_dados(dados)
            return dados["clientes"][i]
    
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

@app.delete("/api/clientes/{cliente_id}")
def deletar_cliente(cliente_id: int):
    dados = ler_dados()
    dados["clientes"] = [c for c in dados["clientes"] if c["id"] != cliente_id]
    salvar_dados(dados)
    return {"mensagem": "Cliente removido"}

# ========== ROTAS DE VENDAS ==========

@app.post("/api/vendas")
def registrar_venda(venda: Venda):
    dados = ler_dados()
    
    total = 0
    for item in venda.itens:
        total += item.preco * item.quantidade
        
        for produto in dados["produtos"]:
            if produto["id"] == item.produto_id:
                produto["estoque"] -= item.quantidade
                break
    
    cliente_nome = "Consumidor Final"
    if venda.cliente_id:
        for cliente in dados["clientes"]:
            if cliente["id"] == venda.cliente_id:
                cliente_nome = cliente["nome"]
                if venda.tipo == "fiado":
                    cliente["divida"] += total
                break
    
    nova_venda = {
        "id": len(dados["vendas"]) + 1,
        "data": datetime.now().isoformat(),
        "cliente_id": venda.cliente_id,
        "cliente_nome": cliente_nome,
        "total": total,
        "tipo": venda.tipo,
        "itens": [item.dict() for item in venda.itens]
    }
    
    dados["vendas"].append(nova_venda)
    salvar_dados(dados)
    
    return {"mensagem": "Venda registrada!", "total": total, "venda_id": nova_venda["id"]}

@app.post("/api/pagamentos")
def registrar_pagamento(pagamento: Pagamento):
    dados = ler_dados()
    
    for cliente in dados["clientes"]:
        if cliente["id"] == pagamento.cliente_id:
            if pagamento.valor > cliente["divida"]:
                raise HTTPException(status_code=400, detail="Valor maior que a dívida")
            
            cliente["divida"] -= pagamento.valor
            salvar_dados(dados)
            return {"mensagem": "Pagamento registrado!"}
    
    raise HTTPException(status_code=404, detail="Cliente não encontrado")

# ========== ROTAS DE RELATÓRIOS ==========

@app.get("/api/resumo")
def obter_resumo():
    dados = ler_dados()
    
    hoje = datetime.now().date()
    vendas_hoje = []
    total_vendas_hoje = 0
    
    for venda in dados["vendas"]:
        data_venda = datetime.fromisoformat(venda["data"]).date()
        if data_venda == hoje:
            vendas_hoje.append(venda)
            total_vendas_hoje += venda["total"]
    
    total_produtos = sum(p["estoque"] for p in dados["produtos"])
    total_dividas = sum(c["divida"] for c in dados["clientes"])
    
    vendas_por_produto = {}
    for venda in dados["vendas"]:
        for item in venda["itens"]:
            nome = item["nome"]
            if nome not in vendas_por_produto:
                vendas_por_produto[nome] = 0
            vendas_por_produto[nome] += item["quantidade"]
    
    mais_vendidos = sorted(
        [{"nome": k, "quantidade": v} for k, v in vendas_por_produto.items()],
        key=lambda x: x["quantidade"],
        reverse=True
    )[:5]
    
    ultimas_vendas = dados["vendas"][-5:][::-1]
    
    return {
        "vendas_hoje": total_vendas_hoje,
        "qtd_vendas_hoje": len(vendas_hoje),
        "total_produtos": total_produtos,
        "total_clientes": len(dados["clientes"]),
        "total_dividas": total_dividas,
        "mais_vendidos": mais_vendidos,
        "ultimas_vendas": ultimas_vendas
    }

@app.get("/api/devedores")
def listar_devedores():
    dados = ler_dados()
    return [c for c in dados["clientes"] if c["divida"] > 0]

if __name__ == "__main__":
    import uvicorn
    print("=" * 50)
    print("🚀 Mercearia do João - Servidor Python")
    print("📡 API rodando em: http://localhost:8000")
    print("📁 Dados salvos em:", ARQUIVO_DADOS)
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000)
