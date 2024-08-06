from datetime import datetime
from database.db import Database

db_produtos = Database().get_collection('produtos')
db_vendas = Database().get_collection('vendas')

def registrar_venda(produto_nome, quantidade, preco_final):
    try:
        venda = {
            'produto': produto_nome,
            'data': datetime.now().strftime('%Y-%m-%d'),
            'hora': datetime.now().strftime('%H:%M:%S'),
            'quantidade': quantidade,
            'preco_total': preco_final
        }
        # Atualiza a quantidade em estoque
        db_produtos.update_one(
            {'nome': produto_nome},
            {'$inc': {'quantidade': -quantidade}}
        )
        db_vendas.insert_one(venda)
        return True
    except Exception as e:
        print(f'Erro ao registrar venda: {e}')
        return False

def listar_vendas():
    try:
        vendas = list(db_vendas.find())
        return vendas
    except Exception as e:
        print(f'Erro ao listar vendas: {e}')
        return []
