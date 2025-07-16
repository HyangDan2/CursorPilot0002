from PySide6.QtWidgets import QApplication
import sys
from sources.halo_pattern_generator import HaloPatternGenerator

def main():
    app = QApplication(sys.argv)
    window = HaloPatternGenerator()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main() 