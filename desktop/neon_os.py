import os
import threading
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from core.module_registry import ModuleRegistry
from core.providers import NeonProviders

ROOT = os.path.dirname(os.path.abspath(__file__))
MODULES = ["Pulsar AI", "Infinity OS", "EXO", "Ember", "AEGIS / ASTER"]

class NeonDesktop(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("NEON OS Desktop")
        self.geometry("1180x760")
        self.minsize(900, 620)
        self.configure(bg="#050711")
        self.providers = NeonProviders()
        self.registry = ModuleRegistry(ROOT)
        self.route = tk.StringVar(value="fast")
        self._build()

    def _build(self):
        header = tk.Frame(self, bg="#070b16", height=68)
        header.pack(fill="x")
        tk.Label(header, text="NEON OS", fg="#6cecff", bg="#070b16", font=("Segoe UI", 21, "bold")).pack(side="left", padx=24, pady=17)
        tk.Label(header, text="DESKTOP • VOID × HORIZON • AI CORE", fg="#8f9db5", bg="#070b16", font=("Segoe UI", 9)).pack(side="left", pady=22)
        tk.Button(header, text="Provider Status", command=self.show_provider_status, bg="#11182b", fg="white", bd=0, padx=14, pady=8).pack(side="right", padx=20)

        body = tk.Frame(self, bg="#050711")
        body.pack(fill="both", expand=True)
        left = tk.Frame(body, bg="#080c18", width=280)
        left.pack(side="left", fill="y", padx=(14, 8), pady=14)
        left.pack_propagate(False)
        right = tk.Frame(body, bg="#050711")
        right.pack(side="left", fill="both", expand=True, padx=(8, 14), pady=14)

        tk.Label(left, text="BUILT-IN SYSTEMS", fg="#8796ad", bg="#080c18", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(18, 10))
        for name in MODULES:
            box = tk.Frame(left, bg="#10172a", highlightbackground="#1d2943", highlightthickness=1)
            box.pack(fill="x", padx=12, pady=5)
            tk.Label(box, text=name, fg="white", bg="#10172a", font=("Segoe UI", 11, "bold")).pack(anchor="w", padx=12, pady=(10, 2))
            state = self.registry.status(name)
            tk.Label(box, text=state, fg="#76e9ff" if state == "ready" else "#f1c980", bg="#10172a", font=("Segoe UI", 8)).pack(anchor="w", padx=12)
            tk.Button(box, text="Open", command=lambda n=name: self.launch_module(n), bg="#17213a", fg="white", bd=0, padx=9, pady=5).pack(anchor="e", padx=10, pady=(2, 9))

        top = tk.Frame(right, bg="#0b1020", highlightbackground="#1c2943", highlightthickness=1)
        top.pack(fill="x")
        tk.Label(top, text="NEON AI CONSOLE", fg="white", bg="#0b1020", font=("Segoe UI", 13, "bold")).pack(side="left", padx=16, pady=13)
        for label, value in [("Fast", "fast"), ("Reasoning", "reasoning"), ("Coding", "coding")]:
            tk.Radiobutton(top, text=label, variable=self.route, value=value, indicatoron=False, bg="#11182b", fg="white", selectcolor="#3b3b8f", activebackground="#16213b", activeforeground="white", bd=0, padx=10, pady=5).pack(side="right", padx=3, pady=10)

        self.chat = ScrolledText(right, bg="#070b15", fg="#dfe9f7", insertbackground="white", bd=0, wrap="word", font=("Segoe UI", 10), padx=14, pady=14)
        self.chat.pack(fill="both", expand=True, pady=(10, 10))
        self.chat.insert("end", "NEON OS Desktop is running.\nShared providers: " + self.providers.status() + "\n\n")
        self.chat.configure(state="disabled")

        compose = tk.Frame(right, bg="#050711")
        compose.pack(fill="x")
        self.prompt = tk.Entry(compose, bg="#10172a", fg="white", insertbackground="white", bd=0, font=("Segoe UI", 11))
        self.prompt.pack(side="left", fill="x", expand=True, ipady=11, padx=(0, 8))
        self.prompt.bind("<Return>", lambda _e: self.send())
        tk.Button(compose, text="Send", command=self.send, bg="#66e7ff", fg="#061018", bd=0, font=("Segoe UI", 10, "bold"), padx=22, pady=11).pack(side="right")

    def log(self, role, text):
        self.chat.configure(state="normal")
        self.chat.insert("end", f"{role}\n{text}\n\n")
        self.chat.see("end")
        self.chat.configure(state="disabled")

    def send(self):
        text = self.prompt.get().strip()
        if not text:
            return
        self.prompt.delete(0, "end")
        self.log("YOU", text)
        threading.Thread(target=self._ask, args=(text, self.route.get()), daemon=True).start()

    def _ask(self, text, route):
        try:
            answer = self.providers.chat(text, route)
        except Exception as exc:
            answer = f"Provider error: {exc}"
        self.after(0, lambda: self.log("NEON", answer))

    def launch_module(self, name):
        try:
            self.registry.launch(name)
            self.log("SYSTEM", f"Opened {name}.")
        except Exception as exc:
            messagebox.showinfo("NEON OS", str(exc))

    def show_provider_status(self):
        messagebox.showinfo("NEON Provider Nexus", self.providers.status())

if __name__ == "__main__":
    NeonDesktop().mainloop()
