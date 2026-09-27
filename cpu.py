# cpu.py

from registers import RegisterBank


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
    def _signed(value):
        return RegisterBank.to_signed(value)

    @staticmethod
    def _unsigned(value):
        return RegisterBank.to_unsigned(value)

    @staticmethod
    def _check_signed_32(value):
        """
        Verifica se o valor cabe em um inteiro
        com sinal de 32 bits.
        """

        return -2147483648 <= value <= 2147483647

    # =========================================================
    # EXECUÇÃO
    # =========================================================

    def execute(self, instruction):
        """
        Executa uma instrução já decodificada.

        Recebe um dicionário contendo os campos da instrução.
        """

        mnemonic = instruction["mnemonic"]

        # -----------------------------------------------------
        # INSTRUÇÕES R - ARITMÉTICAS
        # -----------------------------------------------------

        if mnemonic == "add":

            rs = self.registers.read_signed(instruction["rs"])
            rt = self.registers.read_signed(instruction["rt"])

            result = rs + rt

            if not self._check_signed_32(result):
                return "overflow"

            self.registers.write(
                instruction["rd"],
                result
            )

        elif mnemonic == "sub":

            rs = self.registers.read_signed(instruction["rs"])
            rt = self.registers.read_signed(instruction["rt"])

            result = rs - rt

            if not self._check_signed_32(result):
                return "overflow"

            self.registers.write(
                instruction["rd"],
                result
            )

        elif mnemonic == "addu":

            rs = self.registers.read(instruction["rs"])
            rt = self.registers.read(instruction["rt"])

            result = rs + rt

            self.registers.write(
                instruction["rd"],
                result
            )

        elif mnemonic == "subu":

            rs = self.registers.read(instruction["rs"])
            rt = self.registers.read(instruction["rt"])

            result = rs - rt

            self.registers.write(
                instruction["rd"],
                result
            )

        # -----------------------------------------------------
        # SLT
        # -----------------------------------------------------

        elif mnemonic == "slt":

            rs = self.registers.read_signed(instruction["rs"])
            rt = self.registers.read_signed(instruction["rt"])

            result = 1 if rs < rt else 0

            self.registers.write(
                instruction["rd"],
                result
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

            result = ~(rs | rt)

            self.registers.write(
                instruction["rd"],
                result
            )

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

            result = rs * rt

            # Resultado de 64 bits
            result &= 0xFFFFFFFFFFFFFFFF

            lo = result & 0xFFFFFFFF
            hi = (result >> 32) & 0xFFFFFFFF

            self.registers.write_hi(hi)
            self.registers.write_lo(lo)

        elif mnemonic == "multu":

            rs = self.registers.read(instruction["rs"])
            rt = self.registers.read(instruction["rt"])

            result = rs * rt

            result &= 0xFFFFFFFFFFFFFFFF

            lo = result & 0xFFFFFFFF
            hi = (result >> 32) & 0xFFFFFFFF

            self.registers.write_hi(hi)
            self.registers.write_lo(lo)

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

                quotient = rs // rt
                remainder = rs % rt

                self.registers.write_lo(quotient)
                self.registers.write_hi(remainder)

        # -----------------------------------------------------
        # DESLOCAMENTOS
        # -----------------------------------------------------

        elif mnemonic == "sll":

            rt = self.registers.read(instruction["rt"])
            shamt = instruction["shamt"]

            result = rt << shamt

            self.registers.write(
                instruction["rd"],
                result
            )

        elif mnemonic == "srl":

            rt = self.registers.read(instruction["rt"])
            shamt = instruction["shamt"]

            result = rt >> shamt

            self.registers.write(
                instruction["rd"],
                result
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
            rs = self.registers.read(instruction["rs"])

            shamt = rs & 0x1F

            result = rt << shamt

            self.registers.write(
                instruction["rd"],
                result
            )

        elif mnemonic == "srlv":

            rt = self.registers.read(instruction["rt"])
            rs = self.registers.read(instruction["rs"])

            shamt = rs & 0x1F

            result = rt >> shamt

            self.registers.write(
                instruction["rd"],
                result
            )

        elif mnemonic == "srav":

            rt = self.registers.read_signed(instruction["rt"])
            rs = self.registers.read(instruction["rs"])

            shamt = rs & 0x1F

            result = rt >> shamt

            self.registers.write(
                instruction["rd"],
                result
            )

        # -----------------------------------------------------
        # ADDI
        # -----------------------------------------------------

        elif mnemonic == "addi":

            rs = self.registers.read_signed(instruction["rs"])
            immediate = instruction["immediate"]

            result = rs + immediate

            if not self._check_signed_32(result):
                return "overflow"

            self.registers.write(
                instruction["rt"],
                result
            )

        # -----------------------------------------------------
        # ADDIU
        # -----------------------------------------------------

        elif mnemonic == "addiu":

            rs = self.registers.read(instruction["rs"])
            immediate = instruction["immediate"]

            result = rs + immediate

            self.registers.write(
                instruction["rt"],
                result
            )

        # -----------------------------------------------------
        # SLTI
        # -----------------------------------------------------

        elif mnemonic == "slti":

            rs = self.registers.read_signed(instruction["rs"])
            immediate = instruction["immediate"]

            result = 1 if rs < immediate else 0

            self.registers.write(
                instruction["rt"],
                result
            )

        # -----------------------------------------------------
        # ANDI
        # -----------------------------------------------------

        elif mnemonic == "andi":

            rs = self.registers.read(instruction["rs"])
            immediate = instruction["immediate"] & 0xFFFF

            self.registers.write(
                instruction["rt"],
                rs & immediate
            )

        # -----------------------------------------------------
        # ORI
        # -----------------------------------------------------

        elif mnemonic == "ori":

            rs = self.registers.read(instruction["rs"])
            immediate = instruction["immediate"] & 0xFFFF

            self.registers.write(
                instruction["rt"],
                rs | immediate
            )

        # -----------------------------------------------------
        # XORI
        # -----------------------------------------------------

        elif mnemonic == "xori":

            rs = self.registers.read(instruction["rs"])
            immediate = instruction["immediate"] & 0xFFFF

            self.registers.write(
                instruction["rt"],
                rs ^ immediate
            )

        else:

            raise ValueError(
                f"Instrução não implementada na Entrega 2: "
                f"{mnemonic}"
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