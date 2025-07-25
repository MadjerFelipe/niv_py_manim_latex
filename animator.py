import os
import subprocess
import datetime
import sys
import json
import shutil

class Animator:
    def __init__(self):
        print("Animator inicializado.")
        # Dicionários para manter o controle dos arquivos e dados
        self.generated_scene_files = {} # {eq_id: path_to_temp_scene.py}
        self.temp_json_data_file = None # Path para o arquivo JSON global de dados
        self.equations_data = {}        # Dados das equações do Reader (para uso interno)
        self.animation_setups = {}      # Setups do Designer (para uso interno)

    def _build_temp_scenes(self, equations_data_from_reader, template_dir="templates", template_name="scene_template.py"):
        """
        Cria cópias do template de cena Manim para cada bloco de equação.

        Args:
            equations_data_from_reader (dict): Dicionário de equações do Reader.
            template_dir (str): Diretório onde o template está localizado.
            template_name (str): Nome do arquivo de template.

        Returns:
            dict: Um dicionário onde a chave é o ID do bloco da equação e o valor
                  é o caminho completo para o arquivo de cena Manim temporário criado.
        """
        self.generated_scene_files = {} # Resetar para cada nova chamada
        
        temp_dir = "temp"
        os.makedirs(temp_dir, exist_ok=True)
        print(f"  Pasta de arquivos temporários '{temp_dir}/' garantida.")
        
        template_full_path = os.path.join(template_dir, template_name)
        if not os.path.exists(template_full_path):
            print(f"Erro: Arquivo de template '{template_full_path}' não encontrado. Nenhuma cena será criada.")
            return {}

        print("\n--- Construindo arquivos de cena Manim temporários a partir das equações ---")
        
        for eq_id, _ in equations_data_from_reader.items():
            # Gerar nome de arquivo seguro e único para cada cena
            safe_eq_id = eq_id.replace('.', '_').replace('-', '_').replace(':', '_').replace(' ', '_')
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            temp_scene_file_name = f"scene_{safe_eq_id}_{timestamp}.py"
            temp_scene_full_path = os.path.join(temp_dir, temp_scene_file_name)

            try:
                shutil.copyfile(template_full_path, temp_scene_full_path)
                print(f"  Template para '{eq_id}' copiado para '{temp_scene_full_path}'.")
                self.generated_scene_files[eq_id] = temp_scene_full_path
            except Exception as e:
                print(f"Erro ao copiar template para '{eq_id}': {e}")
                continue # Continua para a próxima equação mesmo com erro

        print(f"Total de {len(self.generated_scene_files)} arquivos de cena temporários criados.")
        return self.generated_scene_files # Retorna os caminhos dos arquivos criados

    def _inject_content(self, scene_file_path, eq_id, equations_data, animation_setups, temp_json_data_file):
        """
        Injeta o conteúdo LaTeX da equação e os dados de setup no arquivo de cena Manim temporário.

        Args:
            scene_file_path (str): Caminho para o arquivo de cena Manim temporário.
            eq_id (str): O ID único do bloco da equação a ser injetado.
            equations_data (dict): Dicionário completo de equações do Reader.
            animation_setups (dict): Dicionário completo de setups de animação do Designer.
            temp_json_data_file (str): Caminho para o arquivo JSON global de dados.
        Returns:
            bool: True se a injeção foi bem-sucedida, False caso contrário.
        """
        try:
            with open(scene_file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # --- Injetar caminho do JSON de dados ---
            json_data_filename_in_scene = repr(os.path.basename(temp_json_data_file))
            content = content.replace(
                "MANIM_DATA_FILE_PLACEHOLDER_FILLED", json_data_filename_in_scene
            )

            # --- Gerar e injetar lógica de animação para o bloco específico ---
            # Esta lógica usará o 'eq_id' para buscar os dados de 'equations_data' e 'animation_setups'
            # dentro da cena Manim, que por sua vez lerá do JSON global.
            
            animation_logic_for_block = f"""
        # Lógica de animação para o bloco: {eq_id}
        current_block_id = "{eq_id}"
        
        if current_block_id in equations_data and current_block_id in animation_setups:
            eq_lines = equations_data[current_block_id]
            setup = animation_setups[current_block_id]

            print(f"  Animando bloco na cena: {{current_block_id}}")
            
            manim_latex_string = "\\n".join(eq_lines)
            
            math_tex_obj = MathTex(
                manim_latex_string,
                color=setup.get("color", WHITE)
            ).scale(setup.get("scale", 1.0))

            position = setup.get("position")
            if position:
                if isinstance(position, list) and len(position) == 3:
                     math_tex_obj.move_to(position)
                else:
                     print(f"Aviso: Posição inválida para {{current_block_id}}: {{position}}. Usando padrão.")


            self.wait(setup.get("delay_before", 0.5))

            animation_type = setup.get("animation_type", "Write")
            duration = setup.get("duration", 1.5)

            if animation_type == "Write":
                self.play(Write(math_tex_obj, run_time=duration))
            elif animation_type == "FadeIn":
                self.play(FadeIn(math_tex_obj, run_time=duration))
            elif animation_type == "Create":
                self.play(Create(math_tex_obj, run_time=duration))
            elif animation_type == "Transform":
                print(f"Aviso: Tipo de animação '{{animation_type}}' requer lógica mais complexa. Usando Write.")
                self.play(Write(math_tex_obj, run_time=duration))
            else:
                print(f"Aviso: Tipo de animação '{{animation_type}}' não reconhecido. Usando Write.")
                self.play(Write(math_tex_obj, run_time=duration))

            self.wait(setup.get("delay_after", 1.0))

            if not setup.get("show_equation_after", True):
                self.play(FadeOut(math_tex_obj))
        else:
            print(f"Aviso: Bloco '{{current_block_id}}' não encontrado nos dados ou setups da cena. Nenhuma animação.")
        
        self.wait(1) # Espera final para esta cena individual
"""
            placeholder_string = "# --- INICIO_BLOCO_DE_ANIMACAO_DO_MANIM ---\n        # --- FIM_BLOCO_DE_ANIMACAO_DO_MANIM ---"
            if placeholder_string not in content:
                print(f"Erro: Placeholder '{placeholder_string}' não encontrado no template da cena para '{eq_id}'.")
                return False
                
            content = content.replace(placeholder_string, animation_logic_for_block)

            # --- Escrever o conteúdo modificado de volta no arquivo ---
            with open(scene_file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  Conteúdo injetado no arquivo de cena: {scene_file_path}")
            return True

        except Exception as e:
            print(f"Erro ao injetar conteúdo no arquivo de cena '{scene_file_path}' para '{eq_id}': {e}")
            return False

    def _populate_scenes(self):
        """
        Popula os arquivos de cena Manim temporários com o conteúdo e setups das equações.
        Assume que self.generated_scene_files já foi preenchido por _build_temp_scenes.
        """
        if not self.generated_scene_files:
            print("Aviso: Nenhum arquivo de cena temporário para popular.")
            return False
        if not self.equations_data or not self.animation_setups:
            print("Aviso: Dados de equações ou setups ausentes. Não é possível popular cenas.")
            return False
            
        print("\n--- Populando arquivos de cena Manim com conteúdo e setups ---")

        # Gerar o arquivo JSON de dados UMA VEZ para todos os blocos
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.temp_json_data_file = os.path.join("temp", f"manim_data_{timestamp}.json")
        
        data_to_pass = {
            "equations_data": self.equations_data,
            "animation_setups": self.animation_setups
        }
        with open(self.temp_json_data_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_pass, f, indent=4)
        print(f"  Dados globais de equações e setups salvos em: {self.temp_json_data_file}")


        successful_injections = 0
        for eq_id, scene_file_path in self.generated_scene_files.items():
            if self._inject_content(scene_file_path, eq_id, self.equations_data, self.animation_setups, self.temp_json_data_file):
                successful_injections += 1
            else:
                # Se a injeção falhar, remova o arquivo da lista de renderização
                print(f"  Falha ao injetar conteúdo em '{scene_file_path}'. Removendo da fila de renderização.")
                if os.path.exists(scene_file_path):
                    os.remove(scene_file_path)
                if eq_id in self.generated_scene_files:
                    del self.generated_scene_files[eq_id]
        
        print(f"Total de {successful_injections} arquivos de cena populados com sucesso.")
        return successful_injections > 0 # Retorna True se pelo menos um foi populado


    def _render_scene(self, scene_file_path, output_dir):
        """
        Renderiza um único arquivo de cena Manim temporário.
        Esta é a funcionalidade anteriormente em render_manim_file.
        """
        print(f"\n--- Renderizando cena: '{os.path.basename(scene_file_path)}' ---")

        # Extrair o nome da classe da cena (assumimos 'GeneratedScene' do template)
        scene_class_name = "GeneratedScene"
        
        # O nome do arquivo de saída base será o nome do arquivo da cena temporária
        base_file_name = os.path.splitext(os.path.basename(scene_file_path))[0]
        output_file_name_base = base_file_name

        manim_command = [
            sys.executable, "-m", "manim",
            scene_file_path,
            scene_class_name,
            "--media_dir", os.path.join(os.getcwd(), output_dir),
            "-o", output_file_name_base,
            "-ql",
            "--disable_caching",
            "--write_all",
            "--verbosity", "DEBUG",
        ]

        print(f"  Executando comando Manim: {' '.join(manim_command)}")

        try:
            result = subprocess.run(manim_command, capture_output=True, text=True, check=True)

            print("  Saída do Manim (stdout):\n", result.stdout)
            if result.stderr:
                print("  Saída do Manim (stderr):\n", result.stderr)

            print(f"  Comando Manim executado com sucesso! Código de saída: {result.returncode}")
            final_video_path = os.path.join(output_dir, 'videos', base_file_name, '480p15', f'{output_file_name_base}.mp4')
            print(f"  Verifique o vídeo em: {final_video_path}")
            return True # Retorna True para indicar sucesso
            
        except subprocess.CalledProcessError as e:
            print(f"  Erro ao renderizar a animação (Manim falhou): {e}")
            print("    Saída do Manim (stdout):\n", e.stdout)
            print("    Saída do Manim (stderr):\n", e.stderr)
            return False
        except FileNotFoundError:
            print("\n  Erro: O comando 'manim' (ou 'python') não foi encontrado.")
            print("    Certifique-se de que o Manim CLI e o Python estão acessíveis no PATH do seu ambiente virtual.")
            return False
        except Exception as e:
            print(f"  Um erro inesperado ocorreu: {e}")
            return False

    def _render_all_equations_(self, output_dir):
        """
        Itera sobre todos os arquivos de cena Manim gerados e os renderiza.
        """
        if not self.generated_scene_files:
            print("Nenhum arquivo de cena para renderizar. Certifique-se de que as cenas foram construídas e populadas.")
            return False

        print(f"\n--- Iniciando a renderização de {len(self.generated_scene_files)} cenas de equação ---")
        os.makedirs(output_dir, exist_ok=True) # Garante o diretório de saída principal
        
        successful_renders = 0
        for eq_id, scene_file_path in self.generated_scene_files.items():
            print(f"\n  Renderizando cena para o bloco: {eq_id}")
            if self._render_scene(scene_file_path, output_dir):
                successful_renders += 1
            
            # Limpar o arquivo de cena temporário após a renderização
            if os.path.exists(scene_file_path):
                os.remove(scene_file_path)
                print(f"  Arquivo de cena temporário '{scene_file_path}' removido.")
        
        print(f"\n--- Renderização de todas as cenas concluída. {successful_renders} de {len(self.generated_scene_files)} renderizadas com sucesso. ---")
        return successful_renders > 0

    def generate_all_scenes(self, equations_data_from_reader, animation_setups_from_designer, output_dir="generated_animations_final"):
        """
        Função principal para gerar e renderizar todas as cenas Manim.

        Args:
            equations_data_from_reader (dict): Dicionário de equações do Reader.
            animation_setups_from_designer (dict): Dicionário de setups de animação do Designer.
            output_dir (str): Diretório onde os vídeos finais serão salvos.
        """
        print("\n--- Orquestrando a geração e renderização de todas as cenas ---")

        # Armazenar os dados para que os métodos internos possam acessá-los
        self.equations_data = equations_data_from_reader
        self.animation_setups = animation_setups_from_designer

        # 1. Construir os arquivos de cena temporários (cópias do template)
        # O generated_scene_files será preenchido aqui
        if not self._build_temp_scenes(equations_data_from_reader):
            print("Falha na construção dos arquivos de cena temporários. Encerrando.")
            return

        # 2. Popular esses arquivos de cena com o conteúdo e setups (e gerar o JSON global de dados)
        if not self._populate_scenes():
            print("Falha ao popular os arquivos de cena. Encerrando.")
            # Limpar arquivos temporários se algo deu errado após a construção
            self._cleanup_temp_files()
            return
        
        # 3. Renderizar todas as cenas populadas
        if not self._render_all_equations_(output_dir):
            print("Nenhuma animação foi renderizada com sucesso.")
            # Limpar arquivos temporários restantes
            self._cleanup_temp_files()
            return
            
        print("\n--- Geração e Renderização de todas as cenas concluída com sucesso! ---")
        self._cleanup_temp_files() # Limpeza final

    def _cleanup_temp_files(self):
        """Limpa arquivos temporários (JSON e .py de cenas) após o processo."""
        # Limpa o arquivo JSON de dados globais
        if self.temp_json_data_file and os.path.exists(self.temp_json_data_file):
            os.remove(self.temp_json_data_file)
            print(f"Arquivo JSON de dados temporário '{self.temp_json_data_file}' removido.")
            self.temp_json_data_file = None # Reseta o path

        # Limpa todos os arquivos de cena temporários ainda presentes
        for eq_id, scene_file_path in list(self.generated_scene_files.items()): # Usar list() para evitar erro de RuntimeError ao deletar
            if os.path.exists(scene_file_path):
                os.remove(scene_file_path)
                print(f"Arquivo de cena temporário '{scene_file_path}' removido.")
            del self.generated_scene_files[eq_id] # Remove do controle
        
        # Opcional: Remover a pasta 'temp' se estiver vazia
        temp_dir = "temp"
        if os.path.exists(temp_dir) and not os.listdir(temp_dir):
            os.rmdir(temp_dir)
            print(f"Pasta temporária '{temp_dir}' removida.")

# --- Métodos de teste antigos (para referência, mas não parte do fluxo principal) ---
# Você pode removê-los se não precisar mais.
    def test_hello_manim_animation(self, output_dir="test_hello_manim_animations"):
        print(f"\n--- Iniciando teste: Gerando animação 'Hello Manim' usando prefab ---")
        
        os.makedirs(output_dir, exist_ok=True)
        print(f"Vídeo de saída será salvo em: {output_dir}")

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file_name_base = f"hello_manim_{timestamp}"

        temp_data_file = f"temp/manim_data_{timestamp}.json" # Ajustado para estar na pasta temp
        data_to_pass = {"equations_data": {}, "animation_setups": {}, "requested_block_ids": []}
        os.makedirs(os.path.dirname(temp_data_file), exist_ok=True) # Garante que a pasta temp exista
        with open(temp_data_file, 'w', encoding='utf-8') as f:
            json.dump(data_to_pass, f)
        print(f"  Dados temporários (vazios) salvos em: {temp_data_file}")

        template_file_path = "templates/scene_template.py"
        try:
            with open(template_file_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
        except FileNotFoundError:
            print(f"Erro: Arquivo de template Manim '{template_file_path}' não encontrado.")
            return

        json_data_filename_in_scene = repr(os.path.basename(temp_data_file))
        final_scene_content = template_content.replace(
            "MANIM_DATA_FILE_PLACEHOLDER_FILLED", json_data_filename_in_scene
        ).replace(
            "class GeneratedScene(Scene):",
            "class HelloManimScene(Scene):"
        )
        
        hello_manim_animation_logic = f"""
        hello_text = Text("Hello Manim!", color=WHITE).scale(1.5)
        self.play(Write(hello_text))
        self.wait(1.5)
"""
        placeholder_string = "# --- INICIO_BLOCO_DE_ANIMACAO_DO_MANIM ---\n        # --- FIM_BLOCO_DE_ANIMACAO_DO_MANIM ---"
        final_scene_content = final_scene_content.replace(placeholder_string, hello_manim_animation_logic)

        temp_scene_file = f"temp/temp_hello_manim_scene_{timestamp}.py" # Ajustado para estar na pasta temp
        os.makedirs(os.path.dirname(temp_scene_file), exist_ok=True) # Garante que a pasta temp exista
        with open(temp_scene_file, 'w', encoding='utf-8') as f:
            f.write(final_scene_content)
        print(f"  Cena Manim temporária '{temp_scene_file}' gerada a partir do template.")

        manim_command = [
            sys.executable, "-m", "manim",
            temp_scene_file,
            "HelloManimScene",
            "--media_dir", os.path.join(os.getcwd(), output_dir),
            "-o", output_file_name_base,
            "-ql",
            "--disable_caching",
            "--write_all",
            "--verbosity", "DEBUG",
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
            print(f"Verifique o vídeo em: {os.path.join(output_dir, 'videos', os.path.basename(temp_scene_file).replace('.py', ''), '480p15', f'{output_file_name_base}.mp4')}")
            
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
            if os.path.exists(temp_scene_file):
                os.remove(temp_scene_file)
                print(f"  Arquivo temporário '{temp_scene_file}' removido.")
            if os.path.exists(temp_data_file):
                os.remove(temp_data_file)
                print(f"  Arquivo temporário '{temp_data_file}' removido.")

        print("\n--- Teste 'Hello Manim' Concluído ---")


    def render_manim_file(self, manim_file_path, output_dir="rendered_manim_files"):
        """
        Renderiza diretamente um arquivo de cena Manim (.py) existente.

        Args:
            manim_file_path (str): O caminho para o arquivo .py da cena Manim a ser renderizada.
            output_dir (str): Diretório onde o vídeo de saída será salvo.
        """
        print(f"\n--- Renderizando arquivo Manim: '{manim_file_path}' ---")

        if not os.path.exists(manim_file_path):
            print(f"Erro: Arquivo Manim '{manim_file_path}' não encontrado.")
            return False
        if not os.path.isfile(manim_file_path):
            print(f"Erro: '{manim_file_path}' não é um arquivo válido.")
            return False
        if not manim_file_path.endswith('.py'):
            print(f"Erro: '{manim_file_path}' não é um arquivo Python válido (.py).")
            return False

        os.makedirs(output_dir, exist_ok=True)
        print(f"  Vídeo de saída será salvo em: {output_dir}")

        scene_class_name = "GeneratedScene" # Nome da classe no template

        base_file_name = os.path.splitext(os.path.basename(manim_file_path))[0]
        output_file_name_base = base_file_name

        manim_command = [
            sys.executable, "-m", "manim",
            manim_file_path,
            scene_class_name,
            "--media_dir", os.path.join(os.getcwd(), output_dir),
            "-o", output_file_name_base,
            "-ql",
            "--disable_caching",
            "--write_all",
            "--verbosity", "DEBUG",
        ]

        print(f"  Executando comando Manim: {' '.join(manim_command)}")

        try:
            result = subprocess.run(manim_command, capture_output=True, text=True, check=True)

            print("  Saída do Manim (stdout):\n", result.stdout)
            if result.stderr:
                print("  Saída do Manim (stderr):\n", result.stderr)

            print(f"  Comando Manim executado com sucesso! Código de saída: {result.returncode}")
            final_video_path = os.path.join(output_dir, 'videos', base_file_name, '480p15', f'{output_file_name_base}.mp4')
            print(f"  Verifique o vídeo em: {final_video_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"  Erro ao renderizar a animação (Manim falhou): {e}")
            print("    Saída do Manim (stdout):\n", e.stdout)
            print("    Saída do Manim (stderr):\n", e.stderr)
            return False
        except FileNotFoundError:
            print("\n  Erro: O comando 'manim' (ou 'python') não foi encontrado.")
            print("    Certifique-se de que o Manim CLI e o Python estão acessíveis no PATH do seu ambiente virtual.")
            return False
        except Exception as e:
            print(f"  Um erro inesperado ocorreu: {e}")
            return False