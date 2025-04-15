from pathlib import Path

def scan_structure_info(base_path='.'):
    base_path = Path(base_path)
    for txt_file in base_path.glob("*.txt"):
        system = txt_file.stem.split('_', 2)[-1]
        print(f"\nProcessing file: {txt_file.name}")
        print(f"  System: {system}")

        system_dir = base_path / system
        if not system_dir.is_dir():
            raise FileNotFoundError(f"Directory '{system_dir}' not found for system '{system}'.")

        with txt_file.open() as f:
            for line_num, line in enumerate(f, 1):
                parts = line.strip().split()
                if len(parts) != 3:
                    raise ValueError(f"Line {line_num} in {txt_file} does not have 3 fields: '{line.strip()}'")
                
                name, charge, multiplicity = parts
                struct_dir = system_dir / name
                coord = struct_dir / 'coord'
                xyz = struct_dir / 'struc.xyz'

                if not struct_dir.is_dir():
                    raise FileNotFoundError(f"Structure directory '{struct_dir}' not found.")

                if not coord.is_file():
                    raise FileNotFoundError(f"Missing 'coord' file in {struct_dir}")

                if not xyz.is_file():
                    raise FileNotFoundError(f"Missing 'struc.xyz' file in {struct_dir}")

                # Read number of atoms from first line of struc.xyz
                with xyz.open() as xyz_file:
                    first_line = xyz_file.readline().strip()
                    try:
                        num_atoms = int(first_line)
                    except ValueError:
                        raise ValueError(f"First line of {xyz} is not an integer: '{first_line}'")

                print(f"    Found: {name} (Charge: {charge}, Multiplicity: {multiplicity}, Atoms: {num_atoms})")

if __name__ == "__main__":
    scan_structure_info()

