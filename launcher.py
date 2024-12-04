import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import subprocess
import os
import config
import datetimeutil
import datetime


def get_period(option: str):
    start, end = datetimeutil.get_start_and_end_day_2(
        datetime.datetime.now(), config.RECALL_INTERVAL_MONTHS, int(option)
    )
    return start.strftime("%Y/%m/%d") + "~" + end.strftime("%d")


def show_option_menu():
    # Tkinterのルートウィンドウを作成
    root = tk.Tk()
    root.title("Select Option")

    # プルダウンメニューの選択肢
    options = [-1, 0, 1]
    selected_option = tk.StringVar(root)
    selected_option.set(options[1])  # デフォルトで0を選択

    # OptionMenuの作成
    option_menu = tk.OptionMenu(root, selected_option, *options)
    option_menu.pack(pady=10)

    # 選択結果表示
    selected_label = tk.Label(
        root,
        text=f"選択範囲: {get_period(selected_option.get())}",
    )
    selected_label.pack(pady=10)

    # 選択肢が変更された時に表示を更新する
    def update_label(*args):
        selected_label.config(
            text=f"選択範囲: {get_period(selected_option.get())}",
        )

    selected_option.trace("w", update_label)

    # 次にファイル選択ダイアログを開く
    def open_file_dialog():
        # 実行フォルダをデフォルトの表示場所に設定
        initial_dir = os.getcwd()  # 現在の作業ディレクトリを取得

        # ファイル選択ダイアログを開く
        file_path = filedialog.askopenfilename(
            title="Select a file", initialdir=initial_dir
        )

        # 選択されたファイルのパスを表示
        if file_path:
            print(f"Selected file: {file_path}")
            run_python_script(file_path, selected_option.get(), root)
        else:
            print("No file selected.")

    # 実行ボタンの作成
    execute_button = tk.Button(
        root, text="Select File and Execute", command=open_file_dialog
    )
    execute_button.pack(pady=10)

    root.mainloop()


def run_python_script(file_path, selected_option, root):
    # 'python main.py {fullpath} {selected_option}' を実行
    command = ["python", "main.py", file_path, selected_option]

    try:
        # プロセスを実行
        subprocess.run(command, check=True)
        messagebox.showinfo("Success", "Python script executed successfully.")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"Error executing script: {e}")
    root.quit()


# 実行
show_option_menu()
