# reader.py
import os

class Reader:
    def __init__(self):
        # O construtor pode ser simples por enquanto.
        # No futuro, talvez você queira inicializar configs aqui.
        pass

    def verify_path(self, caminho_do_diretorio):
        if not isinstance(caminho_do_diretorio, str):
            print("Erro: O caminho do diretório deve ser uma string.")
            exit(1)

        if not os.path.exists(caminho_do_diretorio):
            print(f"Erro: O diretório '{caminho_do_diretorio}' não existe.")
            exit(1)

        if not os.path.isdir(caminho_do_diretorio):
            print(f"Erro: '{caminho_do_diretorio}' não é um diretório válido.")
            exit(1)

        print(f"Sucesso: O diretório '{caminho_do_diretorio}' é válido e existe.")