import argparse
import struct

# Таблица команд УВМ: mnemonic -> (A код, длина команды в байтах)
COMMANDS = {
    "LOAD_CONST": {"A": 12, "size": 4},    # 4 байта: A 0-3, B 4-25, C 26-30
    "READ_MEM":   {"A": 10, "size": 4},    # 4 байта: A 0-3, B 4-20, C 21-25
    "WRITE_MEM":  {"A": 7,  "size": 2},    # 2 байта: A 0-3, B 4-8, C 9-13
    "BITREVERSE": {"A": 1,  "size": 2}     # 2 байта: A 0-3, B 4-8, C 9-13
}

def parse_args():
    parser = argparse.ArgumentParser(description="Assembler for UVM Variant 20")
    parser.add_argument("source", help="Path to source assembly file")
    parser.add_argument("output", help="Path to output binary file")
    parser.add_argument("--test", action="store_true", help="Enable test mode")
    return parser.parse_args()

def parse_line(line):
    line = line.split(";")[0].strip()
    if not line:
        return None
    parts = line.split()
    mnemonic = parts[0].upper()
    args = [int(arg) for arg in " ".join(parts[1:]).replace(",", " ").split()]
    if mnemonic not in COMMANDS:
        raise ValueError(f"Unknown mnemonic: {mnemonic}")
    return {
        "mnemonic": mnemonic,
        "args": args,
        "A": COMMANDS[mnemonic]["A"],
        "size": COMMANDS[mnemonic]["size"]
    }

def assemble(source_path):
    instructions = []
    with open(source_path, "r") as f:
        for line in f:
            instr = parse_line(line)
            if instr:
                instructions.append(instr)
    return instructions

def encode_instruction(instr):
    A = instr["A"]
    args = instr["args"]
    size = instr["size"]

    if size == 4:
        if A == 12:  # LOAD_CONST
            B, C = args
            # 4 байта: A 0-3, B 4-25, C 26-30
            value = (A & 0xF) | ((B & 0x3FFFFF) << 4) | ((C & 0x1F) << 26)
            return struct.pack("<I", value)
        elif A == 10:  # READ_MEM
            B, C = args
            value = (A & 0xF) | ((B & 0x1FFFF) << 4) | ((C & 0x1F) << 21)
            return struct.pack("<I", value)
    elif size == 2:
        B, C = args
        value = (A & 0xF) | ((B & 0x1F) << 4) | ((C & 0x1F) << 9)
        return struct.pack("<H", value)
    else:
        raise ValueError(f"Unsupported instruction size: {size}")

def main():
    args = parse_args()
    instructions = assemble(args.source)

    if args.test:
        print("=== Internal Representation ===")
        for i, instr in enumerate(instructions):
            print(f"{i}: {instr}")

    # Генерация бинарного кода
    binary_code = b""
    for instr in instructions:
        binary_code += encode_instruction(instr)

    # Запись в бинарный файл
    with open(args.output, "wb") as f:
        f.write(binary_code)

    print(f"Binary file '{args.output}' generated, size: {len(binary_code)} bytes")

    if args.test:
        print("=== Machine Code Bytes ===")
        print(" ".join(f"{b:02X}" for b in binary_code))

if __name__ == "__main__":
    main()
# python etap2.py program1.asm program2.bin --test
