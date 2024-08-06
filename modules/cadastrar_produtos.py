from database.db import Database
from bson.objectid import ObjectId

db = Database().get_collection('produtos')

def cadastrar_produto(nome, tipo_venda, preco, quantidade):
    produto = {
        'nome': nome,
        'tipo_venda': tipo_venda,
        'preco': float(preco),
        'quantidade': int(quantidade)
    }
    try:
        db.insert_one(produto)
        return True
    except Exception as e:
        print(f'Erro ao cadastrar produto: {e}')
        return False

def obter_produto(produto_id):
    try:
        produto = db.find_one({'_id': ObjectId(produto_id)})
        return produto
    except Exception as e:
        print(f'Erro ao obter produto: {e}')
        return None

def atualizar_produto(produto_id, nome, tipo_venda, preco, quantidade):
    try:
        db.update_one(
            {'_id': ObjectId(produto_id)},
            {'$set': {
                'nome': nome,
                'tipo_venda': tipo_venda,
                'preco': float(preco),
                'quantidade': int(quantidade)
            }}
        )
        return True
    except Exception as e:
        print(f'Erro ao atualizar produto: {e}')
        return False

def excluir_produto(produto_id):
    try:
        db.delete_one({'_id': ObjectId(produto_id)})
        return True
    except Exception as e:
        print(f'Erro ao excluir produto: {e}')
        return False
