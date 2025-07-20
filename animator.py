# animator.py
import os
import subprocess
import json
import datetime
import sys # Necessário para sys.executable

class Animator:
    def __init__(self):
        """
        Inicializa o Animator. Não recebe parâmetros no construtor nesta versão simplificada.
        """
        print("Animator inicializado (versão de teste simplificada).")

    def test_hello_manim(self, output_dir="test_hello_manim_animations"):
        """
        Gera uma animação simples "Hello Manim" para verificar a funcionalidade básica.

        Args:
            output_dir (str): Diretório onde o vídeo de saída será salvo.
        """
        print(f"\n--- Iniciando teste: Gerando animação 'Hello Manim' ---")
        
        # Garante que o diretório de saída exista
        os.makedirs(output_dir, exist_ok=True)
        print(f"Vídeo de saída será salvo em: {output_dir}")

        # Gerar um nome de arquivo de saída único com timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name_base = f"hello_manim_{timestamp}"

        # 1. Conteúdo da cena Manim "Hello Manim"
        manim_scene_content = f"""
from manim import Scene, Text, Write, WHITE

class HelloManimScene(Scene):
    def construct(self):
        # Cria um objeto de texto "Hello Manim!"
        hello_text = Text("Hello Manim!", color=WHITE).scale(1.5)

        # Anima a escrita do texto na tela
        self.play(Write(hello_text))

        # Espera por um tempo
        self.wait(1.5)
"""
        
        # 2. Escrever o conteúdo da cena em um arquivo temporário
        temp_scene_file = "temp_hello_manim_scene.py"
        with open(temp_scene_file, 'w', encoding='utf-8') as f:
            f.write(manim_scene_content)
        print(f"  Cena Manim temporária '{temp_scene_file}' criada.")

        # 3. Preparar o comando Manim para execução via subprocess
        manim_command = [
            sys.executable, "-m", "manim",
            temp_scene_file,
            "HelloManimScene",  # Nome da classe da cena dentro do arquivo temporário
            "--media_dir", os.path.join(os.getcwd(), output_dir), # Diretório raiz para a saída do Manim
            "-o", output_file_name_base, # Nome do arquivo de saída (sem extensão .mp4)
            "-ql",               # Qualidade baixa (para renderização rápida)
            "--disable_caching", # Garante que o Manim renderize a cada execução
            "--write_all",       # Garante que o método construct seja executado
        ]

        print(f"\n  Executando comando Manim: {' '.join(manim_command)}")

        try:
            # Executar o comando Manim
            result = subprocess.run(manim_command, capture_output=True, text=True, check=True)

            print("\n--- Saída do Manim (stdout) ---")
            print(result.stdout)
            if result.stderr:
                print("\n--- Saída do Manim (stderr) ---")
                print(result.stderr)

            print(f"\nComando Manim executado com sucesso! Código de saída: {result.returncode}")
            print(f"Verifique o vídeo em: {os.path.join(output_dir, 'videos', 'temp_hello_manim_scene', '480p15', f'{output_file_name_base}.mp4')}")
            
        except subprocess.CalledProcessError as e:
            print(f"\nErro ao renderizar a animação (Manim falhou): {e}")
            print("  Saída do Manim (stdout):\n", e.stdout)
            print("  Saída do Manim (stderr):\n", e.stderr)
        except FileNotFoundError:
            print("\nErro: O comando 'manim' (ou 'python') não foi encontrado.")
            print("  Certifique-se de que o Manim CLI e o Python estão acessíveis no PATH do seu ambiente virtual.")
        except Exception as e:
            print(f"\nUm erro inesperado ocorreu: {e}")
        finally:
            # Limpar o arquivo temporário da cena
            if os.path.exists(temp_scene_file):
                os.remove(temp_scene_file)
                print(f"  Arquivo temporário '{temp_scene_file}' removido.")

        print("\n--- Teste 'Hello Manim' Concluído ---")