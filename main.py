from reader import Reader
from designer import Designer
from animator import Animator
import sys
import os
import re

if __name__ == "__main__":
    # Defina o caminho do projeto LaTeX a ser processado
    caminho_do_projeto_latex = r"C:\Users\Madjer\Documents\Nivelamento\2026\manim_py"

    print(f"--- Iniciando processamento para o diretório: {caminho_do_projeto_latex} ---")
    print("-" * 30)

    # FASE 1: Leitura dos arquivos .tex e extração das equações
    leitor = Reader()
    leitor.verify_path(caminho_do_projeto_latex)
    tex_files_encontrados = leitor.get_tex_files(caminho_do_projeto_latex)
    equacoes_encontradas = leitor.find_equations_in_files(tex_files_encontrados)

    print("\n--- Equações Encontradas pelo Reader: ---")
    if not equacoes_encontradas:
        print("Nenhuma equação encontrada. Encerrando o Designer e Animator.")
    else:
        for eq_id, eq_lines_list in equacoes_encontradas.items():
            print(f"  ID: {eq_id}")
            print(f"  Conteúdo: {eq_lines_list}")
        print("-" * 30)

        # FASE 2: Geração dos setups de animação padrão para cada equação
        print("\n--- Iniciando o Designer para criar setups padrão ---")
        projetista = Designer()
        setups_animacao_padrao = projetista.set_deafult_anim(equacoes_encontradas)

        print("\n--- Setups de Animação Padrão Gerados: ---")
        if setups_animacao_padrao:
            for eq_id, setup in setups_animacao_padrao.items():
                print(f"  ID: {eq_id}")
                for key, value in setup.items():
                    display_value = value
                    if isinstance(value, list) and len(value) > 3:
                        display_value = f"{value[:3]}... ({len(value)} itens)"
                    print(f"    {key}: {display_value}")
                print("  --------------------")
        else:
            print("Nenhum setup de animação padrão foi gerado. Encerrando Animator.")
            exit(0)
        print("-" * 30)

        # FASE 3: Renderização das animações usando o Animator
        print("\n--- Iniciando o Animator para renderizar as animações ---")

        # IDs dos blocos a serem animados (aqui, todos encontrados)
        blocks_to_animate = list(equacoes_encontradas.keys())

        if not blocks_to_animate:
            print("Nenhum bloco para animar. Encerrando.")
            exit(0)

        animador = Animator()
        #animador.test_hello_manim(output_dir="minhas_animacoes_de_teste")
        # Define o caminho para o seu arquivo de cena Manim de teste (o prefab)
        manim_file_to_test = "manim_scene_template.py"
        
        # Define o diretório onde o vídeo será salvo
        output_test_dir = "direto_do_manim_template"
        
        # Chama a nova função para renderizar o arquivo Manim
        animador.render_manim_file(manim_file_to_test, output_test_dir)

    print("\n--- Processamento concluído ---")
