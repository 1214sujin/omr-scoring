import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox

def close_app():
    is_running = False #####
    
    if is_running:
        if not messagebox.askyesno('종료',
                                   '작업 중입니다. 정말 종료하시겠습니까?'):
            return
    window.destroy()


class FilePattern:
    def __init__(self, root, type_, msg):
        self.filepath = tk.StringVar()
        if type_=='pdf':
            self.type_tuple = ("PDF", "*.pdf")
        elif type_=='excel':
            self.type_tuple = ("Excel (.xlsx)", "*.xlsx")

        label = ttk.Label(root, text=msg)
        entry = ttk.Entry(root, textvariable=self.filepath)
        entry.state(['readonly'])
        button = ttk.Button(root,text='파일 찾기', command=self.open_file)

        label.pack(side='left', padx=5)
        entry.pack(side='left', fill='x', expand=True)
        button.pack(side='left', padx=5)

    def open_file(self):
        self.filepath.set(filedialog.askopenfilename(filetypes=[self.type_tuple]))

    def getStringVar(self):
        return self.filepath

def on_sec_checkbox_toggle():
    if section_on.get():
        section_numbox.state(['!disabled'])
    else:
        section_numbox.state(['disabled'])

def on_reset_button():
    subject_name.set('')
    section_on.set(False)
    section.set(1)
    section_numbox.state(['disabled'])
    scanfile.getStringVar().set('')
    students.getStringVar().set('')
    corrects.getStringVar().set('')


def append_log(msg):
    prog_log.config(state='normal')
    prog_log.insert('end', msg + '\n')
    prog_log.config(state='disabled')
    prog_log.see('end')

def on_start_button():
    is_running = False ####
    if is_running:
        messagebox.showwarning('새 작업 시작 불가',
                               '작업이 진행 중이므로 새 작업을 시작할 수 없습니다.')
        return

    if (subject_name.get().strip()==''
        or scanfile.getStringVar().get().strip()==''
        or students.getStringVar().get().strip()==''
        or corrects.getStringVar().get().strip()==''):
        
        messagebox.showwarning('새 작업 시작 불가',
                               '비어있는 항목을 확인해주세요.')
        return
    
    msg = '작업을 시작했다고 치자.' #####
    append_log(msg)


window = tk.Tk()
window.title('OMR 채점기')

##### 입력 영역 #####
find_frame = ttk.Frame(window)

####= 교과목 =####
row_subject = ttk.Frame(find_frame)

subject_label = ttk.Label(row_subject, text='채점 교과목명:')
subject_name = tk.StringVar()
subject_input = ttk.Entry(row_subject, width=30,
                          textvariable=subject_name)
section_on = tk.IntVar(value=0)
section_checkbox = ttk.Checkbutton(row_subject, text='분반',
                                   variable=section_on,
                                   command=on_sec_checkbox_toggle)
section = tk.BooleanVar(value=False)
section_numbox = ttk.Spinbox(row_subject, from_=1, to=50, width=5,
                             textvariable=section)
section_numbox.state(['disabled'])

subject_label.pack(side='left', padx=5)
subject_input.pack(side='left', fill='x', expand=True)
ttk.Frame(row_subject).pack(side='left', padx=5)
section_checkbox.pack(side='left')
section_numbox.pack(side='left', padx=5)

####= 답안지 =####
row_scanfile = ttk.Frame(find_frame)

scanfile = FilePattern(row_scanfile, 'pdf', '답안지 스캔 파일:')


####= 수강생 =####
row_students = ttk.Frame(find_frame)

students = FilePattern(row_students, 'excel', '수강생 명단:')


####= 정답지 =####
row_corrects = ttk.Frame(find_frame)

corrects = FilePattern(row_corrects, 'excel', '정답지 파일:')


row_subject.pack(fill='x', pady=5)
row_scanfile.pack(fill='x', pady=(0,5))
row_students.pack(fill='x', pady=(0,5))
row_corrects.pack(fill='x')
find_frame.pack(fill='both', pady=5)
##### 입력 영역 종료 #####

####= 버튼 =####
row_buttons = ttk.Frame(find_frame)
reset_button = ttk.Button(row_buttons, text='초기화',
                          command=on_reset_button)

start_button = ttk.Button(row_buttons, text='채점 시작',
                          command=on_start_button)

end_button = ttk.Button(row_buttons, text="종료", command=close_app)
reset_button.pack(side='left', anchor='center', padx=5)
start_button.pack(side='left', anchor='center', padx=5)
end_button.pack(side='left', anchor='center', padx=5)

row_buttons.pack(padx=10, pady=10)


ttk.Separator(master=window, orient='horizontal').pack(fill='x')

##### 진행 상태 출력 영역 #####
prog_frame = ttk.Frame(window)

prog_label = ttk.Label(prog_frame, text='진행 상태 상세보기')
prog_log = tk.Text(prog_frame, height=10, state='disabled')
scrollbar = ttk.Scrollbar(prog_frame)
scrollbar.config(command=prog_log.yview)

prog_label.pack(anchor='w')
scrollbar.pack(side="right", fill="y")
prog_log.pack(fill='both', padx=(5,0), pady=(5,0))

prog_frame.pack(fill='both', padx=5, pady=10)
##### 출력 영역 종료 #####

window.protocol('WM_DELETE_WINDOW', close_app)
window.mainloop()
