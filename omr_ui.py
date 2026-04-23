import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import subprocess
import re

class FilePattern:
    def __init__(self, root, type_, title):
        self.filepath = tk.StringVar()
        self.title=title

        if type_ == 'pdf':
            self.type_tuple = ("PDF", "*.pdf")
        elif type_ == 'excel':
            self.type_tuple = ("Excel files", "*.xlsx")

        frame = ttk.Frame(root)
        frame.pack(fill='x', pady=2)

        ttk.Label(frame, text=title+':').pack(side='left', padx=5)

        entry = ttk.Entry(frame, textvariable=self.filepath)
        entry.state(['readonly'])
        entry.pack(side='left', fill='x', expand=True)

        ttk.Button(frame, text='파일 찾기',
                   command=self.open_file).pack(side='left', padx=5)

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[self.type_tuple],
                                          title=self.title)
        if path:
            self.filepath.set(path)

    def get(self):
        return self.filepath.get()

    def reset(self):
        self.filepath.set('')


class OMRApp:

    INVALID_CHARS = r'[\\/:*?"<>|]'
    
    def __init__(self, root):
        self.root = root
        #self.on_start = on_start
        self.is_running = False

        root.title('OMR 채점기')
        root.protocol('WM_DELETE_WINDOW', self.close_app)

        # ===== 입력 영역 =====
        find_frame = ttk.Frame(root, padding=5)
        find_frame.pack(fill='x')

        # --- 교과목 ---
        row_subject = ttk.Frame(find_frame)
        row_subject.pack(fill='x', pady=5)

        ttk.Label(row_subject, text='채점 교과목명:').pack(side='left', padx=5)

        self.subject_name = tk.StringVar()
        ttk.Entry(row_subject, textvariable=self.subject_name, width=30, validate="key",
                  validatecommand=(row_subject.register(self.validate_filename), "%P"))\
            .pack(side='left', fill='x', expand=True)

        self.extra_on = tk.IntVar(value=False)
        extra_checkbox = ttk.Checkbutton(row_subject, text='주관식 점수 포함',
                                         variable=self.extra_on)\
                            .pack(side='left', padx=5)

        # --- 파일들 ---
        self.scanfile = FilePattern(find_frame, 'pdf', '답안지 스캔 파일')
        self.corrects = FilePattern(find_frame, 'excel', '정답지 파일')
        self.students = FilePattern(find_frame, 'excel', '수강생 명단')

        style = ttk.Style()
        style.configure('Warning.TLabel', foreground='red')

        ttk.Label(find_frame, text='※ 교과목명은 파일명에 사용 가능해야 합니다.'
                 + '\n※ 답안지는 .pdf, 정답지 및 수강명단은'
                 + '.xlsx만 가능합니다.', style='Warning.TLabel')\
                 .pack(side='left', padx=10)

        # ===== 입력 감도 조절 =====
        ratio_frame = ttk.Frame(root)
        ratio_frame.pack(fill='x', pady=(5,0))

        ttk.Label(ratio_frame, \
                  text='마킹 인식 감도(0~0.5):')\
                  .pack(side='left', padx=5)
        
        self.ratio_threshold = tk.DoubleVar(value=0.2)
        ttk.Spinbox(ratio_frame, textvariable=self.ratio_threshold,
                    from_=0, to=0.5, width=5, increment=0.01, state='readonly')\
                    .pack(side='left', padx=5)

        ttk.Label(ratio_frame, text='※ 작을수록 더 밝은 칸까지 마킹으로 판정합니다.',
                  style='Warning.TLabel')\
                  .pack(side='left', padx=10, fill='x', expand=True)

        # ===== 버튼 =====
        btn_frame = ttk.Frame(root)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text='초기화',
                   command=self.reset).pack(side='left', padx=5)

        ttk.Button(btn_frame, text='채점 시작',
                   command=self.start).pack(side='left', padx=5)

        ttk.Button(btn_frame, text='중지',
                   command=self.stop_app).pack(side='left', padx=5)

        ttk.Button(btn_frame, text='종료',
                   command=self.close_app).pack(side='left', padx=5)

        # ===== 구분선 =====
        ttk.Separator(root).pack(fill='x')

        # ===== 로그 =====
        prog_frame = ttk.Frame(root, padding=5)
        prog_frame.pack(fill='both', expand=True)

        ttk.Label(prog_frame, text='진행 상태 상세보기')\
                              .pack(padx=5, pady=5,anchor='w')

        self.prog_log = tk.Text(prog_frame, height=10,
                                state='disabled', wrap='word')

        scrollbar = ttk.Scrollbar(prog_frame, command=self.prog_log.yview)
        self.prog_log.config(yscrollcommand=scrollbar.set)

        scrollbar.pack(side='right', fill='y')
        self.prog_log.pack(padx=(5,0), pady=5, fill='both', expand=True)

    # ===== 기능 =====

    def validate_filename(self, new_value):
        if new_value == "":
            return True

        if re.search(self.INVALID_CHARS, new_value):
            return False

        if new_value.endswith(" ") or new_value.endswith("."):
            return False

        return True

    def reset(self):
        self.subject_name.set('')

        self.scanfile.reset()
        self.students.reset()
        self.corrects.reset()

    def append_log(self, msg):
        self.prog_log.config(state='normal')
        self.prog_log.insert('end', msg + '\n')
        self.prog_log.config(state='disabled')
        self.prog_log.see('end')

    def read_log(self):
        for line in self.proc.stdout:
            self.append_log(line.strip())
        self.is_running = False

    def start(self):

        if self.is_running:
            messagebox.showwarning('불가', '작업이 진행 중입니다.')
            return

        if (not self.subject_name.get().strip()
                or not self.scanfile.get()
                or not self.students.get()
                or not self.corrects.get()):

            messagebox.showwarning('불가', '비어있는 항목이 있습니다.')
            return
        
        self.is_running = True

        self.proc = subprocess.Popen(
            ['python', 'omr_worker.py',
             self.subject_name.get(),
             str(self.extra_on.get()),
             self.scanfile.get(),
             self.students.get(),
             self.corrects.get(),
             str(self.ratio_threshold.get())
             ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        threading.Thread(target=self.read_log, daemon=True).start()

    def stop_app(self):
        if self.is_running:
            if not messagebox.askokcancel(
                '채점 중지',
                '작업을 중지하시겠습니까?'
            ):
                return
        
            self.proc.kill()
            self.is_running = False
            self.append_log('===== 중지됨 =====\n')

    def close_app(self):
        if self.is_running:
            if not messagebox.askyesno(
                '종료',
                '작업 중입니다. 앱을 종료하시겠습니까?'
            ):
                return

        self.root.destroy()
