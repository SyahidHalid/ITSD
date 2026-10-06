#   !pip install tkinter --trusted-host pypi.org --trusted-host files.pythonhosted.org
#   !python.exe -m pip install --upgrade pip

import tkinter as tk
from tkinter import ttk, messagebox

class CCPTApp:

    def __init__(self, root):
        self.root = root
        self.root.title("EXIM Bank CCPT Assessment")
        self.root.geometry("1000x700")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.create_intro_tab()
        self.create_gp12_tab()
        self.create_gp34_tab()
        self.create_gp5_tab()
        self.create_summary_tab()

    # ==========================
    # INTRO
    # ==========================

    def create_intro_tab(self):
        self.intro_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.intro_frame, text="Intro")

        labels = [
            "Customer Name",
            "CIF Number",
            "Account Number",
            "Sector",
            "Principal Activities",
            "Business Location",
            "Type of Financing",
            "Purpose of Financing"
        ]

        self.intro_entries = {}

        for row, label in enumerate(labels):
            ttk.Label(self.intro_frame, text=label).grid(
                row=row,
                column=0,
                padx=10,
                pady=5,
                sticky="w"
            )

            entry = ttk.Entry(self.intro_frame, width=80)
            entry.grid(
                row=row,
                column=1,
                padx=10,
                pady=5
            )

            self.intro_entries[label] = entry

    # ==========================
    # GP1 GP2
    # ==========================

    def create_gp12_tab(self):
        self.gp12_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gp12_frame, text="GP1 & GP2")

        self.gp1_var = tk.StringVar(value="No")
        self.gp2_var = tk.StringVar(value="No")

        ttk.Label(
            self.gp12_frame,
            text="GP1 - Climate Change Mitigation"
        ).pack(anchor="w", padx=20, pady=10)

        ttk.Combobox(
            self.gp12_frame,
            textvariable=self.gp1_var,
            values=["Yes", "No"],
            state="readonly"
        ).pack(anchor="w", padx=20)

        ttk.Label(
            self.gp12_frame,
            text="GP2 - Climate Change Adaptation"
        ).pack(anchor="w", padx=20, pady=10)

        ttk.Combobox(
            self.gp12_frame,
            textvariable=self.gp2_var,
            values=["Yes", "No"],
            state="readonly"
        ).pack(anchor="w", padx=20)

    # ==========================
    # GP3 GP4
    # ==========================

    def create_gp34_tab(self):
        self.gp34_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gp34_frame, text="GP3 & GP4")

        self.gp3_var = tk.StringVar(value="No")
        self.gp4_var = tk.StringVar(value="No")

        ttk.Label(
            self.gp34_frame,
            text="GP3 Significant Harm Identified?"
        ).pack(anchor="w", padx=20, pady=10)

        ttk.Combobox(
            self.gp34_frame,
            textvariable=self.gp3_var,
            values=["Yes", "No"],
            state="readonly"
        ).pack(anchor="w", padx=20)

        ttk.Label(
            self.gp34_frame,
            text="GP4 Remedial Measures Available?"
        ).pack(anchor="w", padx=20, pady=10)

        ttk.Combobox(
            self.gp34_frame,
            textvariable=self.gp4_var,
            values=["Yes", "No"],
            state="readonly"
        ).pack(anchor="w", padx=20)

    # ==========================
    # GP5
    # ==========================

    def create_gp5_tab(self):
        self.gp5_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.gp5_frame, text="GP5")

        self.gp5_var = tk.StringVar(value="No")

        ttk.Label(
            self.gp5_frame,
            text="Prohibited Activities?"
        ).pack(anchor="w", padx=20, pady=10)

        ttk.Combobox(
            self.gp5_frame,
            textvariable=self.gp5_var,
            values=["Yes", "No"],
            state="readonly"
        ).pack(anchor="w", padx=20)

    # ==========================
    # SUMMARY
    # ==========================

    def create_summary_tab(self):

        self.summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.summary_frame, text="Summary")

        btn = ttk.Button(
            self.summary_frame,
            text="Generate Summary",
            command=self.generate_summary
        )
        btn.pack(pady=20)

        self.summary_text = tk.Text(
            self.summary_frame,
            height=20,
            width=100
        )
        self.summary_text.pack()

    def generate_summary(self):

        gp1 = self.gp1_var.get()
        gp2 = self.gp2_var.get()
        gp3 = self.gp3_var.get()
        gp4 = self.gp4_var.get()
        gp5 = self.gp5_var.get()

        # CCPT Classification Logic

        if gp5 == "Yes":
            classification = "C5b - Watchlist"

        elif (gp1 == "Yes" or gp2 == "Yes") and gp3 == "No":
            classification = "C1 - Climate Supporting"

        elif (gp1 == "Yes" or gp2 == "Yes") and gp3 == "Yes" and gp4 == "Yes":
            classification = "C2 - Transitioning"

        elif gp3 == "Yes" and gp4 == "Yes":
            classification = "C3"

        elif gp3 == "Yes" and gp4 == "No":
            classification = "C5a"

        else:
            classification = "C4"

        self.summary_text.delete("1.0", tk.END)

        self.summary_text.insert(
            tk.END,
            "===== CCPT SUMMARY =====\n\n"
        )

        self.summary_text.insert(
            tk.END,
            f"Customer : {self.intro_entries['Customer Name'].get()}\n"
        )

        self.summary_text.insert(
            tk.END,
            f"CIF Number : {self.intro_entries['CIF Number'].get()}\n"
        )

        self.summary_text.insert(
            tk.END,
            f"GP1 : {gp1}\n"
        )

        self.summary_text.insert(
            tk.END,
            f"GP2 : {gp2}\n"
        )

        self.summary_text.insert(
            tk.END,
            f"GP3 : {gp3}\n"
        )

        self.summary_text.insert(
            tk.END,
            f"GP4 : {gp4}\n"
        )

        self.summary_text.insert(
            tk.END,
            f"GP5 : {gp5}\n\n"
        )

        self.summary_text.insert(
            tk.END,
            f"OVERALL CCPT CLASSIFICATION : {classification}"
        )

        messagebox.showinfo(
            "Completed",
            f"Assessment classified as {classification}"
        )

root = tk.Tk()
app = CCPTApp(root)
root.mainloop()

#   Run in terminal

#   !pip install pyinstaller --trusted-host pypi.org --trusted-host files.pythonhosted.org

#   pyinstaller --onefile tkinter-ccpt.py