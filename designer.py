# designer.py
import os

class Designer:
    def __init__(self):
        # O dicionário de setup padrão será armazenado aqui
        self.anim_setups = {}

    def set_deafult_anim(self, equations_data_from_reader):

        if not isinstance(equations_data_from_reader, dict):
            print("Erro: O 'equations_data_from_reader' deve ser um dicionário.")
            return {}

        if not equations_data_from_reader:
            print("Aviso: O dicionário de equações do Reader está vazio. Nenhum setup será criado.")
            return {}

        print("Iniciando a criação de setups padrão para as equações...")
        
        for eq_id, eq_lines_list in equations_data_from_reader.items():
            # Definindo um setup padrão para cada bloco de equação
            default_setup = {
                "equation_latex_lines": eq_lines_list, # Mantém as linhas da equação original
                "animation_type": "Write",             # Tipo de animação padrão (ex: escrita)
                "color": "#FFFFFF",                    # Cor padrão (branco)
                "position": [0, 0, 0],                 # Posição padrão (centro da tela)
                "scale": 1.0,                          # Escala padrão
                "duration": len(eq_lines_list) * 1.5,  # Duração baseada no número de linhas
                "delay_before": 0.5,                   # Pequeno atraso antes de animar
                "delay_after": 1.0,                    # Atraso após a animação
                "show_equation_after": True,           # Manter a equação na tela após animar
            }
            self.anim_setups[eq_id] = default_setup
            print(f" - Setup padrão criado para: {eq_id}")

        print(f"Total de {len(self.anim_setups)} setups padrão criados.")
        return self.anim_setups