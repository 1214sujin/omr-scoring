from tkinter import Tk

from omr_ui import OMRApp

def main():

    window = Tk()

    app = OMRApp(window)
    
    window.mainloop()


if __name__ == '__main__':
    main()
