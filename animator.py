import os
import subprocess
import datetime
import sys
import json
import shutil

class Animator:
    def __init__(self):
        print("Animator inicializado.")

        self.generated_scene_files = {}

    def _build_temp_manim_scene(self, template_dir="templates", template_name="scene_template.py"):
        """
        Cria um arquivo de cena Manim temporário a partir de um template.

        Args:
            template_dir (str): Diretório do template.
            template_name (str): Nome do arquivo de template.

        Returns:
            str: Caminho completo para o arquivo temporário criado, ou None em caso de erro.
        """
        template_full_path = os.path.join(template_dir, template_name)
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        print(f"  Pasta de arquivos temporários '{temp_dir}/' garantida.")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_scene_file_name = f"temp_scene_{timestamp}.py"
        temp_scene_full_path = os.path.join(temp_dir, temp_scene_file_name)

        try:
            shutil.copyfile(template_full_path, temp_scene_full_path)
            print(f"  Template '{template_full_path}' copiado para '{temp_scene_full_path}'.")
            return temp_scene_full_path
        except FileNotFoundError:
            print(f"Erro: Arquivo de template '{template_full_path}' não encontrado.")
            print("  Certifique-se de que a pasta 'templates' e o arquivo 'scene_template.py' existem.")
            return None
        except Exception as e:
            print(f"Erro ao copiar o arquivo de template: {e}")
            return None
        
    def _inject_content_into_scene_file(self, scene_file_path, equation_id, equation_lines, setup_data=None):
        """
        Injeta o conteúdo específico da animação (equação e setup) no arquivo de cena Manim.

        Args:
            scene_file_path (str): Caminho para o arquivo de cena Manim temporário.
            equation_id (str): O ID único do bloco da equação.
            equation_lines (list): Lista de strings das linhas da equação LaTeX.
            setup_data (dict, optional): Dicionário com os dados de setup da animação.
        """
        try:
            with open(scene_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Converte a lista de linhas da equação em uma string LaTeX para o Manim
            manim_latex_string = "\\n".join(equation_lines)

            # Injeta o código de animação no template, dependendo do tipo de cena
            if equation_id == "hello_manim_test_id":
                animation_code = f"""
        hello_text = Text("{manim_latex_string.replace('"', '\\"')}", color=WHITE).scale(1.5)
        self.play(Write(hello_text))
        self.wait(1.5)
"""
                # Renomeia a classe para HelloManimScene para o teste
                content = content.replace("class GeneratedScene(Scene):", "class HelloManimScene(Scene):")
            else:
                animation_code = f"""
        # Conteúdo da equação com ID: {equation_id}
        # {manim_latex_string.replace('"', '\\"')}
        # self.add(MathTex(r"{manim_latex_string.replace('"', '\\"')}"))
        # self.wait(1)
        pass
"""

            # Substitui o placeholder pelo código de animação gerado
            placeholder_string = "# --- INICIO_BLOCO_DE_ANIMACAO_DO_MANIM ---\n        # --- FIM_BLOCO_DE_ANIMACAO_DO_MANIM ---"
            if placeholder_string not in content:
                print(f"Erro: Placeholder '{placeholder_string}' não encontrado no template da cena.")
                return False

            content = content.replace(placeholder_string, animation_code)

            with open(scene_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Conteúdo injetado no arquivo de cena: {scene_file_path}")
            return True

        except Exception as e:
            print(f"Erro ao injetar conteúdo no arquivo de cena '{scene_file_path}': {e}")
            return False

    def build_scenes_from_equations(self, equations_data_from_reader):
        """
        Cria um arquivo de cena Manim temporário para cada bloco de equação recebido do Reader.

        Args:
            equations_data_from_reader (dict): Dicionário de equações retornado pelo Reader.

        Returns:
            dict: Dicionário onde a chave é o ID do bloco da equação e o valor é o caminho do arquivo de cena gerado.
        """
        if not isinstance(equations_data_from_reader, dict):
            print("Erro: 'equations_data_from_reader' deve ser um dicionário.")
            return {}
        if not equations_data_from_reader:
            print("Aviso: Dicionário de equações vazio. Nenhuma cena será gerada.")
            return {}

        self.generated_scene_files = {}
        print("\n--- Iniciando a construção de cenas Manim a partir das equações ---")

        all_temp_scene_paths = {}
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        print(f"  Pasta de arquivos temporários '{temp_dir}/' garantida.")

        for eq_id, _ in equations_data_from_reader.items():
            # Gera nome de arquivo seguro e único para cada cena
            safe_eq_id = eq_id.replace('.', '_').replace('-', '_').replace(':', '_')
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_scene_file_name = f"scene_{safe_eq_id}_{timestamp}.py"
            temp_scene_full_path = os.path.join(temp_dir, temp_scene_file_name)
            template_full_path = os.path.join("templates", "scene_template.py")

            try:
                shutil.copyfile(template_full_path, temp_scene_full_path)
                print(f"  Template para '{eq_id}' copiado para '{temp_scene_full_path}'.")
                all_temp_scene_paths[eq_id] = temp_scene_full_path
            except FileNotFoundError:
                print(f"Erro: Arquivo de template '{template_full_path}' não encontrado. Não foi possível criar cena para '{eq_id}'.")
                continue
            except Exception as e:
                print(f"Erro ao copiar template para '{eq_id}': {e}")
                continue

        print(f"Total de {len(all_temp_scene_paths)} arquivos de cena temporários criados.")
        return all_temp_scene_paths

    def render_manim_file(self, manim_file_path, output_dir="rendered_manim_files"):
            """
            Renderiza diretamente um arquivo de cena Manim (.py) existente.

            Args:
                manim_file_path (str): O caminho para o arquivo .py da cena Manim a ser renderizada.
                output_dir (str): Diretório onde o vídeo de saída será salvo.
            """
            print(f"\n--- Iniciando teste: Renderizando arquivo Manim '{manim_file_path}' ---")

            if not os.path.exists(manim_file_path):
                print(f"Erro: Arquivo Manim '{manim_file_path}' não encontrado.")
                return
            if not os.path.isfile(manim_file_path):
                print(f"Erro: '{manim_file_path}' não é um arquivo válido.")
                return
            if not manim_file_path.endswith('.py'):
                print(f"Erro: '{manim_file_path}' não é um arquivo Python válido (.py).")
                return

            os.makedirs(output_dir, exist_ok=True)
            print(f"Vídeo de saída será salvo em: {output_dir}")

            # Extrair o nome da classe da cena do arquivo Manim
            # Para um teste simples, vamos assumir que a primeira classe Scene encontrada é a que queremos.
            # Em um cenário real, você teria que saber o nome da classe ou parsear o arquivo.
            # No seu manim_scene_template.py, a classe é 'HelloManimScene'.
            scene_class_name = "HelloManimScene" # Hardcoded para o seu manim_scene_template.py de teste

            # Gerar um nome de arquivo de saída único com timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # O nome do vídeo será baseado no nome do arquivo Manim original
            base_file_name = os.path.splitext(os.path.basename(manim_file_path))[0]
            output_file_name_base = f"{base_file_name}_{timestamp}"

            # Preparar o comando Manim para execução via subprocess
            manim_command = [
                sys.executable, "-m", "manim",
                manim_file_path,        # Passa o caminho direto para o arquivo Manim
                scene_class_name,       # Nome da classe da cena
                "--media_dir", os.path.join(os.getcwd(), output_dir),
                "-o", output_file_name_base,
                "-ql",
                "--disable_caching",
                "--write_all",
                "--verbosity", "DEBUG", # Mantenha o DEBUG para ver logs detalhados
            ]

            print(f"\n  Executando comando Manim: {' '.join(manim_command)}")

            try:
                result = subprocess.run(manim_command, capture_output=True, text=True, check=True)

                print("\n--- Saída do Manim (stdout) ---")
                print(result.stdout)
                if result.stderr:
                    print("\n--- Saída do Manim (stderr) ---")
                    print(result.stderr)

                print(f"\nComando Manim executado com sucesso! Código de saída: {result.returncode}")
                print(f"Verifique o vídeo em: {os.path.join(output_dir, 'videos', base_file_name, '480p15', f'{output_file_name_base}.mp4')}")
                
            except subprocess.CalledProcessError as e:
                print(f"\nErro ao renderizar a animação (Manim falhou): {e}")
                print("  Saída do Manim (stdout):\n", e.stdout)
                print("  Saída do Manim (stderr):\n", e.stderr)
            except FileNotFoundError:
                print("\nErro: O comando 'manim' (ou 'python') não foi encontrado.")
                print("  Certifique-se de que o Manim CLI e o Python estão acessíveis no PATH do seu ambiente virtual.")
            except Exception as e:
                print(f"\nUm erro inesperado ocorreu: {e}")

            print("\n--- Teste de Renderização de Arquivo Manim Concluído ---")