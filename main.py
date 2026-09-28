# main.py

# Programa principal. Le o arquivo JSON de entrada com o codigo em
# linguagem de maquina (hexadecimal, 32 bits por instrucao), usa o
# modulo mips_decoder para traduzir cada instrucao e grava o
# resultado em um arquivo JSON de saida.

# main.py

import json
import sys

from pathlib import Path

from mips_decoder import (
    decode_instruction,
    instruction_to_assembly
)

from cpu import (
    MIPSCpu,
    MIPSOverflow,
    InstrucaoForaDoEscopo
)

BASE_DIR = Path(__file__).resolve().parent

def carregar_entrada(caminho):
    """
    Le o arquivo JSON de entrada e devolve o dicionario completo.
    """

    with open(caminho, "r", encoding="utf-8") as arquivo:
        return json.load(arquivo)

def salvar_saida(caminho, conteudo):
    """
    Grava o resultado em JSON
    """

    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(conteudo, arquivo, indent=4, ensure_ascii=False)

def executar_programa(entrada):

    cpu = MIPSCpu()

    # ---------------------------------------------------------
    # CONFIGURACAO INICIAL
    # ---------------------------------------------------------

    config = entrada.get("config", {})

    cpu.registers.load_registers(config.get("regs", {}))

    # ---------------------------------------------------------
    # CICLO PRINCIPAL
    # ---------------------------------------------------------

    resultados = []
    avisos = []

    for posicao, hexadecimal in enumerate(entrada.get("text", [])):

        try:
            decoded = decode_instruction(hexadecimal)
            assembly = instruction_to_assembly(decoded)

        except ValueError as erro:

            # Instrucao que nem chega a ser reconhecida
            avisos.append(f"[{posicao}] {hexadecimal}: {erro}")

            resultados.append({
                "hex": hexadecimal,
                "text": None,
                "regs": cpu.get_register_state(),
                "mem": {},
                "stdout": ""
            })

            continue

        stdout = ""

        try:
            stdout = cpu.step(decoded)

        except MIPSOverflow as erro:

            # O registrador destino nao e escrito quando
            # ocorre overflow; o estado segue como estava.
            avisos.append(f"[{posicao}] {assembly}: {erro}")

        except InstrucaoForaDoEscopo as erro:

            # Não exectado por estar fora do escopo 
            avisos.append(f"[{posicao}] {assembly}: {erro}")

        resultados.append({
            "hex": hexadecimal,
            "text": assembly,
            "regs": cpu.get_register_state(),
            "mem": {},
            "stdout": stdout
        })

    return resultados, avisos


def main():

    if len(sys.argv) > 1:
        arquivo_entrada = Path(sys.argv[1])
    else:
        arquivo_entrada = BASE_DIR / "entrada.json"

    if len(sys.argv) > 2:
        arquivo_saida = Path(sys.argv[2])
    else:
        arquivo_saida = BASE_DIR / "saida.json"

    entrada = carregar_entrada(arquivo_entrada)

    resultados, avisos = executar_programa(entrada)

    salvar_saida(arquivo_saida, resultados)

    # ---------------------------------------------------------
    # RESUMO DA SAÍDA
    # ---------------------------------------------------------

    print(f"Entrada: {arquivo_entrada}")
    print(f"Saida:   {arquivo_saida}")
    print()

    for resultado in resultados:
        print(f"{resultado['hex']} -> {resultado['text']}")

    if avisos:
        print()
        print("Avisos:")

        for aviso in avisos:
            print(f"  {aviso}")

    print()
    print("Execucao concluida.")


if __name__ == "__main__":
    main()