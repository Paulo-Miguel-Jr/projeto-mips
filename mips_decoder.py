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

    if value & (1 << (bits - 1)):
        value -= (1 << bits)

    return value


def decode_instruction(hex_instruction):

    hex_instruction = hex_instruction.strip()

    if hex_instruction.startswith("0x"):
        hex_instruction = hex_instruction[2:]

    instruction = int(hex_instruction, 16)

    instruction &= 0xFFFFFFFF

    opcode = (instruction >> 26) & 0x3F

    # =========================================================
    # TIPO R
    # =========================================================

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

        return {
            "mnemonic": mnemonic,
            "type": "R",
            "rs": rs,
            "rt": rt,
            "rd": rd,
            "shamt": shamt,
            "funct": funct
        }

    # =========================================================
    # TIPO I
    # =========================================================

    if opcode in INSTRUCTIONS_I:

        mnemonic = INSTRUCTIONS_I[opcode]

        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F

        immediate = instruction & 0xFFFF

        immediate = sign_extend(immediate, 16)

        return {
            "mnemonic": mnemonic,
            "type": "I",
            "rs": rs,
            "rt": rt,
            "immediate": immediate,
            "opcode": opcode
        }

    # =========================================================
    # TIPO J
    # =========================================================

    if opcode in INSTRUCTIONS_J:

        mnemonic = INSTRUCTIONS_J[opcode]

        address = instruction & 0x03FFFFFF

        return {
            "mnemonic": mnemonic,
            "type": "J",
            "address": address,
            "opcode": opcode
        }

    raise ValueError(
        f"Opcode desconhecido: {opcode}"
    )


# =============================================================
# FORMATAÇÃO PARA ASSEMBLY
# =============================================================

def instruction_to_assembly(decoded):

    mnemonic = decoded["mnemonic"]

    if decoded["type"] == "R":

        if mnemonic == "syscall":
            return "syscall"

        if mnemonic == "jr":
            return f"jr ${decoded['rs']}"

        if mnemonic in ("mfhi", "mflo"):
            return f"{mnemonic} ${decoded['rd']}"

        if mnemonic in ("sll", "srl", "sra"):
            return (
                f"{mnemonic} "
                f"${decoded['rd']}, "
                f"${decoded['rt']}, "
                f"{decoded['shamt']}"
            )

        if mnemonic in ("sllv", "srlv", "srav"):
            return (
                f"{mnemonic} "
                f"${decoded['rd']}, "
                f"${decoded['rt']}, "
                f"${decoded['rs']}"
            )

        if mnemonic in ("div", "divu", "mult", "multu"):
            return (
                f"{mnemonic} "
                f"${decoded['rs']}, "
                f"${decoded['rt']}"
            )

        return (
            f"{mnemonic} "
            f"${decoded['rd']}, "
            f"${decoded['rs']}, "
            f"${decoded['rt']}"
        )

    if decoded["type"] == "I":

        if mnemonic in ("andi", "ori", "xori"):
            immediate = decoded["immediate"] & 0xFFFF
        else:
            immediate = decoded["immediate"]

        return (
            f"{mnemonic} "
            f"${decoded['rt']}, "
            f"${decoded['rs']}, "
            f"{immediate}"
        )

    if decoded["type"] == "J":

        return (
            f"{mnemonic} "
            f"{decoded['address']}"
        )

    raise ValueError(
        "Tipo de instrução desconhecido."
    )


def decode_hex_list(hex_list):
    """
    Decodifica uma lista de instruções hexadecimais.
    """

    decoded = []

    for instruction in hex_list:
        decoded.append(decode_instruction(instruction))

    return decoded