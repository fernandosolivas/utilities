#!/usr/bin/env python3
from kubernetes import client, config
from operator import itemgetter
from tabulate import tabulate

def get_pods_cpu_allocation():
    # Carrega a configuração do kubectl
    try:
        config.load_kube_config()
    except Exception as e:
        print(f"Erro ao carregar configuração do kubectl: {e}")
        return

    # Inicializa o cliente do Kubernetes
    v1 = client.CoreV1Api()
    
    try:
        # Lista todos os pods em todos os namespaces
        pods = v1.list_pod_for_all_namespaces(watch=False)
        
        # Lista para armazenar informações dos pods
        pod_resources = []
        
        for pod in pods.items:
            namespace = pod.metadata.namespace
            pod_name = pod.metadata.name
            
            # Inicializa as variáveis de CPU
            total_cpu_request = 0
            total_cpu_limit = 0
            
            # Soma os recursos de todos os containers no pod
            if pod.spec.containers:
                for container in pod.spec.containers:
                    if container.resources and container.resources.requests:
                        cpu_request = container.resources.requests.get('cpu', '0')
                        total_cpu_request += convert_cpu_to_millicores(cpu_request)
                    
                    if container.resources and container.resources.limits:
                        cpu_limit = container.resources.limits.get('cpu', '0')
                        total_cpu_limit += convert_cpu_to_millicores(cpu_limit)
            
            pod_resources.append({
                'namespace': namespace,
                'pod': pod_name,
                'cpu_request': total_cpu_request,
                'cpu_limit': total_cpu_limit
            })
        
        # Ordena os pods por CPU request (decrescente)
        sorted_pods = sorted(pod_resources, key=itemgetter('cpu_request'), reverse=True)
        
        # Formata os resultados para exibição
        headers = ['Namespace', 'Pod', 'CPU Request (cores)', 'CPU Limit (cores)']
        table_data = [[
            pod['namespace'],
            pod['pod'],
            f"{pod['cpu_request']/1000:.2f}",
            f"{pod['cpu_limit']/1000:.2f}"
        ] for pod in sorted_pods]
        
        print("\nPods ordenados por CPU Request (decrescente):")
        print(tabulate(table_data, headers=headers, tablefmt='grid'))
        
    except Exception as e:
        print(f"Erro ao listar pods: {e}")

def convert_cpu_to_millicores(cpu_str):
    """ 
    Converte diferentes formatos de CPU para millicores
    Exemplos: '100m' -> 100, '0.1' -> 100, '1' -> 1000
    """
    if not cpu_str:
        return 0
    
    try:
        if isinstance(cpu_str, str):
            if cpu_str.endswith('m'):
                return int(cpu_str[:-1])
            else:
                return int(float(cpu_str) * 1000)
        return int(cpu_str * 1000)
    except (ValueError, TypeError):
        return 0

if __name__ == "__main__":
    get_pods_cpu_allocation()