import os
from qrcode.main import QRCode

path_main = os.path.dirname(os.path.abspath(__file__))
path_qr_dir = os.path.join(path_main, "..", "QRIMGDATA", "Scan.png")

qr = QRCode(version=3, box_size=20, border=2)

def crear_qr_data(qr_data):
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color=(0, 0, 0), back_color=(255, 255, 255))
    img.save(path_qr_dir)