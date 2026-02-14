from .parser import Parser


reader = Parser("maps/easy/01_linear_path.txt")

print(reader.format_data_for_pydantic())
