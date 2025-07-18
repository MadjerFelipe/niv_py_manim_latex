# reader.py
import os

class Reader:
    def __init__(self):
        # O construtor pode ser simples por enquanto.
        # No futuro, talvez você queira inicializar configs aqui.
        pass

    def verify_path(self, caminho_do_diretorio):
        """
        Verifica se o caminho fornecido é um diretório existente.

        Args:
            caminho_do_diretorio (str): O caminho para o diretório a ser verificado.

        Returns:
            bool: True se o caminho for um diretório existente, False caso contrário.
            str: Uma mensagem informativa sobre o resultado da validação.
        """
        if not isinstance(caminho_do_diretorio, str):
            return False, "Erro: O caminho do diretório deve ser uma string."

        if not os.path.exists(caminho_do_diretorio):
            return False, f"Erro: O diretório '{caminho_do_diretorio}' não existe."

        if not os.path.isdir(caminho_do_diretorio):
            return False, f"Erro: '{caminho_do_diretorio}' não é um diretório válido."

        return True, f"Sucesso: O diretório '{caminho_do_diretorio}' é válido e existe."