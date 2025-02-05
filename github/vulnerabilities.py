import requests
import csv
from datetime import datetime
import os
import argparse
from dotenv import load_dotenv

def get_vulnerabilities(repos, github_token):
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json',
        'X-GitHub-Api-Version': '2022-11-28'
    }
    
    all_vulnerabilities = []
    
    verify_url = 'https://api.github.com/user'
    try:
        verify_response = requests.get(verify_url, headers=headers)
        verify_response.raise_for_status()
        print('Token autenticado com sucesso')
    except requests.exceptions.HTTPError as e:
        print(f'Erro na autenticação do token: {str(e)}')
        return all_vulnerabilities
    
    for repo in repos:
        try:
            owner, repo_name = repo.split('/')
            url = f'https://api.github.com/repos/{owner}/{repo_name}/dependabot/alerts'
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 403:
                error_info = {
                    'repositorio': repo,
                    'severidade': 'N/A',
                    'pacote': 'N/A',
                    'versao_vulneravel': 'N/A',
                    'primeira_deteccao': 'N/A',
                    'estado': 'N/A',
                    'titulo': 'N/A',
                    'descricao': 'Acesso negado - Verifique permissões',
                    'link_github': 'N/A',
                    'status_processamento': 'ERRO_403'
                }
                all_vulnerabilities.append(error_info)
                print(f'Acesso negado para {repo}. Verifique permissões.')
                continue
                
            response.raise_for_status()
            vulnerabilities = response.json()
            
            if not vulnerabilities:  # Repositório sem vulnerabilidades
                no_vuln_info = {
                    'repositorio': repo,
                    'severidade': 'N/A',
                    'pacote': 'N/A',
                    'versao_vulneravel': 'N/A',
                    'primeira_deteccao': 'N/A',
                    'estado': 'N/A',
                    'titulo': 'N/A',
                    'descricao': 'Nenhuma vulnerabilidade encontrada',
                    'link_github': 'N/A',
                    'status_processamento': 'SEM_VULNERABILIDADES'
                }
                all_vulnerabilities.append(no_vuln_info)
            
            for vuln in vulnerabilities:
                # Pula vulnerabilidades com estado 'fixed'
                if vuln.get('state') == 'fixed':
                    continue
                    
                vulnerability_info = {
                    'repositorio': repo,
                    'severidade': vuln.get('security_advisory', {}).get('severity', 'N/A'),
                    'pacote': vuln.get('security_advisory', {}).get('package', {}).get('name', 'N/A'),
                    'versao_vulneravel': vuln.get('security_vulnerability', {}).get('vulnerable_version_range', 'N/A'),
                    'primeira_deteccao': vuln.get('created_at', 'N/A'),
                    'estado': vuln.get('state', 'N/A'),
                    'titulo': vuln.get('security_advisory', {}).get('summary', 'N/A'),
                    'descricao': vuln.get('security_advisory', {}).get('description', 'N/A').replace('\n', ' '),
                    'link_github': vuln.get('html_url', 'N/A'),
                    'status_processamento': 'SUCESSO'
                }
                all_vulnerabilities.append(vulnerability_info)
            
        except Exception as e:
            error_info = {
                'repositorio': repo,
                'severidade': 'N/A',
                'pacote': 'N/A',
                'versao_vulneravel': 'N/A',
                'primeira_deteccao': 'N/A',
                'estado': 'N/A',
                'titulo': 'N/A',
                'descricao': f'Erro ao processar: {str(e)}',
                'link_github': 'N/A',
                'status_processamento': 'ERRO'
            }
            all_vulnerabilities.append(error_info)
            print(f'Erro ao processar {repo}: {str(e)}')
    
    return all_vulnerabilities

def save_to_csv(vulnerabilities, output_file):
    fieldnames = [
        'repositorio',
        'severidade',
        'pacote',
        'versao_vulneravel',
        'primeira_deteccao',
        'estado',
        'titulo',
        'descricao',
        'link_github',
        'status_processamento'
    ]
    
    # Definindo ordem de prioridade para severidade
    severity_order = {
        'critical': 0,
        'high': 1,
        'medium': 2,
        'low': 3,
        'N/A': 4
    }
    
    # Ordenando primeiro por repositório e depois por severidade
    sorted_vulnerabilities = sorted(
        vulnerabilities,
        key=lambda x: (
            x['repositorio'],
            severity_order.get(x['severidade'].lower(), 5)
        )
    )
    
    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for vuln in sorted_vulnerabilities:
            writer.writerow(vuln)

def get_repositories(github_token, organization, prefix):
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    repos = []
    page = 1
    while True:
        url = f'https://api.github.com/orgs/{organization}/repos?per_page=100&page={page}'
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        repositories = response.json()
        if not repositories:
            break
            
        github_repos = [f"{organization}/{repo['name']}" for repo in repositories if not prefix or (prefix and prefix in repo['name'].lower())]
        repos.extend(github_repos)
        
        page += 1
    
    return repos

def main():
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()
    
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description='Busca vulnerabilidades em repositórios GitHub.')
    parser.add_argument('--token', help='Token de acesso do GitHub', default=os.getenv('GITHUB_TOKEN'))
    parser.add_argument('--org', help='Nome da organização no GitHub', default=os.getenv('GITHUB_ORG'))
    parser.add_argument('--prefix', help='Prefixo para filtrar repositórios', default=os.getenv('REPO_PREFIX', ''))
    
    args = parser.parse_args()
    
    # Verificar se token e organização foram fornecidos
    if not args.token:
        raise ValueError('Token do GitHub não fornecido. Use --token ou defina a variável de ambiente GITHUB_TOKEN')
    if not args.org:
        raise ValueError('Organização não fornecida. Use --org ou defina a variável de ambiente GITHUB_ORG')
    
    print('Buscando repositórios...')
    repos = get_repositories(args.token, args.org, args.prefix)
    print(f'Encontrados {len(repos)} repositórios')
    
    # Obter vulnerabilidades
    print('Buscando vulnerabilidades...')
    vulnerabilities = get_vulnerabilities(repos, args.token)
    
    # Gerar nome do arquivo com timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'vulnerabilidades_{timestamp}.csv'
    
    # Salvar no CSV
    save_to_csv(vulnerabilities, output_file)
    
    print(f'Relatório salvo em: {output_file}')
    print(f'Total de vulnerabilidades encontradas: {len(vulnerabilities)}')

if __name__ == '__main__':
    main()