import os
import sys
import zlib
from base64 import b85encode

filenames = ['background.png', 'check.png', 'cross.png', 'empty.png']
_COLOR = {0: "club", 1: "diamond", 2: "heart", 3: "spade"}
for i in range(4):
    for j in range(2, 15):
        filenames.append(f"{_COLOR[i]}_{j}.png")


def compress_png_files(directory):
    total_size = 0
    output_dict = {}
    for filename in filenames:
        file_path = os.path.join(directory, filename)
        with open(file_path, 'rb') as f:
            file_data = f.read()
        compressed_data = zlib.compress(file_data, level=9)
        a85_data = b85encode(compressed_data)
        output_dict[filename] = a85_data
        total_size += len(a85_data)
    print(total_size, file=sys.stderr)
    return output_dict


output = compress_png_files('./')
# print as if dictionary
with open('../imgs.py', 'w') as file:
    file.write("imgs = {\n")
    for key, value in output.items():
        file.write(f'    "{key}": "{value.decode()}",\n')
    file.write("}\n")
    file.write("""
from base64 import b64encode, b85decode
import zlib

for img_name, img in imgs.items():
    img_data = b85decode(img)
    img_data = zlib.decompress(img_data)
    img_data = b64encode(img_data)
    imgs[img_name] = img_data
""")
