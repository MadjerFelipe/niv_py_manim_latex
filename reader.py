# reader.py
import os
import re

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

    def get_tex_files(self, caminho_do_diretorio):
        self.verify_path(caminho_do_diretorio)
        tex_files = []
        for file in os.listdir(caminho_do_diretorio):
            if file.endswith('.tex'):
                tex_files.append(os.path.join(caminho_do_diretorio, file))
        if not tex_files:
            print(f"Erro: Nenhum arquivo .tex encontrado no diretório '{caminho_do_diretorio}'.")
            exit(1)
        return tex_files

    def find_equations_in_files(self, tex_files):
        equations = {}
        for tex_file in tex_files:
            with open(tex_file, 'r', encoding='utf-8') as f:
                content = f.read()
            # Find equations between \begin{equation}...\end{equation}
            eqs = re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}', content, re.DOTALL)
            equations[tex_file] = eqs
        return equations