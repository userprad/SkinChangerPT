import customtkinter as ctk
import json
import shutil
import os

from tkinter import messagebox
from PIL import Image

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None

        widget.bind("<Button-1>", self.show_tooltip)  # agora só aparece no clique
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip is not None:
            return

        self.tooltip = ctk.CTkToplevel()
        self.tooltip.overrideredirect(True)
        self.tooltip.attributes("-topmost", True)

        # posição perto do "?"
        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + 25
        self.tooltip.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(
            self.tooltip,
            text=self.text,
            fg_color="#202020",
            text_color="white",
            corner_radius=6,
            padx=10,
            pady=5,
        )
        label.pack()

        # se tirar o mouse do tooltip também fecha
        self.tooltip.bind("<Leave>", self.hide_tooltip)

    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

# ===== CAMINHOS DO JOGO =====
PASTA_GAME_SMD = r"C:\Zenit Games\Priston Tale Brasil Reloaded (Beta)\image\Sinimage\Items\DropItem"
PASTA_GAME_BMP = r"C:\Zenit Games\Priston Tale Brasil Reloaded (Beta)\image\Sinimage\Items\Weapon"
PASTA_GAME_DEF = r"C:\Zenit Games\Priston Tale Brasil Reloaded (Beta)\image\Sinimage\Items\Defense"

# ===== CAMINHOS LOCAIS DO PROGRAMA =====
PASTA_ITEMS = r"./ItemsPack"   # .smd de origem
PASTA_IMG   = r"./Images"      # .png preview
#
# Carregar itens
with open("items.json", "r", encoding="utf-8") as file:
    categorias = json.load(file)

lista_categorias = list(categorias.keys())

# ===== Função para carregar imagem com tamanho fixo sem distorcer =====
def carregar_imagem(nome_arquivo, frame_preview, label_img):
    base = nome_arquivo.replace(".smd", ".bmp")
    caminho = os.path.join(PASTA_IMG, base)

    TAMANHO = (50, 90)

    if os.path.exists(caminho):
        img = Image.open(caminho)
        img.thumbnail(TAMANHO, Image.LANCZOS)

        imgCTK = ctk.CTkImage(img, size=TAMANHO)
        label_img.configure(image=imgCTK, text="")
        label_img.image = imgCTK
    else:
        label_img.configure(image="", text="Sem imagem")

# Atualizações dos combos
def atualizar_itens_atual(_=None):
    cat = box_cat_atual.get()
    box_atual.configure(values=list(categorias[cat].keys()))
    box_atual.set("")
    img_atual.configure(image="", text="")

def atualizar_itens_novo(_=None):
    cat = box_cat_novo.get()
    box_novo.configure(values=list(categorias[cat].keys()))
    box_novo.set("")
    img_novo.configure(image="", text="")

def selecionar_item_atual(_=None):
    cat = box_cat_atual.get()
    item = box_atual.get()
    if item:
        carregar_imagem(categorias[cat][item], frame_img_left, img_atual)

def selecionar_item_novo(_=None):
    cat = box_cat_novo.get()
    item = box_novo.get()
    if item:
        carregar_imagem(categorias[cat][item], frame_img_right, img_novo)


# Funções rápidas para Escudos
def set_categoria_escudos_atual():
    # define a categoria Atual como Escudos e atualiza a lista
    box_cat_atual.set("Escudos")
    atualizar_itens_atual()

def set_categoria_escudos_novo():
    # define a categoria Novo como Escudos e atualiza a lista
    box_cat_novo.set("Escudos")
    atualizar_itens_novo()



# ===== Função de troca agora move .smd e .bmp =====
def trocar_itens():
    cat_atual = box_cat_atual.get()
    cat_novo  = box_cat_novo.get()

    item_atual = box_atual.get()
    item_novo  = box_novo.get()

    if not item_atual or not item_novo:
        messagebox.showwarning("Atenção!", "Selecione os dois itens!")
        return

    arq_atual = categorias[cat_atual][item_atual]  # ex: itWA101.smd
    arq_novo  = categorias[cat_novo][item_novo]

    base_atual = arq_atual.replace(".smd", "")
    base_novo  = arq_novo.replace(".smd", "")

    # Caminhos de ORIGEM (seu pack)
    origem_smd = os.path.join(PASTA_ITEMS, arq_novo)
    origem_bmp = os.path.join(PASTA_IMG, base_novo + ".bmp")

    # Caminhos do JOGO (onde será substituído)
    destino_smd = os.path.join(PASTA_GAME_SMD, arq_atual)
    # para armaduras/escudos o BMP vai para a pasta Defense; para armas usa Weapon
    if cat_atual == "Escudos":
        destino_bmp = os.path.join(PASTA_GAME_DEF, base_atual + ".bmp")
    else:
        destino_bmp = os.path.join(PASTA_GAME_BMP, base_atual + ".bmp")

    if not os.path.exists(origem_smd):
        messagebox.showerror("Erro", f"SMD não encontrado:\n{origem_smd}")
        return

    try:
        # Backup SMD
        if os.path.exists(destino_smd):
            shutil.copy(destino_smd, destino_smd + ".backup")

        # Copiar arquivos novos
        shutil.copy(origem_smd, destino_smd)

        if os.path.exists(origem_bmp):
            shutil.copy(origem_bmp, destino_bmp)

        # ⬇ GRAVA O LOG DA TROCA
        salvar_log(item_atual, item_novo)

        messagebox.showinfo("Sucesso!", f"{item_atual} foi substituído por {item_novo}.\n\n")

    except Exception as e:
        messagebox.showerror("Erro na troca", str(e))


# ===== INTERFACE =====
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()
app.title("Skin Changer PT")
app.geometry("350x250")
app.resizable(False, False)

frame_left  = ctk.CTkFrame(app)
frame_right = ctk.CTkFrame(app)
frame_left.pack(side="left", padx=10, pady=10, fill="y")
frame_right.pack(side="right", padx=10, pady=10, fill="y")

# Esquerda
ctk.CTkLabel(frame_left, text="Item Equipado", font=("Arial", 15, "bold")).pack()
frame_cat_atual = ctk.CTkFrame(frame_left, fg_color="transparent")
frame_cat_atual.pack(pady=5, fill="x")
box_cat_atual = ctk.CTkComboBox(frame_cat_atual, values=lista_categorias, command=atualizar_itens_atual)
box_cat_atual.pack(side="left", expand=True, fill="x")
box_cat_atual.set("Selecione a categoria")

box_atual = ctk.CTkComboBox(frame_left, values=[], command=selecionar_item_atual)
box_atual.pack(pady=5)
box_atual.set("Selecione o item")

# ---- FRAME DO PREVIEW ESQUERDO ----
frame_img_left = ctk.CTkFrame(frame_left, width=60, height=100, corner_radius=12, fg_color="#1A1A1A")
frame_img_left.pack(pady=10)
frame_img_left.pack_propagate(False)

img_atual = ctk.CTkLabel(frame_img_left, text="Sem \r imagem")
img_atual.pack(expand=True)

# Direita
ctk.CTkLabel(frame_right, text="Skin a Aplicar", font=("Arial", 15, "bold")).pack()
frame_cat_novo = ctk.CTkFrame(frame_right, fg_color="transparent")
frame_cat_novo.pack(pady=5, fill="x")
box_cat_novo = ctk.CTkComboBox(frame_cat_novo, values=lista_categorias, command=atualizar_itens_novo)
box_cat_novo.pack(side="left", expand=True, fill="x")
box_cat_novo.set("Selecione uma categoria")

box_novo = ctk.CTkComboBox(frame_right, values=[], command=selecionar_item_novo)
box_novo.pack(pady=5)
box_novo.set("Selecione um item")

# ---- FRAME DO PREVIEW DIREITO
frame_img_right = ctk.CTkFrame(frame_right, width=60, height=100, corner_radius=12, fg_color="#1A1A1A")
frame_img_right.pack(pady=10)
frame_img_right.pack_propagate(False)

img_novo = ctk.CTkLabel(frame_img_right, text="Sem \r imagem")
img_novo.pack(expand=True)

# Botão

# Botões rápidos agora inline ao lado das categorias

# Botão geral de troca
btn_trocar = ctk.CTkButton(app, text="⇄", command=trocar_itens, width=200, height=40)
btn_trocar.pack(pady=(4, 4))

help_label = ctk.CTkLabel(app, text="?", font=("Arial", 18, "bold"), text_color="#888888")
help_label.pack()

Tooltip(help_label,
"Na Esquerda Selecione o item que você está Equipado\n"
"Na Direita o item (Skin) que deseja utilizar\n"
"Clique no botão ⇄ para realizar a troca\n"
"-Posso utilizar uma Skin de Foice no Lugar do Machado?\n"
"Sim! Você pode usar qualquer Skin em qualquer arma!\n"
"mas lembre-se que o modelo 3D pode não combinar com a arma.\n"
"Ex: usar uma Skin de Arco no Lugar da Lança pode ficar estranho..."
)


from datetime import datetime

def salvar_log(item_antigo, item_novo):
    horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linha = f"[{horario}] Trocado: {item_antigo} => {item_novo}\n"

    with open("trocas.log", "a", encoding="utf-8") as log:
        log.write(linha)


app.mainloop()
