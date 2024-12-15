#!/usr/bin/env python
from kubernetes import client, config

class K8S():
    def __init__(self):
        # Configura a conexão com o cluster
        config.load_kube_config()  # Use load_incluster_config() se o script rodar dentro do cluster
        self.v1 = client.CoreV1Api()

    def get_service_ip(self, service_name, namespace):
        try:
            # Obtém o serviço
            service = self.v1.read_namespaced_service(name=service_name, namespace=namespace)
            
            # Verifica se o serviço tem IP do tipo LoadBalancer
            if service.status.load_balancer.ingress:
                # print(service)
                lb_ip = service.status.load_balancer.ingress[0].ip
                # print(f"LoadBalancer IP: {lb_ip}")
                return lb_ip
            else:
                # print("O serviço ainda não tem um IP do tipo LoadBalancer.")
                raise Exception("O serviço ainda não tem um IP do tipo LoadBalancer.")
        except client.exceptions.ApiException as e:
            # print(f"Erro ao acessar o serviço: {e}")
            raise e
        
    