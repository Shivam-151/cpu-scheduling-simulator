import tkinter as tk
from gui import CPUSchedulingApp


def main():
    root = tk.Tk()
    app = CPUSchedulingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()