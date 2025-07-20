import os
import subprocess
import datetime
import sys
import json
import shutil

class Animator:
    def __init__(self):
        print("Animator inicializado.")

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