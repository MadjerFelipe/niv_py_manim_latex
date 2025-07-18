# reader.py
import os
import re

class Reader:
    def __init__(self):
        pass  # Construtor simples; pode ser expandido futuramente para configurações

    def verify_path(self, caminho_do_diretorio):
        # Normaliza o caminho para o formato do sistema operacional
        caminho_do_diretorio = os.path.normpath(caminho_do_diretorio.replace('\\', '/'))

        # Verifica se o caminho é uma string
        if not isinstance(caminho_do_diretorio, str):
            print("Erro: O caminho do diretório deve ser uma string.")
            exit(1)

        # Verifica se o caminho existe
        if not os.path.exists(caminho_do_diretorio):
            print(f"Erro: O diretório '{caminho_do_diretorio}' não existe.")
            exit(1)

        # Verifica se o caminho é um diretório
        if not os.path.isdir(caminho_do_diretorio):
            print(f"Erro: '{caminho_do_diretorio}' não é um diretório válido.")
            exit(1)

        print(f"Sucesso: O diretório '{caminho_do_diretorio}' é válido e existe.")

    def get_tex_files(self, caminho_do_diretorio):
        self.verify_path(caminho_do_diretorio)
        tex_files = []
        # Lista todos os arquivos .tex no diretório fornecido
        for file in os.listdir(caminho_do_diretorio):
            if file.endswith('.tex'):
                tex_files.append(os.path.join(caminho_do_diretorio, file))
        if not tex_files:
            print(f"Erro: Nenhum arquivo .tex encontrado no diretório '{caminho_do_diretorio}'.")
            exit(1)
        return tex_files

    def find_equations_in_files(self, tex_files):
        all_equations = {}
        equation_block_counter = 0

        # Define os ambientes de equação e se eles suportam múltiplas linhas
        equation_environments = [
            ("equation", "equation", False),
            ("equation*", "equation*", False),
            ("eqnarray", "eqnarray", True),
            ("eqnarray*", "eqnarray*", True),
            ("align", "align", True),
            ("align*", "align*", True),
            # Adicione outros ambientes que comportem múltiplas linhas se necessário, ex: ("gather", "gather", True)
        ]

        for tex_file in tex_files:
            file_name = os.path.basename(tex_file)
            try:
                with open(tex_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for begin_env, end_env, is_multiline in equation_environments:
                    eqs_found_raw = self._find_equations_by_environment(content, begin_env, end_env)

                    for eq_content_raw in eqs_found_raw:
                        # Cria um ID único para cada bloco de equação
                        equation_id = f"{file_name}_block_{equation_block_counter}"

                        # Processa o conteúdo dependendo se é multilinha ou não
                        if is_multiline:
                            # Divide em linhas se o ambiente for multilinha
                            lines = [line.strip() for line in re.split(r'\\\\\s*', eq_content_raw) if line.strip()]
                            all_equations[equation_id] = lines
                        else:
                            # Salva como uma lista com uma única string para ambientes de linha única
                            all_equations[equation_id] = [eq_content_raw.strip()]

                        equation_block_counter += 1

            except Exception as e:
                print(f"Erro ao ler ou processar o arquivo '{tex_file}': {e}")
                continue

        return all_equations
    
    def _find_equations_by_environment(self, content, begin_env, end_env):
        # Monta a expressão regular para capturar o conteúdo entre \begin e \end do ambiente
        escaped_begin = re.escape(f"\\begin{{{begin_env}}}")
        escaped_end = re.escape(f"\\end{{{end_env}}}")
        pattern = rf'{escaped_begin}(.*?){escaped_end}'
        return re.findall(pattern, content, re.DOTALL)
