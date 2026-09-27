# main.py

# Programa principal. Le o arquivo JSON de entrada com o codigo em
# linguagem de maquina (hexadecimal, 32 bits por instrucao), usa o
# modulo mips_decoder para traduzir cada instrucao e grava o
# resultado em um arquivo JSON de saida.

# main.py

import json

from mips_decoder import (
    decode_instruction,
    instruction_to_assembly
)

from cpu import MIPSCpu


def carregar_entrada(nome_arquivo):

    with open(
        nome_arquivo,
        "r",
        encoding="utf-8"
    ) as arquivo:

        return json.load(arquivo)


def executar_programa(entrada):

    cpu = MIPSCpu()

    # =========================================================
    # CARREGAR CONFIGURAÇÃO INICIAL
    # =========================================================

    config = entrada.get("config", {})

    regs = config.get("regs", {})

    cpu.registers.load_registers(regs)

    # =========================================================
    # EXECUTAR INSTRUÇÕES
    # =========================================================

    resultados = []

    for hexadecimal in entrada.get("text", []):

        decoded = decode_instruction(hexadecimal)

        assembly = instruction_to_assembly(decoded)

        stdout = cpu.execute(decoded)

        # Uma instrução ocupa 4 bytes.
        cpu.registers.increment_pc()

        resultado = {
            "hex": hexadecimal,
            "text": assembly,
            "regs": cpu.get_register_state(),
            "mem": {},
            "stdout": stdout
        }

        resultados.append(resultado)

    return resultados


def main():

    entrada = carregar_entrada("entrada.json")

    resultados = executar_programa(entrada)

    with open(
        "saida.json",
        "w",
        encoding="utf-8"
    ) as arquivo:

        json.dump(
            resultados,
            arquivo,
            indent=4,
            ensure_ascii=False
        )

    print("Execução concluída.")
    print("Resultado salvo em saida.json")


if __name__ == "__main__":
    main()