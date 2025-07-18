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
        all_equations = {}

        # Definir os ambientes de equação que queremos buscar
        # E indicar se eles podem ter múltiplas linhas (usando \\)
        equation_environments = [
            ("equation", "equation", False),    # Normalmente uma linha
            ("equation*", "equation*", False),  # Normalmente uma linha
            ("eqnarray", "eqnarray", True),     # Múltiplas linhas
            ("eqnarray*", "eqnarray*", True),   # Múltiplas linhas
            ("align", "align", True),           # Múltiplas linhas
            ("align*", "align*", True),         # Múltiplas linhas
        ]

        for tex_file in tex_files:
            file_equations = []
            try:
                with open(tex_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for begin_env, end_env, is_multiline in equation_environments:
                    eqs_found_raw = self._find_equations_by_environment(content, begin_env, end_env)

                    for eq_content_raw in eqs_found_raw:
                        if is_multiline:
                            # Se for um ambiente de múltiplas linhas, faça o split
                            # O re.split é mais robusto que .split() para lidar com espaços/quebras de linha
                            # Ele divide por '\\' e remove strings vazias
                            lines = [line.strip() for line in re.split(r'\\\\\s*', eq_content_raw) if line.strip()]
                            file_equations.extend(lines)
                        else:
                            # Para ambientes de linha única, apenas adicione o conteúdo
                            file_equations.append(eq_content_raw.strip())

            except Exception as e:
                print(f"Erro ao ler ou processar o arquivo '{tex_file}': {e}")
                continue

            file_name = os.path.basename(tex_file)
            all_equations[file_name] = file_equations

        return all_equations
    
    def _find_equations_by_environment(self, content, begin_env, end_env):
        # Escapando caracteres especiais na string do ambiente para a regex
        escaped_begin = re.escape(f"\\begin{{{begin_env}}}")
        escaped_end = re.escape(f"\\end{{{end_env}}}")

        # Construindo a regex com os ambientes escapados
        # O padrão (.*?) captura o conteúdo não-guloso entre os delimitadores
        # re.DOTALL permite que o '.' case com quebras de linha
        pattern = rf'{escaped_begin}(.*?){escaped_end}'
        return re.findall(pattern, content, re.DOTALL)