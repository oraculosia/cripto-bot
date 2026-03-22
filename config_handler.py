import yaml
from typing import Dict, Any
from datetime import datetime
import re

def load_yaml_config(file_path: str = 'config.yaml') -> Dict[Any, Any]:
    """Carrega a configuração do YAML existente ou cria um novo se não existir."""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {'credentials': {'users': []}}
    except FileNotFoundError:
        return {'credentials': {'users': []}}
    except UnicodeDecodeError as e:
        raise ValueError(f"Erro ao decodificar o arquivo: {e}")
    except Exception as e:
        raise ValueError(f"Erro ao carregar o arquivo de configuração: {e}")

def save_yaml_config(config: Dict[Any, Any], file_path: str = 'config.yaml') -> None:
    """Salva a configuração no arquivo YAML, garantindo que todos os valores sejam strings."""
    try:
        # Converter todos os valores para strings
        for user in config.get('credentials', {}).get('users', []):
            for key in user:
                user[key] = str(user[key])

        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, allow_unicode=True, default_flow_style=False)
    except Exception as e:
        raise ValueError(f"Erro ao salvar o arquivo de configuração: {e}")

def validate_client_data(client_data: Dict[str, Any]) -> None:
    """Valida os dados do cliente."""
    required_keys = ['username', 'name', 'email', 'password', 'role', 'whatsapp', 'endereco', 'cep', 'bairro', 'cidade', 'cpf_cnpj']

    # Verifica se todas as chaves necessárias estão presentes
    for key in required_keys:
        if key not in client_data:
            raise ValueError(f"Falta o campo obrigatório: {key}")

    # Validação de e-mail
    if not re.match(r"[^@]+@[^@]+\.[^@]+", client_data['email']):
        raise ValueError("E-mail inválido.")

    # Validação de CPF/CNPJ (exemplo simples, pode ser melhorado)
    if len(client_data['cpf_cnpj']) not in [11, 14]:
        raise ValueError("CPF/CNPJ deve ter 11 ou 14 dígitos.")

def add_client_to_config(client_data: Dict[str, Any]) -> None:
    """Adiciona um novo cliente à configuração."""
    validate_client_data(client_data)

    config = load_yaml_config()

    if 'credentials' not in config:
        config['credentials'] = {'users': []}

    # Verifica se o cliente já existe
    existing_users = config['credentials']['users']
    if any(user['email'] == client_data['email'] for user in existing_users):
        raise ValueError("Um cliente com este e-mail já existe.")

    # Gera o timestamp atual no formato ISO
    current_timestamp = datetime.now().isoformat()

    # Forçando todos os valores a serem strings
    new_user = {
        'username': str(client_data['username']),
        'name': str(client_data['name']),
        'email': str(client_data['email']),
        'password': str(client_data['password']),
        'role': str(client_data['role']),
        'whatsapp': str(client_data['whatsapp']),
        'endereco': str(client_data['endereco']),
        'cep': str(client_data['cep']),
        'bairro': str(client_data['bairro']),
        'cidade': str(client_data['cidade']),
        'cpf_cnpj': str(client_data['cpf_cnpj']),
        'created_at': str(current_timestamp)
    }

    config['credentials']['users'].append(new_user)
    save_yaml_config(config)
