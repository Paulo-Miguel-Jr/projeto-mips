# main.py

# Programa principal. Le o arquivo JSON de entrada com o codigo em
# linguagem de maquina (hexadecimal, 32 bits por instrucao), usa o
# modulo mips_decoder para traduzir cada instrucao e grava o
# resultado em um arquivo JSON de saida.

import json
import sys

from pathlib import Path

from mips_decoder import decode_instruction

BASE_DIR = Path(__file__).resolve().parent

def carregar_entrada(caminho):
    """
    Le o arquivo JSON de entrada e devolve o dicionario completo.
    """
    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def salvar_saida(caminho, conteudo):
    """
    Grava o dicionario de saida em formato JSON.
    """

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(conteudo, arquivo, indent=4, ensure_ascii=False)


def decodificar(instrucoes):
    """
    Decodifica a lista de instrucoes preservando a ordem do arquivo
    de entrada. Retorna uma tupla com a lista de instrucoes em assembly e a lista
    """

    assembly = []
    erros = []

    for posicao, hexadecimal in enumerate(instrucoes):

        try:
            assembly.append(decode_instruction(hexadecimal))

        except ValueError as erro:

            assembly.append(None)

            erros.append({
                "indice": posicao,
                "instrucao": hexadecimal,
                "erro": str(erro)
            })

    return assembly, erros


def main():
    """
    Fluxo principal: le a entrada, decodifica, grava a saida e
    exibe um resumo no console para conferencia.
    """

    if len(sys.argv) > 1:
        arquivo_entrada = Path(sys.argv[1])
    else:
        arquivo_entrada = BASE_DIR / "entrada.json"

    if len(sys.argv) > 2:
        arquivo_saida = Path(sys.argv[2])
    else:
        arquivo_saida = BASE_DIR / "saida.json"

    entrada = carregar_entrada(arquivo_entrada)

    instrucoes = entrada.get("text", [])

    assembly, erros = decodificar(instrucoes)

    saida = {
        "config": entrada.get("config", {"regs": {}, "mem": {}}),
        "data": entrada.get("data", {}),
        "text": assembly
    }

    if erros:
        saida["erros"] = erros

    salvar_saida(arquivo_saida, saida)

    print(f"Entrada: {arquivo_entrada}")
    print(f"Saida:   {arquivo_saida}")
    print()

    for hexadecimal, linha in zip(instrucoes, assembly):
        print(f"{hexadecimal} -> {linha if linha else 'ERRO'}")

    if erros:
        print()
        print(f"{len(erros)} instrucao(oes) nao reconhecida(s).")


if __name__ == "__main__":
    main()