# main.py

import json

from mips_decoder import decode_instruction


def carregar_entrada(nome_arquivo):

    with open(nome_arquivo, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)


def main():

    entrada = carregar_entrada("entrada.json")

    instrucoes = entrada.get("text", [])

    print("Instruções encontradas:")
    print()

    for hexadecimal in instrucoes:

        try:
            assembly = decode_instruction(hexadecimal)

            print(f"{hexadecimal} -> {assembly}")

        except ValueError as erro:

            print(f"{hexadecimal} -> ERRO: {erro}")


if __name__ == "__main__":
    main()