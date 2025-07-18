# main.py
from reader import Reader
import os

if __name__ == "__main__":
    # --- Definindo o diretório de teste diretamente aqui ---
    # Madjer, lembre-se de que este diretório deve existir para o teste!
    # Se ainda não o fez, crie uma pasta chamada 'meu_projeto_latex' no mesmo local de main.py
    path = "C:/Users/Madjer/Documents/Nivelamento/2025/Seringueiros/PC/Apostilas/PC_Álgebra"

    print(f"Verificando o diretório: {path}")
    print("-" * 30)

    # --- Usando a classe Reader para validar o diretório ---
    leitor = Reader()
    exist, mensagem = leitor.verify_path(path)

    if not exist:
        print(f"Erro: {mensagem}")
        print("Por favor, verifique se o diretório configurado existe.")
        # Se o diretório não for válido, o programa deve parar.
        exit(1) # Código de saída 1 indica erro
    else:
        print(f"Sucesso: {mensagem}")
        print("Continuando com o processamento das equações...")
        # A partir daqui, você chamaria as próximas etapas do seu projeto
        # (por exemplo, ler equações, interagir com o Designer, etc.)

    print("-" * 30)
    print("Programa principal finalizado (neste ponto).")