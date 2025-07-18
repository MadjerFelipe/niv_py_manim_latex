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

        equation_environments = [
            ("equation", "equation"),
            ("equation*", "equation*"),
            ("eqnarray", "eqnarray"),
            ("eqnarray*", "eqnarray*"),
            ("align", "align"),
            ("align*", "align*"),
        ]

        for tex_file in tex_files:
            file_equations = []
            try:
                with open(tex_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                for begin_env, end_env in equation_environments:
                    eqs_found = self._find_equations_by_environment(content, begin_env, end_env)
                    for eq in eqs_found:
                        # Opcional: Você pode adicionar metadados aqui,
                        # como o tipo de ambiente de onde a equação veio.
                        # Por simplicidade, estamos adicionando apenas a string da equação.
                        file_equations.append(eq.strip()) # .strip() para limpar espaços em branco

            except Exception as e:
                print(f"Erro ao ler ou processar o arquivo '{tex_file}': {e}")
                # Continua para o próximo arquivo mesmo com erro
                continue

            file_name = os.path.basename(tex_file)
            all_equations[file_name] = file_equations

        return all_equations
    
    def _find_equations_by_environment(self, content, begin_env, end_env):
        """
        Função auxiliar para encontrar equações dentro de um ambiente LaTeX específico.

        Args:
            content (str): O conteúdo completo do arquivo LaTeX.
            begin_env (str): A string de início do ambiente (ex: 'equation', 'align').
            end_env (str): A string de fim do ambiente (ex: 'equation', 'align').

        Returns:
            list: Uma lista de strings, onde cada string é o conteúdo de uma equação
                encontrada dentro do ambiente especificado.
        """
        # Escapando caracteres especiais na string do ambiente para a regex
        escaped_begin = re.escape(f"\\begin{{{begin_env}}}")
        escaped_end = re.escape(f"\\end{{{end_env}}}")

        # Construindo a regex com os ambientes escapados
        # O padrão (.*?) captura o conteúdo não-guloso entre os delimitadores
        # re.DOTALL permite que o '.' case com quebras de linha
        pattern = rf'{escaped_begin}(.*?){escaped_end}'
        return re.findall(pattern, content, re.DOTALL)