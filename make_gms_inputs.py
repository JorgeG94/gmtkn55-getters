from pathlib import Path

# Extend this as needed
ELEMENTS = {
    'H': 1,  'He': 2,  'Li': 3,  'Be': 4,  'B': 5,   'C': 6,   'N': 7,   'O': 8,   'F': 9,   'Ne': 10,
    'Na': 11,'Mg': 12, 'Al': 13, 'Si': 14, 'P': 15,  'S': 16,  'Cl': 17, 'Ar': 18,
    'K': 19, 'Ca': 20, 'Sc': 21, 'Ti': 22, 'V': 23,  'Cr': 24, 'Mn': 25, 'Fe': 26, 'Co': 27, 'Ni': 28,
    'Cu': 29,'Zn': 30, 'Br': 35, 'Kr': 36, 'Sn': 50, 'Sb': 51, 'Te': 52, 'I': 53,'Pb': 82, 'Bi': 83
    # Add more if needed
}


template = """!   File created by MacMolPlt 7.7.3
 $CONTRL SCFTYP=rhf RUNTYP=makefp MAXIT=200 $END
 $contrl ispher=1 $end
 $contrl icharg={charge} mult={multiplicity} $end
 $SYSTEM mwords=1000 memddi=1000 $END
 !$BASIS GBASIS=ccq $END
 $basis gbasis=dsvp basnam=dsvp extfil=.true. $end 
 $SCF DIRSCF=.TRUE. $END
 $DATA
{title}
C1
{geometry}
 $END
"""
def xyz_to_gamess_input(xyz_path, charge, multiplicity, title):
    lines = xyz_path.read_text().splitlines()
    try:
        expected_atoms = int(lines[0].strip())
    except ValueError:
        raise ValueError(f"First line of {xyz_path} should be an integer (number of atoms), got: {lines[0]}")

    atoms = lines[2:]  # skip first two lines

    if len(atoms) != expected_atoms:
        raise ValueError(f"Atom count mismatch in {xyz_path}: expected {expected_atoms}, found {len(atoms)}")

    formatted_atoms = []
    for atom_line in atoms:
        parts = atom_line.strip().split()
        raw_symbol = parts[0]
        symbol = raw_symbol.capitalize()  # normalize to match ELEMENTS keys
        assert symbol in ELEMENTS, f"Missing atomic number for element: '{raw_symbol}' (normalized: '{symbol}') in {xyz_path}"
        atomic_number = ELEMENTS[symbol]
        x, y, z = map(float, parts[1:4])
        formatted_atoms.append(f"{symbol} {atomic_number}.0 {x:.6f} {y:.6f} {z:.6f}")

    geometry_block = "\n".join(formatted_atoms)
    return template.format(
        charge=charge,
        multiplicity=multiplicity,
        title=title,
        geometry=geometry_block
    )

def generate_all_inputs(base_path='.'):
    base_path = Path(base_path)
    top_level_output = base_path / "all_gms_inputs"
    top_level_output.mkdir(exist_ok=True)

    for txt_file in base_path.glob("*.txt"):
        parts = txt_file.stem.split('_', 2)
        if len(parts) < 3:
            continue  # skip malformed names
        system = parts[2]
        system_dir = base_path / system
        if not system_dir.is_dir():
            raise FileNotFoundError(f"Missing directory: {system_dir}")

        # New output directory inside all_gms_inputs/
        output_system_dir = top_level_output / f"gms_input_format_{system}"

        with txt_file.open() as f:
            for line_num, line in enumerate(f, 1):
                parts = line.strip().split()
                if len(parts) != 3:
                    raise ValueError(f"Line {line_num} in {txt_file} is malformed: {line.strip()}")

                name, charge, multiplicity = parts
                struct_dir = system_dir / name
                xyz_path = struct_dir / 'struc.xyz'
                if not xyz_path.exists():
                    raise FileNotFoundError(f"Missing: {xyz_path}")

                input_text = xyz_to_gamess_input(xyz_path, charge, multiplicity, title=name)

                # Create mirrored structure: all_gms_inputs/gms_input_format_SYSTEM/NAME/
                output_struct_dir = output_system_dir / name
                output_struct_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_struct_dir / f"{name}.inp"
                output_path.write_text(input_text)

                print(f"Written: {output_path}")

if __name__ == "__main__":
    generate_all_inputs()
