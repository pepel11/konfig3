import argparse
import struct
import json

# Таблица команд УВМ: mnemonic -> (A код, размер в байтах)
COMMANDS = {
    12: {"mnemonic": "LOAD_CONST", "size": 4},    # загрузка константы
    10: {"mnemonic": "READ_MEM", "size": 4},      # чтение из памяти
    7:  {"mnemonic": "WRITE_MEM", "size": 2},     # запись в память
    1:  {"mnemonic": "BITREVERSE", "size": 2}     # унарная операция
}

MEMORY_SIZE = 1024  # пример размера памяти данных

def parse_args():
    parser = argparse.ArgumentParser(description="UVM Interpreter - Variant 20")
    parser.add_argument("binary", help="Path to binary file with program")
    parser.add_argument("dump", help="Path to JSON file for memory dump")
    parser.add_argument("--start", type=int, default=0, help="Start address for memory dump")
    parser.add_argument("--end", type=int, default=64, help="End address for memory dump")
    return parser.parse_args()

def decode_instruction(data, pc):
    # Сначала считываем байт для A
    first_byte = data[pc]
    A = first_byte & 0x0F  # 4 младших бита — это A

    if A in [12, 10]:  # команды 4 байта
        raw = struct.unpack_from("<I", data, pc)[0]
        if A == 12:  # LOAD_CONST
            B = (raw >> 4) & 0x3FFFFF
            C = (raw >> 26) & 0x1F
        else:       # READ_MEM
            B = (raw >> 4) & 0x1FFFF
            C = (raw >> 21) & 0x1F
        size = 4
    elif A in [7, 1]:  # команды 2 байта
        raw = struct.unpack_from("<H", data, pc)[0]
        B = (raw >> 4) & 0x1F
        C = (raw >> 9) & 0x1F
        size = 2
    else:
        raise ValueError(f"Unknown opcode {A} at PC={pc}")

    return {"A": A, "B": B, "C": C, "size": size, "mnemonic": COMMANDS[A]["mnemonic"]}


def bitreverse(value, bits=32):
    return int('{:0{width}b}'.format(value, width=bits)[::-1], 2)

def run_program(binary_file, mem_dump_file, start_addr, end_addr):
    # Загрузка программы в память команд
    with open(binary_file, "rb") as f:
        code = f.read()

    # Инициализация памяти данных
    data_mem = [0] * MEMORY_SIZE
    reg_mem = [0] * 32  # регистры по адресам

    pc = 0
    while pc < len(code):
        instr = decode_instruction(code, pc)
        A, B, C = instr["A"], instr["B"], instr["C"]
        mnemonic = instr["mnemonic"]

        if mnemonic == "LOAD_CONST":
            reg_mem[C] = B
        elif mnemonic == "READ_MEM":
            reg_mem[C] = data_mem[B]
        elif mnemonic == "WRITE_MEM":
            data_mem[C] = reg_mem[B]
        elif mnemonic == "BITREVERSE":
            reg_mem[C] = bitreverse(reg_mem[B], bits=32)
        else:
            raise ValueError(f"Unknown instruction at PC={pc}")

        pc += instr["size"]

    # Формирование дампа памяти
    mem_dump = {addr: data_mem[addr] for addr in range(start_addr, min(end_addr, MEMORY_SIZE))}
    with open(mem_dump_file, "w") as f:
        json.dump(mem_dump, f, indent=4)
    print(f"Memory dump saved to {mem_dump_file}")

if __name__ == "__main__":
    args = parse_args()
    run_program(args.binary, args.dump, args.start, args.end)
# python etap3.py program3.bin memory_dump3.json --start 0 --end 4