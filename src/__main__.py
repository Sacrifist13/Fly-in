from .parser import Parser


reader = Parser("maps/easy/01_linear_path.txt")

if not reader.create_map_data():
    print("Error")
