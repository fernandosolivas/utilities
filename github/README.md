# GitHub Utils

Ferramenta para análise de vulnerabilidades em repositórios GitHub usando a API do Dependabot. A ferramenta gera um relatório CSV com as vulnerabilidades encontradas nos repositórios.

## Pré-requisitos

* Python 3.x instalado
* Token de acesso do GitHub com as seguintes permissões:
  * `repo`
  * `security_events`
  * `read:org`

## Instalação

1. Clone este repositório:

```bash
git clone https://github.com/fernandosolivas/utilities.git
cd utilities/github
```

2. (Opcional) Crie e ative um ambiente virtual:

```bash
python -m venv .venv
source .venv/bin/activate # Linux/Mac
# ou
.venv\Scripts\activate # Windows
```

3. Instale as dependências usando make:
```bash
make install
```

Ou manualmente:

```bash
pip install -r requirements.txt
```

## Configuração

1. Abra o arquivo `vulnerabilities.py`
2. Insira seu token do GitHub na variável `github_token`

## Como usar

Execute o script principal:
```bash
python vulnerabilities.py
```

O script irá:
1. Buscar todos os repositórios da organização e caso um `prefix` seja definido buscará somente os repos com esse 
2. Verificar vulnerabilidades usando o Dependabot
3. Gerar um arquivo CSV com o relatório no formato: `vulnerabilidades_AAAAMMDD_HHMMSS.csv`

### Estrutura do relatório CSV

O relatório contém as seguintes informações:
- Repositório
- Severidade da vulnerabilidade
- Pacote afetado
- Versão vulnerável
- Data da primeira detecção
- Estado atual
- Título da vulnerabilidade
- Descrição
- Link do GitHub
- Status do processamento

## Dependências

- requests==2.32.3
- Demais dependências listadas em `requirements.txt`

## Tratamento de Erros

O script lida com diferentes cenários:
- Erro 403 (Acesso negado)
- Repositórios sem vulnerabilidades
- Erros de processamento geral

Todos os erros são registrados no arquivo CSV final para análise posterior.