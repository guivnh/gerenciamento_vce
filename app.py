from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session, send_file
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import random
import string
import csv
import io
from io import StringIO

app = Flask(__name__)
app.secret_key = 'supersecretkey'


######################################################
# Acesso do DB Localmente

client = MongoClient('mongodb://localhost:27017/')
db = client['gerenciamento_vendas']
produtos_collection = db['produtos']
vendas_collection = db['vendas']
######################################################


@app.route('/')
def index():
    return render_template('index.html')

def converter_preco(preco_brl):
    preco_brl = preco_brl.replace('.', '').replace(',', '.')
    return float(preco_brl)

def formatar_preco(preco):
    try:
        if isinstance(preco, str):
            preco = preco.replace('.', '').replace(',', '.')
        preco = float(preco)
        return f"{preco:.2f}".replace('.', ',')
    except (ValueError, TypeError):
        return "0,00"

def formatar_quantidade(quantidade, tipo_venda):
    if tipo_venda in ['peso', 'mililitros']:
        return f"{quantidade:.0f}".replace('.', ',')
    return f"{int(quantidade)}"

def calcular_valor_quantidade(quantidade, preco, tipo_venda):
    if tipo_venda in ['peso', 'mililitros']:
        quantidade_kg_ml = quantidade / 1000
        valor = preco * quantidade_kg_ml
    else:
        valor = preco * quantidade
    return valor

@app.template_filter('formatar_preco')
def formatar_preco_filter(preco):
    return formatar_preco(preco)

@app.route('/cadastrar_produtos', methods=['GET', 'POST'])
def cadastrar_produtos():
    if request.method == 'POST':
        nome = request.form.get('nome')
        preco = request.form.get('preco')
        preco_compra = request.form.get('preco_compra')
        tipo_venda = request.form.get('tipo_venda')
        quantidade = request.form.get('quantidade')
        observacao = request.form.get('observacao')

        if not tipo_venda:
            flash("O campo 'tipo_venda' é obrigatório.", 'danger')
            return render_template('cadastrar_produtos.html')

        try:
            preco = converter_preco(preco)
            preco_compra = converter_preco(preco_compra)
        except ValueError as e:
            flash(f"Preço inválido: {e}", 'danger')
            return render_template('cadastrar_produtos.html')

        try:
            if tipo_venda == 'unitario':
                quantidade = int(float(quantidade.replace(',', '.')))
            else:
                quantidade = float(quantidade.replace(',', '.'))
        except ValueError:
            flash("Quantidade inválida.", 'danger')
            return render_template('cadastrar_produtos.html')

        # Salvar o produto no banco de dados
        salvar_produto(nome, preco, preco_compra, tipo_venda, quantidade, observacao)
        flash(f'Produto "{nome}" cadastrado com sucesso.', 'success')
        return render_template('cadastrar_produtos.html')

    return render_template('cadastrar_produtos.html')


def salvar_produto(nome, preco, preco_compra, tipo_venda, quantidade, observacao):
    produto = {
        "nome": nome,
        "preco": preco,
        "preco_compra": preco_compra,
        "tipo_venda": tipo_venda,
        "quantidade": quantidade,
        "observacao": observacao
    }
    produtos_collection.insert_one(produto)

@app.route('/listar_produtos')
def listar_produtos():
    produtos = produtos_collection.find()
    produtos_formatados = []

    for produto in produtos:
        produto = dict(produto)
        try:
            preco_formatado = formatar_preco(produto['preco'])
            preco_compra_formatado = formatar_preco(produto.get('preco_compra', 0.0))

            if produto['tipo_venda'] == 'peso':
                quantidade_formatada = f"{produto['quantidade']:.0f} gr. |"
                valor_monetario = produto['preco'] * (produto['quantidade'] / 1000)
                quantidade_formatada += f" (R$ {formatar_preco(valor_monetario)})"
            elif produto['tipo_venda'] == 'mililitros':
                quantidade_formatada = f"{produto['quantidade']:.0f} ml. |"
                valor_monetario = produto['preco'] * (produto['quantidade'] / 1000)
                quantidade_formatada += f" (R$ {formatar_preco(valor_monetario)})"
            else:
                quantidade_formatada = f"{int(produto['quantidade'])} un. |"
                valor_monetario = produto['preco'] * int(produto['quantidade'])
                quantidade_formatada += f" (R$ {formatar_preco(valor_monetario)})"

            produto['preco'] = preco_formatado
            produto['preco_compra'] = preco_compra_formatado
            produto['quantidade'] = quantidade_formatada
            produto['observacao'] = produto.get('observacao', '')
            produtos_formatados.append(produto)
        except ValueError:
            produto['preco'] = "Erro na formatação"
            produto['preco_compra'] = "Erro na formatação"
            produto['quantidade'] = "Erro na formatação"

    return render_template('listar_produtos.html', produtos=produtos_formatados)

@app.route('/editar_produto/<id>', methods=['GET', 'POST'])
def editar_produto(id):
    produto = produtos_collection.find_one({'_id': ObjectId(id)})
    if not produto:
        return redirect(url_for('listar_produtos'))

    produto = dict(produto)

    if request.method == 'POST':
        nome = request.form.get('nome')
        preco = request.form.get('preco')
        preco_compra = request.form.get('preco_compra', produto.get('preco_compra', '0'))
        tipo_venda = request.form.get('tipo_venda')
        quantidade = request.form.get('quantidade')
        observacao = request.form.get('observacao', '')

        if not tipo_venda:
            flash("O campo 'tipo_venda' é obrigatório.", 'danger')
            return render_template('editar_produto.html', produto=produto)

        try:
            preco = converter_preco(preco)
            preco_compra = converter_preco(preco_compra)
            quantidade = int(float(quantidade.replace(',', '.'))) if tipo_venda == 'unitario' else float(quantidade.replace(',', '.'))
        except ValueError as e:
            flash(f"Dados inválidos: {e}", 'danger')
            return render_template('editar_produto.html', produto=produto, erro=str(e))

        produtos_collection.update_one(
            {'_id': ObjectId(id)},
            {'$set': {
                'nome': nome,
                'preco': preco,
                'preco_compra': preco_compra,
                'quantidade': quantidade,
                'tipo_venda': tipo_venda,
                'observacao': observacao
            }}
        )
        flash("Produto atualizado com sucesso!", 'success')
        return redirect(url_for('listar_produtos'))

    preco_compra = formatar_preco(produto.get('preco_compra', 0))
    observacao = produto.get('observacao', '')
    preco = formatar_preco(produto.get('preco', 0))

    produto['preco_compra'] = preco_compra
    produto['observacao'] = observacao
    produto['preco'] = preco

    return render_template('editar_produto.html', produto=produto)

@app.route('/remover_produto/<id>', methods=['GET'])
def remover_produto(id):
    produto = produtos_collection.find_one({'_id': ObjectId(id)})
    if produto:
        produtos_collection.delete_one({'_id': ObjectId(id)})
        flash("Produto removido com sucesso!", 'success')
    else:
        flash("Produto não encontrado.", 'danger')
    return redirect(url_for('listar_produtos'))

@app.route('/realizar_venda', methods=['GET', 'POST'])
def realizar_venda():
    if 'carrinho' not in session:
        session['carrinho'] = []

    if request.method == 'POST':
        produto_id = request.form.get('produto_id')
        quantidade = request.form.get('quantidade')

        try:
            quantidade = float(quantidade.replace(',', '.'))
            if quantidade <= 0:
                flash("Quantidade deve ser maior que zero.", 'danger')
                return redirect(url_for('realizar_venda'))

        except ValueError:
            flash("Quantidade inválida.", 'danger')
            return redirect(url_for('realizar_venda'))

        try:
            produto_id = ObjectId(produto_id)
        except Exception as e:
            flash(f"Erro na conversão do ID: {e}", 'danger')
            return redirect(url_for('realizar_venda'))

        produto = produtos_collection.find_one({'_id': produto_id})
        if produto:
            tipo_venda = produto.get('tipo_venda', '')
            quantidade_disponivel = produto.get('quantidade', 0)

            if tipo_venda != 'unitario' and quantidade_disponivel > 0 and quantidade > quantidade_disponivel:
                flash("Quantidade excede a disponível em estoque.", 'danger')
                return redirect(url_for('realizar_venda'))

            item_carrinho = {
                'produto_id': str(produto_id),
                'nome': produto['nome'],
                'quantidade': quantidade,
                'preco_unitario': produto['preco'],
                'tipo_venda': produto['tipo_venda'],
            }

            session['carrinho'].append(item_carrinho)
            session.modified = True

            # Removendo a mensagem "Produto adicionado ao carrinho!"
            # flash("Produto adicionado ao carrinho!", 'success')
            return redirect(url_for('realizar_venda'))

        flash("Produto não encontrado.", 'danger')
        return redirect(url_for('realizar_venda'))

    produtos = produtos_collection.find()
    return render_template('realizar_vendas.html', produtos=produtos, carrinho=session.get('carrinho', []))


@app.route('/remover_item_carrinho/<produto_id>', methods=['POST'])
def remover_item_carrinho(produto_id):
    if 'carrinho' in session:
        session['carrinho'] = [item for item in session['carrinho'] if item['produto_id'] != produto_id]
        session.modified = True
    return redirect(url_for('realizar_venda'))

@app.route('/carrinho', methods=['GET', 'POST'])
def carrinho():
    if 'carrinho' not in session:
        session['carrinho'] = []

    carrinho = session['carrinho']

    if request.method == 'POST':
        total = 0
        itens_venda = []
        for item in carrinho:
            produto_id = ObjectId(item['produto_id'])
            produto = produtos_collection.find_one({'_id': produto_id})

            if produto:
                preco_unitario = produto['preco']
                tipo_venda = produto['tipo_venda']
                quantidade = item['quantidade']

                if produto['quantidade'] > 0 and quantidade > produto['quantidade']:
                    flash(f"Estoque insuficiente para {produto['nome']}.", 'danger')
                    return redirect(url_for('realizar_venda'))

                valor_item = calcular_valor_quantidade(quantidade, preco_unitario, tipo_venda)
                total += valor_item

                itens_venda.append({
                    'produto_id': produto_id,
                    'nome': produto['nome'],
                    'quantidade': quantidade,
                    'preco_unitario': preco_unitario,
                    'valor_total': valor_item,
                    'tipo_venda': tipo_venda
                })

                if produto['quantidade'] > 0:
                    produtos_collection.update_one(
                        {'_id': produto_id},
                        {'$inc': {'quantidade': -quantidade}}
                    )

        venda_id = gerar_id_venda()

        vendas_collection.insert_one({
            '_id': venda_id,
            'itens': itens_venda,
            'total': total,
            'data_hora': datetime.now()
        })

        session.pop('carrinho', None)
        #flash("Venda realizada com sucesso!", 'success')
        return redirect(url_for('listar_vendas'))

    return jsonify(carrinho)

def gerar_id_venda():
    agora = datetime.now()
    data_str = agora.strftime('%d%m%Y-%H%M')
    sufixo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
    return f"{data_str}-{sufixo}"

def obter_vendas_do_banco():
    try:
        vendas = list(vendas_collection.find())
        return vendas
    except Exception as e:
        print(f"Erro ao obter vendas do banco: {e}")
        return []


@app.route('/listar_vendas')
def listar_vendas():
    vendas = obter_vendas_do_banco()
    vendas_agrupadas = {}

    for venda in vendas:
        if 'itens' not in venda:
            print(f"Venda sem 'itens': {venda}")
            continue

        venda_id = str(venda.get('_id', ''))
        if venda_id not in vendas_agrupadas:
            vendas_agrupadas[venda_id] = {
                'venda_id': venda_id,
                'data': venda.get('data_hora', ''),
                'itens': []
            }

        for item in venda['itens']:
            produto = produtos_collection.find_one({'_id': item['produto_id']})
            if produto:
                # Certifique-se de que venda['data_hora'] é um objeto datetime
                data_e_hora = venda.get('data_hora')
                if isinstance(data_e_hora, datetime):
                    data_e_hora = data_e_hora.strftime('%d/%m/%Y %H:%M:%S')
                else:
                    # Se já for string, use diretamente
                    data_e_hora = str(data_e_hora)

                vendas_agrupadas[venda_id]['data'] = data_e_hora
                vendas_agrupadas[venda_id]['itens'].append({
                    'produto': produto['nome'],
                    'quantidade': formatar_quantidade(item['quantidade'], produto['tipo_venda']),
                    'preco_unitario': formatar_preco(produto['preco']),
                    'total': formatar_preco(item['valor_total']),
                    'tipo_venda': produto['tipo_venda'],
                    'observacao': produto.get('observacao', ''),
                    'id': str(item['produto_id'])
                })

    return render_template('listar_vendas.html', vendas=vendas_agrupadas.values())


@app.route('/remover_venda/<id>', methods=['GET'])
def remover_venda(id):
    try:
        venda = vendas_collection.find_one({'_id': id})

        if venda:
            vendas_collection.delete_one({'_id': id})
            #flash("Venda removida com sucesso!", 'success')
        else:
            flash("Venda não encontrada.", 'danger')

    except Exception as e:
        flash(f"Erro ao remover a venda: {e}", 'danger')

    return redirect(url_for('listar_vendas'))  # Certifique-se de que listar_vendas é a rota correta

@app.route('/estoque-baixo')
def estoque_baixo():
    produtos = produtos_collection.find()
    resultado = []

    for produto in produtos:
        quantidade = produto['quantidade']
        if produto['tipo_venda'] in ['peso', 'mililitros']:
            if quantidade == 0 or quantidade < 500:
                resultado.append({
                    'nome': produto['nome'],
                    'quantidade': quantidade,
                    'peso_ml': quantidade
                })
        else:
            if quantidade == 0 or quantidade < 5:
                resultado.append({
                    'nome': produto['nome'],
                    'quantidade': quantidade,
                    'peso_ml': 0
                })

    return jsonify(resultado)

@app.route('/exportar_produtos')
def exportar_produtos():
    produtos = produtos_collection.find()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

    # Cabeçalhos do CSV
    writer.writerow(['Nome', 'Preço', 'Preço de Compra', 'Tipo de Venda', 'Quantidade', 'Observação'])

    for produto in produtos:
        writer.writerow([
            produto.get('nome', ''),
            format_valor(produto.get('preco', '')),
            format_valor(produto.get('preco_compra', '')),
            produto.get('tipo_venda', ''),
            format_valor(produto.get('quantidade', '')),
            produto.get('observacao', '')
        ])

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', download_name='produtos.csv', as_attachment=True)

def format_valor(valor):
    if isinstance(valor, float):
        return f"{valor:.0f}".replace('.', ',')  # Formata para duas casas decimais e substitui ponto por vírgula
    return valor


@app.route('/importar_produtos', methods=['POST'])
def importar_produtos():
    file = request.files['file']
    if not file:
        flash('Nenhum arquivo selecionado', 'danger')
        return redirect(url_for('listar_produtos'))

    stream = io.TextIOWrapper(file.stream, encoding='utf-8', newline=None)
    reader = csv.reader(stream, delimiter=';')
    next(reader)  # Pula o cabeçalho do CSV

    for row in reader:
        nome, preco, preco_compra, tipo_venda, quantidade, observacao = row
        try:
            # Ajusta a formatação antes de converter
            preco = preco.replace(',', '.')
            preco_compra = preco_compra.replace(',', '.')
            quantidade = quantidade.replace(',', '.')

            preco = converter_preco(preco)
            preco_compra = converter_preco(preco_compra)
            quantidade = int(quantidade) if tipo_venda == 'unitario' else float(quantidade)
        except ValueError:
            flash(f"Erro ao converter dados para o produto {nome}.", 'danger')
            continue

        produtos_collection.insert_one({
            'nome': nome,
            'preco': preco,
            'preco_compra': preco_compra,
            'tipo_venda': tipo_venda,
            'quantidade': quantidade,
            'observacao': observacao
        })

    flash('Produtos importados com sucesso!', 'success')
    return redirect(url_for('listar_produtos'))


@app.route('/exportar_vendas')
def exportar_vendas():
    vendas = obter_vendas_do_banco()
    output = io.StringIO()
    writer = csv.writer(output, delimiter=';', quoting=csv.QUOTE_MINIMAL)

    # Cabeçalhos do CSV
    writer.writerow(
        ['ID da Venda', 'Nome do Produto', 'Quantidade', 'Preço Unitário', 'Valor Total', 'Data e Hora', 'Observação'])

    for venda in vendas:
        if 'itens' not in venda:
            continue

        venda_id = venda.get('_id', '')
        for item in venda['itens']:
            produto = produtos_collection.find_one({'_id': item['produto_id']})
            if produto:
                data_e_hora = venda['data_hora'].strftime('%d/%m/%Y %H:%M')
                writer.writerow([
                    venda_id,
                    produto['nome'],
                    formatar_quantidade(item['quantidade'], produto['tipo_venda']),
                    formatar_preco(produto['preco']),
                    formatar_preco(item['valor_total']),
                    data_e_hora,
                    produto.get('observacao', '')
                ])

    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode('utf-8')), mimetype='text/csv', download_name='vendas.csv', as_attachment=True)


@app.route('/importar_vendas', methods=['POST'])
def importar_vendas():
    if 'file' not in request.files:
        flash('Nenhum arquivo enviado.')
        return redirect(url_for('listar_vendas'))

    file = request.files['file']
    if file.filename == '':
        flash('Nenhum arquivo selecionado.')
        return redirect(url_for('listar_vendas'))

    if file and file.filename.endswith('.csv'):
        # Ler o conteúdo do arquivo CSV
        file_contents = file.read().decode('utf-8')
        csv_reader = csv.reader(StringIO(file_contents), delimiter=';')

        # Pular o cabeçalho
        next(csv_reader)

        vendas = {}

        for row in csv_reader:
            venda_id, produto_nome, quantidade, preco_unitario, valor_total, data_hora_str, observacao = row

            # Converter os dados
            try:
                quantidade = float(quantidade.replace(',', '.'))
                preco_unitario = float(preco_unitario.replace(',', '.'))
                valor_total = float(valor_total.replace(',', '.'))
                data_hora = datetime.strptime(data_hora_str, '%d/%m/%Y %H:%M')
            except ValueError as e:
                flash(f'Erro ao processar linha: {row}. Erro: {e}')
                continue

            produto = produtos_collection.find_one({'nome': produto_nome})
            if not produto:
                flash(f'Produto "{produto_nome}" não encontrado no banco de dados.')
                continue

            item = {
                'produto_id': produto['_id'],
                'quantidade': quantidade,
                'valor_total': valor_total
            }

            if venda_id not in vendas:
                vendas[venda_id] = {
                    'data_hora': data_hora,
                    'itens': []
                }

            vendas[venda_id]['itens'].append(item)

        # Inserir ou atualizar vendas no banco de dados
        for venda_id, venda_data in vendas.items():
            venda = {
                '_id': venda_id,
                'data_hora': venda_data['data_hora'],
                'itens': venda_data['itens']
            }
            vendas_collection.replace_one({'_id': venda_id}, venda, upsert=True)

        flash('Vendas importadas com sucesso.')
    else:
        flash('Formato de arquivo inválido. Por favor, envie um arquivo CSV.')

    return redirect(url_for('listar_vendas'))

# if __name__ == '__main__':
#     app.run(debug=True)