# registers.py

REGISTER_NAMES = {
    "zero": 0, "at": 1,
    "v0": 2, "v1": 3,
    "a0": 4, "a1": 5, "a2": 6, "a3": 7,
    "t0": 8, "t1": 9, "t2": 10, "t3": 11,
    "t4": 12, "t5": 13, "t6": 14, "t7": 15,
    "s0": 16, "s1": 17, "s2": 18, "s3": 19,
    "s4": 20, "s5": 21, "s6": 22, "s7": 23,
    "t8": 24, "t9": 25,
    "k0": 26, "k1": 27,
    "gp": 28, "sp": 29, "fp": 30, "ra": 31
}

GP_INICIAL = 0x10008000     # $28 - global pointer
SP_INICIAL = 0x7FFFEFFC     # $29 - stack pointer
PC_INICIAL = 0x00400000     # inicio do segmento de texto

class RegisterBank:
    """
    Banco de registradores do MIPS.

    Registradores:
        $0 até $31
        $pc
        $hi / $lo
    """

    def __init__(self):
        self.regs = [0] * 32

        self.regs[REGISTER_NAMES["gp"]] = GP_INICIAL
        self.regs[REGISTER_NAMES["sp"]] = SP_INICIAL

        self.pc = PC_INICIAL
        self.hi = 0
        self.lo = 0

    # =========================================================
    # CONVERSÕES
    # =========================================================

    @staticmethod
    def to_unsigned(value):
        """
        Mantém um valor dentro de 32 bits.

        Exemplo:
            -1 -> 4294967295
        """

        return value & 0xFFFFFFFF

    @staticmethod
    def to_signed(value):
        """
        Interpreta um valor de 32 bits como inteiro com sinal.

        Exemplo:
            0xFFFFFFFF -> -1
        """

        value &= 0xFFFFFFFF

        if value & 0x80000000:
            return value - 0x100000000

        return value

    # =========================================================
    # REGISTRADORES $0 - $31
    # =========================================================

    def _get_register_index(self, register):
        """
        Converte:
            "$10" -> 10
            10    -> 10
        """

        if isinstance(register, int):
            index = register

        else:
            nome = str(register).strip()

            if nome.startswith("$"):
                nome = nome[1:]

            # Forma simbolica ($sp, $t0, $zero...)
            if nome.lower() in REGISTER_NAMES:
                index = REGISTER_NAMES[nome.lower()]

            else:
                try:
                    index = int(nome)

                except ValueError:
                    raise ValueError(
                        f"Registrador invalido: {register}"
                    )

        if index < 0 or index > 31:
            raise ValueError(
                f"Registrador fora do intervalo: ${index}"
            )

        return index

    def read(self, register):
        """
        Lê um registrador.
        """

        return self.regs[self._get_register_index(register)]

    def read_signed(self, register):
        """
        Lê um registrador interpretando seu conteúdo
        como inteiro com sinal de 32 bits.
        """

        return self.to_signed(self.read(register))

    def write(self, register, value):
        """
        Escreve em um registrador.

        $0 nunca pode ser alterado.
        """

        index = self._get_register_index(register)

        # $0 é permanentemente zero
        if index == 0:
            return

        self.regs[index] = self.to_unsigned(value)

    # =========================================================
    # PC
    # =========================================================

    def read_pc(self):
        return self.pc

    def write_pc(self, value):
        self.pc = self.to_unsigned(value)

    def increment_pc(self, value=4):
        self.pc = self.to_unsigned(self.pc + value)

    # =========================================================
    # HI / LO
    # =========================================================
    # Guardam o resultado de 64 bits de mult e div:
    #   hi -> 32 bits mais significativos
    #   lo -> 32 bits menos significativos

    def read_hi(self):
        return self.hi

    def read_hi_signed(self):
        return self.to_signed(self.hi)

    def write_hi(self, value):
        self.hi = self.to_unsigned(value)

    def read_lo(self):
        return self.lo

    def read_lo_signed(self):
        return self.to_signed(self.lo)

    def write_lo(self, value):
        self.lo = self.to_unsigned(value)

    # =========================================================
    # CONFIGURAÇÃO INICIAL
    # =========================================================

    @staticmethod
    def _coerce_value(value):
        """
        Aceita o valor do config como inteiro ou como string
        decimal/hexadecimal
        """

        if isinstance(value, int):
            return value

        texto = str(value).strip()

        if texto.lower().startswith("0x"):
            return int(texto, 16)

        return int(texto) 


    def load_registers(self, registers):
        """
        Carrega os registradores fornecidos pelo JSON.
        """

        for register, value in registers.items():

            valor = self._coerce_value(value)

            chave = str(register).strip().lstrip("$").lower()

            if chave == "pc":
                self.write_pc(valor)

            elif chave == "hi":
                self.write_hi(valor)

            elif chave == "lo":
                self.write_lo(valor)

            else:
                self.write(register, valor)

    # =========================================================
    # ESTADO PARA O JSON
    # =========================================================

    def get_non_zero_registers(self):
        """
        Retorna somente os registradores diferentes de zero.

        Ordem: $1 ... $31, depois $pc, $hi e $lo.

        $0 nunca aparece porqe é sempre zero.
        """

        result = {}

        for index in range(1, 32):

            if self.regs[index] != 0:
                result[f"${index}"] = self.to_signed(self.regs[index])

        if self.pc != 0:
            result["$pc"] = self.to_signed(self.pc)

        if self.hi != 0:
            result["$hi"] = self.to_signed(self.hi)

        if self.lo != 0:
            result["$lo"] = self.to_signed(self.lo)

        return result

    def __str__(self):
        return str(self.get_non_zero_registers())