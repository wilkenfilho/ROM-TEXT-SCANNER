import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

# ==============================
# Funções de leitura de TBL
# ==============================
def carregar_tbl(caminho_tbl):
    tabela = {}
    if not caminho_tbl or not os.path.exists(caminho_tbl):
        return tabela
    with open(caminho_tbl, "r", encoding="utf-8", errors="ignore") as f:
        for linha in f:
            if "=" in linha:
                hex_code, char = linha.strip().split("=", 1)
                try:
                    tabela[int(hex_code, 16)] = char
                except ValueError:
                    continue
    return tabela

# ==============================
# Detecção de texto legível
# ==============================
def detectar_texto(data, tabela=None):
    achados = []

    if tabela:
        decoded = ""
        for byte in data:
            decoded += tabela.get(byte, "")
        texto = decoded
        encoding = "TBL personalizada"
    else:
        for encoding in ("utf-8", "shift_jis", "latin1"):
            try:
                texto = data.decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            return achados

    # Expressão regular para palavras e frases simples em inglês
    for match in re.finditer(r"[A-Za-z0-9 ,.!?';:\-\"]{4,}", texto):
        achados.append((match.start(), match.group(), encoding))

    return achados

# ==============================
# Analisar ROM individual
# ==============================
def analisar_rom(caminho_arquivo, tabela=None):
    with open(caminho_arquivo, "rb") as f:
        data = f.read()

    resultados = detectar_texto(data, tabela)

    if resultados:
        nome = os.path.basename(caminho_arquivo)
        saida_nome = f"{os.path.splitext(nome)[0]}_textdump.txt"
        saida_caminho = os.path.join(os.path.dirname(caminho_arquivo), saida_nome)

        # Exporta o dump completo
        with open(saida_caminho, "w", encoding="utf-8") as out:
            out.write(f"Arquivo analisado: {nome}\n")
            out.write("=" * 60 + "\n\n")
            for addr, texto, enc in resultados:
                out.write(f"[0x{addr:08X}] ({enc}) {texto}\n")

        # Retorna amostras (máx. 5)
        amostras = [
            f"[0x{addr:08X}] ({enc}) {texto[:80]}"
            for addr, texto, enc in resultados[:5]
        ]
        return True, len(resultados), saida_caminho, amostras

    return False, 0, None, []

# ==============================
# Analisar pasta com múltiplos arquivos
# ==============================
def analisar_pasta(pasta, tabela=None, progress_callback=None):
    resultados = []
    arquivos = [
        os.path.join(root, f)
        for root, _, files in os.walk(pasta)
        for f in files
        if f.lower().endswith((".nds", ".bin", ".iso", ".dat", ".pak"))
    ]

    total = len(arquivos)
    for i, arquivo in enumerate(arquivos, 1):
        if progress_callback:
            progress_callback(i, total, arquivo)
        tem_texto, count, saida, amostras = analisar_rom(arquivo, tabela)
        if tem_texto:
            resultados.append((arquivo, count, saida, amostras))

    return resultados

# ==============================
# Interface Tkinter
# ==============================
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("ROM Text Scanner - Tradutores 🔍")
        self.geometry("800x600")
        self.configure(bg="#222")

        self.tbl_path = None

        # --- Label ---
        tk.Label(self, text="Arraste ou selecione uma pasta de ROMs:",
                 bg="#222", fg="#fff", font=("Segoe UI", 12)).pack(pady=10)

        # --- Área de drop ---
        self.drop_area = tk.Label(self, text="🗂️ Solte aqui uma pasta",
                                  bg="#333", fg="#ccc",
                                  width=60, height=5, relief="groove")
        self.drop_area.pack(pady=10)
        self.drop_area.bind("<Button-1>", self.selecionar_pasta)

        # --- Botão de tabela ---
        tk.Button(self, text="📄 Carregar .TBL (opcional)",
                  command=self.selecionar_tbl).pack(pady=5)

        # --- Barra de progresso ---
        self.progress = ttk.Progressbar(self, orient="horizontal", length=600, mode="determinate")
        self.progress.pack(pady=10)

        # --- Resultados ---
        self.text_output = tk.Text(self, bg="#111", fg="#0f0", height=18, width=90, wrap="word")
        self.text_output.pack(pady=10)

    def selecionar_pasta(self, event=None):
        pasta = filedialog.askdirectory()
        if pasta:
            self.text_output.delete("1.0", tk.END)
            self.text_output.insert(tk.END, f"🔍 Analisando pasta: {pasta}\n\n")
            self.progress["value"] = 0
            resultados = analisar_pasta(pasta, self.tbl_path, self.atualizar_progresso)

            if resultados:
                self.text_output.insert(tk.END, f"\n✅ Arquivos com texto detectado:\n\n")
                for caminho, count, saida, amostras in resultados:
                    self.text_output.insert(tk.END, f"📄 {os.path.basename(caminho)} ({count} trechos)\n")
                    for a in amostras:
                        self.text_output.insert(tk.END, f"    → {a}\n")
                    self.text_output.insert(tk.END, f"    🔸 Dump completo: {saida}\n\n")
            else:
                self.text_output.insert(tk.END, "\n🟥 Nenhum texto legível detectado.")
            messagebox.showinfo("Concluído", "Análise finalizada!")

    def selecionar_tbl(self):
        caminho = filedialog.askopenfilename(filetypes=[("Tabelas de caracteres", "*.tbl")])
        if caminho:
            self.tbl_path = carregar_tbl(caminho)
            messagebox.showinfo("Tabela carregada", f"Tabela personalizada carregada de:\n{caminho}")

    def atualizar_progresso(self, atual, total, arquivo):
        self.progress["value"] = (atual / total) * 100
        self.update_idletasks()
        self.text_output.insert(tk.END, f"Analisando {os.path.basename(arquivo)}...\n")
        self.text_output.see(tk.END)

# ==============================
# Execução principal
# ==============================
if __name__ == "__main__":
    app = App()
    app.mainloop()
