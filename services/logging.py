import logging
import memcache
import dotenv
import os


class MemcachedLogger:
    def __init__(self):
        # Configuração do servidor Memcached
        self.host = os.environ.get('MEMCACHED_HOST')
        self.port = os.environ.get('MEMCACHED_PORT')

        # Inicialize o cliente Memcached
        self.mc = memcache.Client([f'{self.host}:{self.port}'])

        # Configuração básica do sistema de log
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s [%(levelname)s] %(message)s')

        # Crie uma instância de log
        self.logger = logging.getLogger('app')

    def save_logs_to_memcached(self, message: str):
        try:
            if message is not None:
                # Use a chave adequada para salvar os logs no Memcached
                logs = self.mc.get('logs') or []
                logs.append(message)
                self.mc.set('logs', logs)
                print('Sucesso ao salvar logs no Memcached')
            else:
                print(message)
        except Exception as e:
            self.logger.error(f'Erro ao salvar logs no Memcached: {e}')

    def log_info(self, message: str):
        self.logger.info(message)
        print(message)
        self.save_logs_to_memcached(message)

    def log_warning(self, message: str):
        self.logger.warning(message)
        self.save_logs_to_memcached(message)

    def log_error(self, message: str):
        self.logger.error(message)
        self.save_logs_to_memcached(message)

    def log_exception(self, message: str):
        self.logger.exception(message)
        self.save_logs_to_memcached(message)