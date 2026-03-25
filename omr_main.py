from tkinter import Tk

from omr_ui import OMRApp

def main():

    window = Tk()

    app = OMRApp(window)
    
    window.mainloop()


if __name__ == '__main__':
    main()

#input('종료하려면 Enter를 누르세요.')


