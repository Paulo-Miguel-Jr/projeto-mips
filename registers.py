# registers.py


class RegisterBank:
    """
    Banco de registradores do MIPS.

    Registradores:
        $0 até $31
        $pc
        $hi
        $lo
    """

    def __init__(self):
        self.regs = [0] * 32

        self.pc = 0
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

        if isinstance(register, str):

            if not register.startswith("$"):
                raise ValueError(
                    f"Registrador inválido: {register}"
                )

            register = register[1:]

        try:
            index = int(register)

        except ValueError:
            raise ValueError(
                f"Registrador inválido: {register}"
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

        index = self._get_register_index(register)

        return self.regs[index]

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
    # HI
    # =========================================================

    def read_hi(self):
        return self.hi

    def read_hi_signed(self):
        return self.to_signed(self.hi)

    def write_hi(self, value):
        self.hi = self.to_unsigned(value)

    # =========================================================
    # LO
    # =========================================================

    def read_lo(self):
        return self.lo

    def read_lo_signed(self):
        return self.to_signed(self.lo)

    def write_lo(self, value):
        self.lo = self.to_unsigned(value)

    # =========================================================
    # CONFIGURAÇÃO INICIAL
    # =========================================================

    def load_registers(self, registers):
        """
        Carrega os registradores fornecidos pelo JSON.

        Exemplo:

        {
            "$1": 10,
            "$2": 20
        }
        """

        for register, value in registers.items():

            if register == "$pc":
                self.write_pc(value)

            elif register == "$hi":
                self.write_hi(value)

            elif register == "$lo":
                self.write_lo(value)

            else:
                self.write(register, value)

    # =========================================================
    # ESTADO PARA O JSON
    # =========================================================

    def get_non_zero_registers(self):
        """
        Retorna somente os registradores diferentes de zero.

        Ordem:
            $0 ... $31
            $pc
            $hi
            $lo

        $0 nunca aparece.
        """

        result = {}

        for index in range(1, 32):

            if self.regs[index] != 0:
                result[f"${index}"] = self.to_signed(
                    self.regs[index]
                )

        if self.pc != 0:
            result["$pc"] = self.to_signed(self.pc)

        if self.hi != 0:
            result["$hi"] = self.to_signed(self.hi)

        if self.lo != 0:
            result["$lo"] = self.to_signed(self.lo)

        return result

    def __str__(self):
        return str(self.get_non_zero_registers())