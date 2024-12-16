# ScriptAtualizacao-2.0

Autoria: Gustavo (?), Israel Borges, Jhonatan Borges.

## Sobre o projeto.

Versão atualizada do script de atualização automática de arquivos recebidos pelo email.

## Execução do Script

Requisitos: Python 3.10+

Existem duas opções de script, uma que mantém um histórico de atualização por questões de eficiência, e uma que não tem histórico por questões de simplicidade. A utilização dos scripts é feita importando o modulo relatorios na pasta src, e chamando a função escolhida. O caminho do arquivo de configuração deve ser passado na chamda da função.

**Arquivo de configuração**

- adicionar os seguintes atributos ao arquivo(em json):
  - *username*: nome de usuário do email
  - *password*: senha de aplicação. NÃO É A MESMA QUE A SENHA DA CONTA (mais informações neste [link](https://support.google.com/mail/answer/185833?hl=pt-BR))
  - *history_path*: Caminho para o arquivo de histórico
  - *file_list*: Lista de arquivos configurados.

- atributo opcional:
    - *rementes*: lista de endereços de email

- atributos do arquivo, na lista file_list:
    - *filename*: nome do arquivo, com extensão. É a palavra chave utilizada na pesquiva do script
    - *remetente*: remetente do email
    - *path*: caminho do *diretório*, onde o arquivo vai ser salvo
    - *save_as* (opcional): nome do arquivo, caso tenha que ser renomeado
    - *alway_save*(opcional): booleano que ignora o historico e sempre salva o arquivo
    - *after_save*(opcional): função a ser chamada após salvar o arquivo (para adicionar mais, uma palavra chave nova e substituição precisa ser definida, no código fonte)
    - *encoding*(opcional): codificação do arquivo, padrão é utf-8

na lista de arquivos, alguns atributos podem ser expandidos utilizando a sintaxe `${<palavra-chave>}`, as palavras chave são:
- THISYEAR: é substituida pelo ano atual. ex: `'save_as': '${THISYEAR}.xlsx'`
- REMETENTE: caso o atributo remetentes esteja definido, substitui a variavel pelo remente definido no indice. ex: `'remetente': '${REMETENTE.0}'`
- RENAME_AFTE_SAVE: substituido pelo objeto da função rename_afte_save definida no arquivo helpers.py

**Pelo Script Local em (ver [`script_local.py`](./utils/script_local.py)):**

- Configurar os caminhos do módulo e arquivo de configuração nas variáveis dentro do código e executar o arquivo pelo python.
