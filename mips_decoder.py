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

    # -----------------------------------------------------------
    # TIPO R
    # -----------------------------------------------------------
    # Cada campo e isolado com deslocamento seguido de
    # mascara: 0x1F = 5 bits, 0x3F = 6 bits.

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

        return {
            "mnemonic": INSTRUCTIONS_R[funct],
            "type": "R",
            "opcode": opcode,
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

        rs = (instruction >> 21) & 0x1F
        rt = (instruction >> 16) & 0x1F

        # Os 16 bits do campo immediate.
        immediate_unsigned = instruction & 0xFFFF

        return {
            "mnemonic": INSTRUCTIONS_I[opcode],
            "type": "I",
            "opcode": opcode,
            "rs": rs,
            "rt": rt,
            "immediate": sign_extend(immediate_unsigned, 16),
            "immediate_unsigned": immediate_unsigned
        }

    # =========================================================
    # TIPO J
    # =========================================================

    if opcode in INSTRUCTIONS_J:

        return {
            "mnemonic": INSTRUCTIONS_J[opcode],
            "type": "J",
            "opcode": opcode,
            "address": instruction & 0x03FFFFFF
        }

    # -----------------------------------------------------------
    # OPCODE NAO RECONHECIDO
    # -----------------------------------------------------------

    raise ValueError(
        f"Opcode desconhecido: {opcode}"
    )


# =============================================================
# FORMATAÇÃO PARA ASSEMBLY
# =============================================================

def instruction_to_assembly(decoded):

    mnemonic = decoded["mnemonic"]

    # ---------------------------------------------------------
    # TIPO R
    # ---------------------------------------------------------

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

    # ---------------------------------------------------------
    # TIPO I
    # ---------------------------------------------------------

    if decoded["type"] == "I":

        rs = decoded["rs"]
        rt = decoded["rt"]

        if mnemonic in ("andi", "ori", "xori", "lui"):
            immediate = decoded["immediate_unsigned"]
        else:
            immediate = decoded["immediate"]

        if mnemonic in ("beq", "bne"):
            return f"{mnemonic} ${rs}, ${rt}, {immediate}"

        if mnemonic in ("bgtz", "bltz", "blez"):
            return f"{mnemonic} ${rs}, {immediate}"

        if mnemonic == "lui":
            return f"lui ${rt}, {immediate}"

        if mnemonic in ("lw", "lb", "lbu", "sw", "sb"):
            return f"{mnemonic} ${rt}, {immediate}(${rs})"

        return f"{mnemonic} ${rt}, ${rs}, {immediate}"

    # ---------------------------------------------------------
    # TIPO J
    # ---------------------------------------------------------

    if decoded["type"] == "J":
        return f"{mnemonic} {decoded['address']}"

    raise ValueError(
        "Tipo de instrucao desconhecido."
    )

def decode_hex_list(hex_list):
    """
    Decodifica uma lista de instruções hexadecimais.
    """
    
    return [decode_instruction(item) for item in hex_list]