import pandas as pd
import os

EXCEL_FILE = "juegos_final.xlsx"
OUTPUT_HTML = "index.html"
WHATSAPP_NUM = "+5492944907380"  # tu número
CARPETA_IMAGENES = "caratulas/"

# Usar número sin + para wa.me
WA_NUM = WHATSAPP_NUM.lstrip("+")

df = pd.read_excel(EXCEL_FILE)

# Validación de columnas
for col in ["Nombre", "Categoria", "Precio_Normal", "Precio_Oferta", "Alias", "Disponible"]:
    if col not in df.columns:
        raise ValueError(f"Falta la columna '{col}' en la planilla.")

df = df.sort_values("Nombre")


# ---------------------------------------
# GENERADOR DE ALIAS EXTRAS INTELIGENTES
# ---------------------------------------

def generar_alias_extra(nombre):
    n = nombre.lower()
    alias = []

    # Deportes
    if "fifa" in n:
        alias += ["fifa", "futbol", "soccer"]

    if "pro evolution" in n or "winning eleven" in n or "pes" in n:
        alias += ["pes", "pro", "futbol", "soccer"]

    # Disparos
    if "call of duty" in n:
        alias += ["cod", "duty"]

    if "medal of honor" in n:
        alias += ["moh"]

    if "resident evil" in n:
        alias += ["re", "resident"]

    # Lucha
    if "mortal kombat" in n:
        alias += ["mk", "mortal", "kombat"]

    if "tekken" in n:
        alias += ["tkn", "tekken"]

    # Acción / Aventura
    if "god of war" in n:
        alias += ["gow", "godwar", "god"]

    if "naruto" in n:
        alias += ["naruto", "nar", "shinobi"]

    if "dragon ball" in n:
        alias += ["dbz", "dragonball", "db", "tenkaichi", "bt3"]

    # Autos / carreras
    if (
        "need for speed" in n or
        "gran turismo" in n or
        "midnight club" in n or
        "rally" in n or
        "mx vs atv" in n or
        "colin" in n or
        "outrun" in n or
        "motorstorm" in n or
        "test drive" in n or
        "wrc" in n or
        "bike" in n or
        "kart" in n or
        "race" in n or
        "driver" in n or
        "motogp" in n or
        "f1" in n
    ):
        alias += [
            "auto", "autos",
            "carrera", "carreras",
            "racing", "race",
            "rally",
            "moto", "motor", "motos",
            "bike", "bikes",
            "speed", "drive", "drift",
            "gt", "vehiculo", "vehiculos",
            "conduccion"
        ]

    # GTA
    if "grand theft auto" in n or "gta" in n:
        alias += ["gta", "sanandreas", "gta sa", "san"]

    return " ".join(alias)


# -----------------------------
#  HTML BASE
# -----------------------------

html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Almacén Copihue – Juegos PS2</title>

<style>
body {{ background:#111; color:#fff; margin:0; font-family:Arial; }}
header {{ background:#222; padding:20px; text-align:center; border-bottom:2px solid #a00; position:sticky; top:0; }}
.title {{ font-size:26px; font-weight:bold; color:#e33; margin-bottom:12px; }}
#searchInput, #categoryFilter {{ padding:10px; width:180px; border-radius:5px; border:none; margin:5px; }}

.games-grid {{
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 18px;
    padding: 15px;
}}

.game-card {{
    background:#1d1d1d;
    border-radius:10px;
    overflow:hidden;
    box-shadow:0 0 10px #000;
    transition:.2s;
    width:180px;
    position:relative;
}}

.game-card:hover {{ transform:scale(1.03); }}

.game-cover {{
    width: 100%;
    aspect-ratio: 400 / 267;
    object-fit: cover;
}}

.game-card.no-disponible .game-cover {{
    filter: grayscale(80%) brightness(50%);
}}

.no-disponible-text {{
    background:#c00;
    color:white;
    font-weight:bold;
    text-align:center;
    padding:5px;
    margin-top:5px;
    border-radius:5px;
}}

.game-info {{ padding:10px; }}

.game-title {{ font-size:16px; font-weight:bold; color:#f44; margin-bottom:6px; }}
.game-category {{ font-size:12px; color:#bbb; margin-bottom:6px; }}

.price-line {{ color:#ddd; font-size:14px; margin-bottom:4px; }}
.price-oferta {{ color:#ff0; font-size:15px; font-weight:bold; }}

.buttons-row {{
    display:flex;
    gap:6px;
    margin-top:8px;
    flex-wrap:wrap;
}}

.btn-uno, .btn-dos {{
    flex:1;
    padding:6px;
    border-radius:6px;
    border:none;
    cursor:pointer;
    font-size:13px;
    text-align:center;
    font-weight:bold;
}}

.btn-uno {{
    background:#444;
    color:#fff;
    text-decoration:none;
}}

.btn-dos {{
    background:#e33;
    color:#fff;
}}

.btn-dos.selected {{
    background:#ff8800;
}}

/* BOTÓN VOLVER ARRIBA */
#btnTop {{
    position: fixed;
    bottom: 25px;
    right: 25px;
    background: #e33;
    color: #fff;
    border: none;
    padding: 12px 15px;
    border-radius: 50%;
    font-size: 20px;
    cursor: pointer;
    box-shadow: 0 0 10px #000;
    display: none;
    z-index: 999;
    transition: 0.3s;
}}

#btnTop:hover {{
    background: #ff4444;
}}

/* BARRA OFERTA 2 x 10000 */
#ofertaBar {{
    position: fixed;
    left: 50%;
    transform: translateX(-50%);
    bottom: 70px;
    background: #222;
    color: #fff;
    padding: 8px 12px;
    border-radius: 999px;
    display: none;
    align-items: center;
    gap: 8px;
    box-shadow: 0 0 10px #000;
    z-index: 998;
    font-size: 13px;
}}
#ofertaEnviar {{
    background:#25D366;
    border:none;
    border-radius:999px;
    padding:5px 10px;
    font-weight:bold;
    cursor:pointer;
}}
#ofertaEnviar:disabled {{
    background:#555;
    cursor:default;
}}

/* OPTIMIZACIÓN PARA CELULARES */
@media (max-width: 600px) {{
    header {{ padding: 15px; }}
    .title {{ font-size: 22px; }}
    #searchInput, #categoryFilter {{ width: 95%; margin: 5px auto; }}
    .games-grid {{ gap: 14px; }}
    .game-card {{ width: 160px; }}
    .btn-uno, .btn-dos {{ font-size: 12px; padding:6px; }}
}}
</style>
</head>

<body>

<header>
    <div class="title">Almacén Copihue – Juegos PS2</div>
    <input type="text" id="searchInput" placeholder="Buscar juego...">
    <select id="categoryFilter">
        <option value="">Todas las Categorías</option>
"""

# CATEGORÍAS
for cat in sorted(df["Categoria"].unique()):
    html += f'<option value="{cat}">{cat}</option>\n'

html += "</select></header>\n<div class='games-grid' id='gamesGrid'>\n"


# -----------------------------
#  TARJETAS DE JUEGOS
# -----------------------------

for _, row in df.iterrows():
    nombre = str(row["Nombre"])
    categoria = str(row["Categoria"])
    normal = str(row["Precio_Normal"])
    oferta = str(row["Precio_Oferta"])
    disponible = str(row["Disponible"]).strip().lower()

    alias_base = str(row["Alias"]).lower()
    alias_extra = generar_alias_extra(nombre)

    data_name = f"{nombre.lower()} {alias_base} {alias_extra}"

    img = nombre.lower().replace(" ", "_") + ".jpg"
    if not os.path.exists(os.path.join(CARPETA_IMAGENES, img)):
        img = "sin_imagen.jpg"

    # Mensaje para 1 x normal
    mensaje_1x = f"Hola! Me interesa el juego {nombre} por ${normal}."
    mensaje_1x = mensaje_1x.replace(" ", "%20")

    # NO DISPONIBLE
    if disponible == "no":
        html += f"""
        <div class="game-card no-disponible"
             data-name="{data_name}"
             data-category="{categoria}">
             
            <img src="{CARPETA_IMAGENES}{img}" class="game-cover">
            <div class="game-info">
                <div class="game-title">{nombre}</div>
                <div class="game-category">{categoria}</div>
                <div class="no-disponible-text">NO DISPONIBLE</div>
            </div>
        </div>
        """
        continue

    # DISPONIBLE
    html += f"""
    <div class="game-card"
         data-name="{data_name}"
         data-category="{categoria}">
         
        <img src="{CARPETA_IMAGENES}{img}" class="game-cover">
        <div class="game-info">
            <div class="game-title">{nombre}</div>
            <div class="game-category">{categoria}</div>
            <div class="price-line">Precio: ${normal}</div>
            <div class="price-oferta">Oferta: {oferta}</div>

            <div class="buttons-row">
                <a class="btn-uno" href="https://wa.me/{WA_NUM}?text={mensaje_1x}" target="_blank">
                    1 x ${normal}
                </a>
                <button class="btn-dos btn-2x" data-game="{nombre}">
                    2 x $10000
                </button>
            </div>
        </div>
    </div>
    """

# Barra oferta y botón volver arriba
html += f"""
</div>

<div id="ofertaBar">
    <span id="ofertaTexto">Oferta 2 x $10000 — 0 juegos seleccionados</span>
    <button id="ofertaEnviar" disabled>Enviar por WhatsApp</button>
</div>

<button id="btnTop">↑</button>

<script>
document.addEventListener('DOMContentLoaded', () => {{
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const cards = document.querySelectorAll('.game-card');
    const btnTop = document.getElementById("btnTop");

    const ofertaBar = document.getElementById("ofertaBar");
    const ofertaTexto = document.getElementById("ofertaTexto");
    const ofertaEnviar = document.getElementById("ofertaEnviar");
    const botones2x = document.querySelectorAll(".btn-2x");
    const WHATSAPP_NUM = "{WA_NUM}";

    let seleccionados = [];

    function normalizar(txt) {{
        return txt.toLowerCase()
                  .normalize("NFD")
                  .replace(/\\u0300-\\u036f/g, "");
    }}

    function actualizarFiltro() {{
        const text = searchInput.value.trim().toLowerCase()
                       .normalize("NFD")
                       .replace(/\\u0300-\\u036f/g, "");
        const words = text.split(/\\s+/);
        const cat = categoryFilter.value;

        cards.forEach(card => {{
            const nombre = card.getAttribute('data-name')
                               .toLowerCase()
                               .normalize("NFD")
                               .replace(/\\u0300-\\u036f/g, "");
            const categoria = card.getAttribute('data-category');

            const coincideBusq = words.every(w => !w || nombre.includes(w));
            const coincideCat  = !cat || categoria === cat;

            card.style.display = (coincideBusq && coincideCat) ? "block" : "none";
        }});
    }}

    searchInput.addEventListener('input', actualizarFiltro);
    categoryFilter.addEventListener('change', actualizarFiltro);

    // BOTÓN VOLVER ARRIBA
    window.addEventListener("scroll", () => {{
        if (window.scrollY > 300) btnTop.style.display = "block";
        else btnTop.style.display = "none";
    }});

    btnTop.addEventListener("click", () => {{
        window.scrollTo({{ top: 0, behavior: "smooth" }});
    }});

    // LÓGICA OFERTA 2 x 10000
    function actualizarOfertaBar() {{
        if (seleccionados.length === 0) {{
            ofertaBar.style.display = "none";
        }} else {{
            ofertaBar.style.display = "flex";
            ofertaTexto.textContent = "Oferta 2 x $10000 — " + seleccionados.length + " juego(s) seleccionado(s)";
        }}
        ofertaEnviar.disabled = (seleccionados.length !== 2);
    }}

    botones2x.forEach(btn => {{
        btn.addEventListener("click", () => {{
            const nombreJuego = btn.getAttribute("data-game");
            const idx = seleccionados.indexOf(nombreJuego);

            if (idx === -1) {{
                if (seleccionados.length >= 2) {{
                    alert("Ya seleccionaste 2 juegos para la oferta 2 x $10000. Quita uno antes de elegir otro.");
                    return;
                }}
                seleccionados.push(nombreJuego);
                btn.classList.add("selected");
            }} else {{
                seleccionados.splice(idx, 1);
                btn.classList.remove("selected");
            }}

            actualizarOfertaBar();
        }});
    }});

    ofertaEnviar.addEventListener("click", () => {{
        if (seleccionados.length !== 2) return;

        const msg = 
            "Hola! Quiero aprovechar la oferta 2 x $10000.\\n" +
            "Juego 1: " + seleccionados[0] + "\\n" +
            "Juego 2: " + seleccionados[1];

        const url = "https://wa.me/" + WHATSAPP_NUM + "?text=" + encodeURIComponent(msg);
        window.open(url, "_blank");
    }});
}});
</script>

</body>
</html>
"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print("Catálogo generado correctamente:", OUTPUT_HTML)
