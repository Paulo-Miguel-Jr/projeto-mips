# cpu.py

from registers import RegisterBank

class MIPSOverflow(Exception):
    """
    Overflow aritmetico com sinal em add, addi ou sub.
    """

class InstrucaoForaDoEscopo(Exception):
    """
    Instrucao valida do MIPS, porem fora do escopo do projeto
    (como desvios, saltos, acesso a memoria e syscall).
    """

# Conjunto das instrucoes logicas e aritmeticas que devem ser
# executadas nesta parte do projeto.
INSTRUCOES_EXECUTAVEIS = {
    # Tipo R - aritmeticas
    "add", "addu", "sub", "subu",
    "mult", "multu", "div", "divu",
    "mfhi", "mflo", "slt",
    # Tipo R - logicas
    "and", "or", "xor", "nor",
    # Tipo R - deslocamentos
    "sll", "srl", "sra", "sllv", "srlv", "srav",
    # Tipo I
    "addi", "addiu", "slti", "andi", "ori", "xori", "lui"
}
class MIPSCpu:
    """
    CPU responsável pela execução das instruções
    aritméticas e lógicas da Entrega 2.
    """

    def __init__(self):
        self.registers = RegisterBank()

    # =========================================================
    # AUXILIARES
    # =========================================================

    @staticmethod
    def _check_signed_32(value):
        """
        Verifica se o resultado cabe em um inteiro com sinal de
        32 bits (-2^31 a 2^31 - 1).
        """

        return -2147483648 <= value <= 2147483647

    # =========================================================
    # EXECUÇÃO
    # =========================================================

    def step(self, instruction):
        """
        Executa uma instrucao e avanca o PC.
        """

        try:
            saida = self.execute(instruction)

        finally:
            # Uma instrucao ocupa 4 bytes (uma palavra).
            self.registers.increment_pc()

        return saida


    def execute(self, instruction):
        """
        Executa uma instrução já decodificada.

        Recebe um dicionário contendo os campos da instrução.
        """

        mnemonic = instruction["mnemonic"]

        if mnemonic not in INSTRUCOES_EXECUTAVEIS:
            raise InstrucaoForaDoEscopo(
                f"Instrucao fora do escopo: {mnemonic}"
            )

        # -----------------------------------------------------
        # INSTRUÇÕES R - ARITMÉTICAS
        # -----------------------------------------------------

        if mnemonic == "add":

            rs = self.registers.read_signed(instruction["rs"])
            rt = self.registers.read_signed(instruction["rt"])

            result = rs + rt

            if not self._check_signed_32(result):
                raise MIPSOverflow("Overflow em add")

            self.registers.write(
                instruction["rd"],
                result
            )

        elif mnemonic == "sub":

            rs = self.registers.read_signed(instruction["rs"])
            rt = self.registers.read_signed(instruction["rt"])

            result = rs - rt

            if not self._check_signed_32(result):
                raise MIPSOverflow("Overflow em sub")

            self.registers.write(
                instruction["rd"],
                result
            )

        elif mnemonic == "addu":

            rs = self.registers.read(instruction["rs"])
            rt = self.registers.read(instruction["rt"])

            self.registers.write(instruction["rd"], rs + rt)

        elif mnemonic == "subu":

            rs = self.registers.read(instruction["rs"])
            rt = self.registers.read(instruction["rt"])

            self.registers.write(instruction["rd"], rs - rt)

        # -----------------------------------------------------
        # SLT
        # -----------------------------------------------------

        elif mnemonic == "slt":

            rs = self.registers.read_signed(instruction["rs"])
            rt = self.registers.read_signed(instruction["rt"])

            self.registers.write(
                instruction["rd"],
                1 if rs < rt else 0
            )

        # -----------------------------------------------------
        # OPERAÇÕES LÓGICAS
        # -----------------------------------------------------

        elif mnemonic == "and":

            rs = self.registers.read(instruction["rs"])
            rt = self.registers.read(instruction["rt"])

            self.registers.write(
                instruction["rd"],
                rs & rt
            )

        elif mnemonic == "or":

            rs = self.registers.read(instruction["rs"])
            rt = self.registers.read(instruction["rt"])

            self.registers.write(
                instruction["rd"],
                rs | rt
            )

        elif mnemonic == "xor":

            rs = self.registers.read(instruction["rs"])
            rt = self.registers.read(instruction["rt"])

            self.registers.write(
                instruction["rd"],
                rs ^ rt
            )

        elif mnemonic == "nor":

            rs = self.registers.read(instruction["rs"])
            rt = self.registers.read(instruction["rt"])

            self.registers.write(instruction["rd"], ~(rs | rt))

        # -----------------------------------------------------
        # HI / LO
        # -----------------------------------------------------

        elif mnemonic == "mfhi":

            self.registers.write(
                instruction["rd"],
                self.registers.read_hi()
            )

        elif mnemonic == "mflo":

            self.registers.write(
                instruction["rd"],
                self.registers.read_lo()
            )

        # -----------------------------------------------------
        # MULT
        # -----------------------------------------------------

        elif mnemonic == "mult":

            rs = self.registers.read_signed(instruction["rs"])
            rt = self.registers.read_signed(instruction["rt"])

            result = (rs * rt) & 0xFFFFFFFFFFFFFFFF

            self.registers.write_hi((result >> 32) & 0xFFFFFFFF)
            self.registers.write_lo(result & 0xFFFFFFFF)

        elif mnemonic == "multu":

            rs = self.registers.read(instruction["rs"])
            rt = self.registers.read(instruction["rt"])

            result = (rs * rt) & 0xFFFFFFFFFFFFFFFF

            self.registers.write_hi((result >> 32) & 0xFFFFFFFF)
            self.registers.write_lo(result & 0xFFFFFFFF)

        # -----------------------------------------------------
        # DIV
        # -----------------------------------------------------

        elif mnemonic == "div":

            rs = self.registers.read_signed(instruction["rs"])
            rt = self.registers.read_signed(instruction["rt"])

            if rt != 0:
                quotient = abs(rs) // abs(rt)

                if (rs < 0) != (rt < 0):
                    quotient = -quotient

                remainder = rs - quotient * rt

                self.registers.write_lo(quotient)
                self.registers.write_hi(remainder)

        elif mnemonic == "divu":

            rs = self.registers.read(instruction["rs"])
            rt = self.registers.read(instruction["rt"])

            if rt != 0:
                self.registers.write_lo(rs // rt)
                self.registers.write_hi(rs % rt)

        # -----------------------------------------------------
        # DESLOCAMENTOS
        # -----------------------------------------------------

        elif mnemonic == "sll":

            rt = self.registers.read(instruction["rt"])

            self.registers.write(
                instruction["rd"],
                rt << instruction["shamt"]
            )

        elif mnemonic == "srl":

            rt = self.registers.read(instruction["rt"])

            self.registers.write(
                instruction["rd"],
                rt >> instruction["shamt"]
            )

        elif mnemonic == "sra":

            rt = self.registers.read_signed(instruction["rt"])
            shamt = instruction["shamt"]

            result = rt >> shamt

            self.registers.write(
                instruction["rd"],
                result
            )

        # -----------------------------------------------------
        # DESLOCAMENTOS VARIÁVEIS
        # -----------------------------------------------------

        elif mnemonic == "sllv":

            rt = self.registers.read(instruction["rt"])
            shamt = self.registers.read(instruction["rs"]) & 0x1F

            self.registers.write(instruction["rd"], rt << shamt)

        elif mnemonic == "srlv":

            rt = self.registers.read(instruction["rt"])
            shamt = self.registers.read(instruction["rs"]) & 0x1F

            self.registers.write(instruction["rd"], rt >> shamt)

        elif mnemonic == "srav":

            rt = self.registers.read_signed(instruction["rt"])
            shamt = self.registers.read(instruction["rs"]) & 0x1F

            self.registers.write(instruction["rd"], rt >> shamt)

        # -----------------------------------------------------
        # ADDI
        # -----------------------------------------------------

        elif mnemonic == "addi":

            rs = self.registers.read_signed(instruction["rs"])

            result = rs + instruction["immediate"]

            if not self._check_signed_32(result):
                raise MIPSOverflow("Overflow em addi")

            self.registers.write(instruction["rt"], result)

        # -----------------------------------------------------
        # ADDIU
        # -----------------------------------------------------

        elif mnemonic == "addiu":

           rs = self.registers.read(instruction["rs"])

           self.registers.write(
                instruction["rt"],
                rs + instruction["immediate"]
            )

        # -----------------------------------------------------
        # SLTI
        # -----------------------------------------------------

        elif mnemonic == "slti":

            rs = self.registers.read_signed(instruction["rs"])

            self.registers.write(
                instruction["rt"],
                1 if rs < instruction["immediate"] else 0
            )

        # -----------------------------------------------------
        # ANDI
        # -----------------------------------------------------

        elif mnemonic == "andi":

            rs = self.registers.read(instruction["rs"])

            self.registers.write(
                instruction["rt"],
                rs & instruction["immediate_unsigned"]
            )

        # -----------------------------------------------------
        # ORI
        # -----------------------------------------------------

        elif mnemonic == "ori":

            rs = self.registers.read(instruction["rs"])

            self.registers.write(
                instruction["rt"],
                rs | instruction["immediate_unsigned"]
            )

        # -----------------------------------------------------
        # XORI
        # -----------------------------------------------------

        elif mnemonic == "xori":

            rs = self.registers.read(instruction["rs"])

            self.registers.write(
                instruction["rt"],
                rs ^ instruction["immediate_unsigned"]
            )

        elif mnemonic == "lui":

            self.registers.write(
                instruction["rt"],
                instruction["immediate_unsigned"] << 16
            )

        return ""

    # =========================================================
    # ESTADO
    # =========================================================

    def get_register_state(self):
        """
        Retorna somente os registradores diferentes de zero.
        """

        return self.registers.get_non_zero_registers()