# main.py
from reader import Reader
import os
import re

if __name__ == "__main__":
    # Definindo o diretório de teste diretamente
    path = "C:/Users/Madjer/Documents/Nivelamento/2025/Seringueiros/PC/Apostilas/PC_Álgebra"

    print(f"Verificando o diretório: {path}")
    print("-" * 30)

    # Instanciando a classe Reader e verificando o diretório
    leitor = Reader()
    files = leitor.get_tex_files(path)

    eqs = leitor.find_equations_in_files(files)

    print("-" * 30)
    print("Programa principal finalizado (neste ponto).")

    print(eqs)
