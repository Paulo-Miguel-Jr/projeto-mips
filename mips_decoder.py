# mips_decoder.py

# Tabela das instruções MIPS


INSTRUCTIONS_R = {
    32: "add",
    33: "addu",
    36: "and",
    26: "div",
    27: "divu",
    8: "jr",
    16: "mfhi",
    18: "mflo",
    24: "mult",
    25: "multu",
    39: "nor",
    37: "or",
    0: "sll",
    4: "sllv",
    42: "slt",
    3: "sra",
    7: "srav",
    2: "srl",
    6: "srlv",
    34: "sub",
    35: "subu",
    12: "syscall",
    38: "xor"
}

INSTRUCTIONS_I = {
    8: "addi",
    9: "addiu",
    12: "andi",
    7: "bgtz",
    4: "beq",
    1: "bltz",
    6: "blez",
    5: "bne",
    32: "lb",
    36: "lbu",
    15: "lui",
    35: "lw",
    13: "ori",
    40: "sb",
    10: "slti",
    43: "sw",
    14: "xori"
}

INSTRUCTIONS_J = {
    2: "j",
    3: "jal"
}


def sign_extend(value, bits):
    """
    Converte um valor para inteiro com sinal.

    Exemplo:
    0xFFFF com 16 bits -> -1
    """
    if value & (1 << (bits - 1)):
        value -= (1 << bits)

    return value


def decode_instruction(hex_instruction):
    """
    Recebe uma instrução MIPS em hexadecimal
    e retorna sua representação em Assembly.
    """

    hex_instruction = hex_instruction.strip()

    if hex_instruction.startswith("0x"):
        hex_instruction = hex_instruction[2:]

    try:
        instruction = int(hex_instruction, 16)
    except ValueError:
        raise ValueError(
            f"Instrucao nao e um hexadecimal valido: {hex_instruction!r}"
        )

    if instruction < 0 or instruction > 0xFFFFFFFF:
        raise ValueError(
            f"Instrucao fora da faixa de 32 bits: {hex_instruction!r}"
        )

    opcode = (instruction >> 26) & 0x3F

    # ---------------------------------------------------------
    # INSTRUÇÕES TIPO R
    # ---------------------------------------------------------

    if opcode == 0:

        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F
        rd = (instruction >> 11) & 0x1F
        shamt = (instruction >> 6) & 0x1F
        funct = instruction & 0x3F

        if funct not in INSTRUCTIONS_R:
            raise ValueError(
                f"Funct desconhecido: {funct}"
            )

        mnemonic = INSTRUCTIONS_R[funct]

        if mnemonic == "syscall":
            return "syscall"

        if mnemonic == "jr":
            return f"jr ${rs}"

        if mnemonic in ("mfhi", "mflo"):
            return f"{mnemonic} ${rd}"

        if mnemonic in ("sll", "srl", "sra"):
            return f"{mnemonic} ${rd}, ${rt}, {shamt}"

        if mnemonic in ("sllv", "srlv", "srav"):
            return f"{mnemonic} ${rd}, ${rt}, ${rs}"

        if mnemonic in ("div", "divu", "mult", "multu"):
            return f"{mnemonic} ${rs}, ${rt}"

        return f"{mnemonic} ${rd}, ${rs}, ${rt}"

    # ---------------------------------------------------------
    # INSTRUÇÕES TIPO J
    # ---------------------------------------------------------

    if opcode in INSTRUCTIONS_J:

        mnemonic = INSTRUCTIONS_J[opcode]

        address = instruction & 0x03FFFFFF

        return f"{mnemonic} {address}"

    # ---------------------------------------------------------
    # INSTRUÇÕES TIPO I
    # ---------------------------------------------------------

    if opcode in INSTRUCTIONS_I:

        mnemonic = INSTRUCTIONS_I[opcode]

        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F

        immediate = instruction & 0xFFFF

        signed_immediate = sign_extend(immediate, 16)

        if mnemonic in ("andi", "ori", "xori"):
            immediate_value = immediate

        else:
            immediate_value = signed_immediate

        # -----------------------------------------------------
        # Branches
        # -----------------------------------------------------

        if mnemonic in ("beq", "bne"):
            return (
                f"{mnemonic} ${rs}, ${rt}, "
                f"{immediate_value}"
            )

        if mnemonic in ("bgtz", "bltz", "blez"):
            return (
                f"{mnemonic} ${rs}, "
                f"{immediate_value}"
            )

        # -----------------------------------------------------
        # lui
        # -----------------------------------------------------

        if mnemonic == "lui":
            return f"lui ${rt}, {immediate_value}"

        # -----------------------------------------------------
        # Load / Store
        # -----------------------------------------------------

        if mnemonic in ("lw", "lb", "lbu", "sw", "sb"):
            return (
                f"{mnemonic} ${rt}, "
                f"{immediate_value}(${rs})"
            )

        # -----------------------------------------------------
        # Instruções I padrão
        # -----------------------------------------------------

        return (
            f"{mnemonic} ${rt}, "
            f"${rs}, {immediate_value}"
        )

    # ---------------------------------------------------------
    # OPCODE NAO RECONHECIDO
    # ---------------------------------------------------------

    raise ValueError(
        f"Opcode desconhecido: {opcode}"
    )


def decode_hex_list(hex_list):
    """
    Decodifica uma lista de instruções hexadecimais.
    """

    decoded = []

    for instruction in hex_list:
        decoded.append(decode_instruction(instruction))

    return decoded