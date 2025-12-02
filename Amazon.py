import streamlit as st
import pandas as pd
import io

st.title("Generatore File Amazon - Olio Motore")

uploaded = st.file_uploader("Carica il file input", type=["xlsx", "csv"])

def first_non_empty(row, columns):
    for c in columns:
        if pd.notna(row[c]) and str(row[c]).strip() != "":
            return str(row[c]).strip()
    return ""

if uploaded:
    if uploaded.name.endswith(".csv"):
        df = pd.read_csv(uploaded)
    else:
        df = pd.read_excel(uploaded)

    # Normalizzo i nomi colonne eliminando spazi extra
    df.columns = df.columns.str.strip()

    output = pd.DataFrame()

    # --- POPOLAZIONE COLONNE BASE ---
    output["SKU"] = df["Sku"]
    output["Tipo di prodotto"] = "AUTO_OIL"

    # -------------------------------
    # FUNZIONE TITOLO AMAZON
    # -------------------------------
    def build_nome_articolo(row):
        marca = str(row["Marca"]).strip()
        viscosity = str(row["Viscosità"]).strip()
        acea = str(row["ACEA"]).strip()
        formato = str(row["Formato (L)"]).strip()
        tipologia = str(row["Tipologia"]).strip()
        utilizzo = str(row["Utilizzo"]).strip()

        return (
            f"Lubrificanti {marca} SAE {viscosity} {acea} "
            f"{formato}x1L - Olio motore {tipologia} per {utilizzo}"
        )

    output["Nome dell’articolo"] = df.apply(build_nome_articolo, axis=1)
    output["Nome del marchio"] = df["Marca"]
    output["Tipo ID di prodotto"] = "Esenzione GTIN"
    output["ID prodotto"] = ""
    output["Nome del modello"] = df["Nome olio"]
    output["Produttore"] = df["Marca"]
    output["Condizione dell’articolo"] = "Nuovo"
    output["Prezzo al pubblico consigliato (IVA inclusa)"] = df["Prezzo Marketplace"]
    output["Codice canale di gestione (IT)"] = "DEFAULT"
    output["Quantità (IT)"] = 20
    output["Prezzo EUR (Vendita su Amazon, IT)"] = df["Prezzo Marketplace"]

    def shipping_group(row):
        return "" if float(row["Formato (L)"]) == 205 else "Modello Amazon predefinito"

    output["Gruppo spedizione venditore (IT)"] = df.apply(shipping_group, axis=1)
    output["Descrizione del prodotto"] = df["Descrizione"]

    # --- PUNTI ELENCO STANDARDIZZATI ---
    def punto1(row):
        return "LONG LIFE CONSULTING: azienda italiana specializzata nel settore dei lubrificanti per autovetture, motocicli, industriali, agricoli e nautici."

    def punto2(row):
        return "PRODOTTO: i prodotti offerti dalla LONG LIFE CONSULTING sono 100% made in Italy, studiati per fornire massime prestazioni, formulati con oli e additivi selezionati."

    def punto3(row):
        return "SPEDIZIONE: il prodotto è altamente controllato, riscontrato e sigillato prima di effettuare il ritiro per la spedizione."

    def punto4(row):
        return "ASSISTENZA: Gli uffici di LONG LIFE CONSULTING sono disponibili per qualsiasi tipo di chiarimento per fornire una massima esperienza di acquisto."

    def punto5(row):
        return "SPECIFICHE TECNICHE: trovi le specifiche tecniche ben visibili sulle foto mostrate in inserzione."

    output["Punto elenco 1"] = df.apply(punto1, axis=1)
    output["Punto elenco 2"] = df.apply(punto2, axis=1)
    output["Punto elenco 3"] = df.apply(punto3, axis=1)
    output["Punto elenco 4"] = df.apply(punto4, axis=1)
    output["Punto elenco 5"] = df.apply(punto5, axis=1)

    # Colonne aggiuntive
    output["Materiale"] = "Lubrificanti Motore"

    def qty_logic(row):
        f = float(row["Formato (L)"])
        return int(f) if f <= 6 else 1

    output["Numero di articoli"] = df.apply(qty_logic, axis=1)
    output["Quantità per pacco dell’articolo"] = output["Numero di articoli"]

    # Vari
    output["Numero Di Parte"] = df["Viscosità"]
    output["Grado del Prodotto"] = "Ricambio"
    output["Compatibile con tipo di veicolo"] = "Automobile"
    output["Conteggio di unità"] = 1
    output["Tipo di conteggio unità"] = "Unità"
    output["Componenti inclusi"] = "Olio motore"
    output["È fragile?"] = "Si"
    output["Tipo di installazione automobilistica"] = "Universale"
    output["Grado di viscosità SAE J300"] = df["Viscosità"]
    output["Paese di origine"] = "Italia"
    output["Garanzia prodotto"] = "Non applicabile"
    output["Regolamentazioni di merci pericolose"] = "Non applicabile"
    output["Contiene sostanze liquide"] = "Si"
    output["Volume del liquido"] = df["Formato (L)"]
    output["Unità di volume del liquido"] = "Litri"

    # Search Terms ottimizzati
    def search_terms(row):
        return (
            f"{row['Viscosità']} {row['Nome olio']} {row['ACEA']} "
            f"{row['Tipologia']} {row['Utilizzo']} "
            f"{row['Formato (L)']}L "
            "olio motore olio auto lubrificante sintetico diesel benzina manutenzione"
        )

    output["Search Terms"] = df.apply(search_terms, axis=1)

    # Immagini: fino a 8 immagini
    img_cols = ["Img 1", "Img 2", "Img 3", "Img 4", "Img 5", "Img 6", "Img 7"]

    def get_images(row):
        images = []
        for col in img_cols:
            val = row[col]
            if pd.notna(val) and str(val).strip() != "":
                images.append(val)
        while len(images) < 8:
            images.append("")
        return images[:8]

    img_matrix = df.apply(get_images, axis=1, result_type="expand")
    img_matrix.columns = [
        "URL immagine principale",
        "URL altra immagine 1",
        "URL altra immagine 2",
        "URL altra immagine 3",
        "URL altra immagine 4",
        "URL altra immagine 5",
        "URL altra immagine 6",
        "URL altra immagine 7",
    ]

    output = pd.concat([output, img_matrix], axis=1)

    # --- DOWNLOAD ---
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        output.to_excel(writer, index=False, sheet_name="Amazon")

    st.success("File generato correttamente!")
    st.download_button(
        label="Scarica file Amazon",
        data=buffer.getvalue(),
        file_name="amazon_output.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
