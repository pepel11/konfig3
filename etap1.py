import argparse

# Таблица команд УВМ: mnemonic -> (A код, длина команды в байтах)
COMMANDS = {
    "LOAD_CONST": {"A": 12, "size": 4},    # загрузка константы
    "READ_MEM":   {"A": 10, "size": 4},    # чтение из памяти
    "WRITE_MEM":  {"A": 7,  "size": 2},    # запись в память
    "BITREVERSE": {"A": 1,  "size": 2}     # унарная операция
}

def parse_args():
    parser = argparse.ArgumentParser(description="Assembler for UVM Variant 20")
    parser.add_argument("source", help="Path to source assembly file")
    parser.add_argument("output", help="Path to output binary file")
    parser.add_argument("--test", action="store_true", help="Enable test mode")
    return parser.parse_args()

def parse_line(line):
    # удалить комментарии
    line = line.split(";")[0].strip()
    if not line:
        return None
    parts = line.split()
    mnemonic = parts[0].upper()
    args = [int(arg) for arg in " ".join(parts[1:]).replace(",", " ").split()]
    if mnemonic not in COMMANDS:
        raise ValueError(f"Unknown mnemonic: {mnemonic}")
    return {"mnemonic": mnemonic, "args": args, "A": COMMANDS[mnemonic]["A"], "size": COMMANDS[mnemonic]["size"]}

def assemble(source_path):
    instructions = []
    with open(source_path, "r") as f:
        for line in f:
            instr = parse_line(line)
            if instr:
                instructions.append(instr)
    return instructions

def main():
    args = parse_args()
    instructions = assemble(args.source)

    if args.test:
        print("=== Internal Representation ===")
        for i, instr in enumerate(instructions):
            print(f"{i}: {instr}")

    # запись во внешний бинарный файл (пока просто как текст для проверки)
    with open(args.output, "w") as f:
        for instr in instructions:
            f.write(f"{instr}\n")

if __name__ == "__main__":
    main()
# python etap1.py program1.asm output.txt --test
