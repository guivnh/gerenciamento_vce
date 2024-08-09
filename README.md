# Sistema de Controle de Estoque e Gerenciamento de Vendas

## Descrição

O projeto visa proporcionar aos pequenos e médios empreendedores uma maneira fácil e gratuita de gerenciar seus estoques e vendas. O sistema é acessível localmente e oferece uma interface intuitiva para controle completo das operações de venda e estoque.

## Funcionalidades

- **Página Inicial**: Acesso local na porta 8080 (http://localhost:8080/) com uma página inicial que contém botões para acessar os módulos do sistema.


- **Módulo de Cadastro de Produtos**: Permite adicionar novos produtos com campos para:
  - Preço de venda;
  - Preço de compra (opcional);
  - Tipo de venda (unitária, gramas ou mililitros);
  - Quantidade em estoque (opcional);
  - Observações (opcional).


- **Módulo de Lista de Produtos Cadastrados**: Exibe uma lista com as colunas:
  - Nome do produto;
  - Preço de venda;
  - Preço de compra;
  - Quantidade e valor total em estoque;
  - Observações;
  - Opções de edição e exclusão do produto;
  - Exportação e importação da lista em formato CSV.


- **Módulo de Realizar Venda**: Permite selecionar produtos e:
  - Exibe o preço de venda e quantidade disponível;
  - Inserir a quantidade desejada para venda;
  - Calcula automaticamente o valor total do preço do produto X quantidade para venda;
  - Adicionar múltiplos produtos para uma única venda.


- **Módulo de Lista de Vendas Realizadas**: Mostra uma lista com:
  - ID única da venda;
  - Nome do produto;
  - Quantidade vendida;
  - Preço (por unidade, gramas ou mililitros);
  - Valor total do produto listado para venda;
  - Data e hora da venda;
  - Observações;
  - Botão de exclusão de vendas;
  - Cálculo total da venda;
  - Exportação e importação da lista em formato CSV.

## Manual do usuário

- Vídeo guia simples de utilização do aplicativo rodando localmente: [Vídeo no YOUTUBE.](https://youtu.be/j1UxKJodvNo)
- [Manual básico do usuário.](Manual.pdf) Em PDF.

## Desenvolvimento

O software foi desenvolvido usando:
- **Linguagem**: Python.
- **Framework**: Flask.
- **Banco de Dados**: MongoDB (com pymongo).
- **Frontend**: HTML, CSS, e JavaScript para funcionalidades específicas.

### Dependências

#### Para clientes:

- Flask
- Jinja2
- MarkupSafe
- Werkzeug
- click
- itsdangerous
- pymongo
- MongoDB 
- waitress

#### Para desenvolvimento:

- Flask
- Jinja2
- MarkupSafe
- Werkzeug
- blinker
- click
- colorama
- dnspython
- itsdangerous
- numpy
- pandas
- pip
- pyasn1
- pymongo
- MongoDB
- python-dateutil
- pytz
- rsa
- six
- tzdata
- waitress

### Configuração padrão do ambiente de execução

- Instale as dependências necessárias ao seu modo de uso(Cliente ou Desenvolvedor).
- Instale o MongoDB e use-o como serviço(localhost:27017). Crie o banco de dados 'gerenciamento_vendas' e as coleções 'produtos' e 'vendas'.

## Docker

O projeto inclui:
- **Dockerfile**: Para criar e executar o ambiente de desenvolvimento e produção.
- **requirements.txt**: Lista de dependências necessárias para o ambiente Python.

## Licença

Este projeto está licenciado sob a [Apache License 2.0](LICENSE.txt). Veja o arquivo LICENSE para mais detalhes.

## Contato

Para mais informações, entre em contato com [Guilherme Vanhoni](mailto:guivnh@gmail.com).