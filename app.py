import streamlit as st
import json
import os

# Dateipfade
ZUTATEN_FILE = "zutaten.json"
GERICHTE_FILE = "gerichte.json"
WOCHENPLAN_FILE = "wochenplan.json"

# Hilfsfunktionen für JSON lesen/schreiben
def load_json(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {}

def save_json(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

# Zutatenverwaltung
def zutatenverwaltung():
    st.header("Zutatenverwaltung")
    zutaten = load_json(ZUTATEN_FILE)

    # Neuzutat hinzufügen
    with st.form("neue_zutat"):
        st.subheader("Neue Zutat hinzufügen")
        name = st.text_input("Name")
        kalorien = st.number_input("Kalorien (pro 100g)", min_value=0.0, format="%.2f")
        protein = st.number_input("Protein (g pro 100g)", min_value=0.0, format="%.2f")
        fett = st.number_input("Fett (g pro 100g)", min_value=0.0, format="%.2f")
        kohlenhydrate = st.number_input("Kohlenhydrate (g pro 100g)", min_value=0.0, format="%.2f")
        hinweise = st.text_input("Hinweise (z.B. Kaufort)")

        submitted = st.form_submit_button("Zutat speichern")
        if submitted:
            if name.strip() == "":
                st.error("Name darf nicht leer sein.")
            elif name in zutaten:
                st.error("Zutat existiert bereits.")
            else:
                zutaten[name] = {
                    "kalorien": kalorien,
                    "protein": protein,
                    "fett": fett,
                    "kohlenhydrate": kohlenhydrate,
                    "hinweise": hinweise
                }
                save_json(ZUTATEN_FILE, zutaten)
                st.success(f"Zutat '{name}' gespeichert.")

    # Zutatenliste anzeigen
    if zutaten:
        st.subheader("Vorhandene Zutaten")
        for name, info in zutaten.items():
            st.write(f"**{name}** — Kal: {info['kalorien']}, Prot: {info['protein']}g, Fett: {info['fett']}g, KH: {info['kohlenhydrate']}g, Hinweise: {info['hinweise']}")
    else:
        st.info("Keine Zutaten vorhanden.")

# Gerichtserstellung
def gerichtserstellung():
    st.header("Gerichtserstellung")
    zutaten = load_json(ZUTATEN_FILE)
    gerichte = load_json(GERICHTE_FILE)

    # Neues Gericht erstellen
    with st.form("neues_gericht"):
        st.subheader("Neues Gericht erstellen")
        gericht_name = st.text_input("Name des Gerichts")

        selected_zutaten = []
        mengen = []

        if zutaten:
            st.write("Zutaten auswählen und Mengen in Gramm eingeben:")
            for zutat in zutaten:
                menge = st.number_input(f"{zutat} (g)", min_value=0, step=10, key=f"menge_{zutat}")
                if menge > 0:
                    selected_zutaten.append(zutat)
                    mengen.append(menge)
        else:
            st.info("Bitte zuerst Zutaten hinzufügen.")

        submitted = st.form_submit_button("Gericht speichern")
        if submitted:
            if gericht_name.strip() == "":
                st.error("Gerichtsname darf nicht leer sein.")
            elif gericht_name in gerichte:
                st.error("Gericht existiert bereits.")
            elif not selected_zutaten:
                st.error("Bitte mindestens eine Zutat mit Menge angeben.")
            else:
                # Nährwerte berechnen
                kalorien = 0
                protein = 0
                fett = 0
                kohlenhydrate = 0
                for z, m in zip(selected_zutaten, mengen):
                    z_info = zutaten[z]
                    factor = m / 100
                    kalorien += z_info["kalorien"] * factor
                    protein += z_info["protein"] * factor
                    fett += z_info["fett"] * factor
                    kohlenhydrate += z_info["kohlenhydrate"] * factor

                gerichte[gericht_name] = {
                    "zutaten": [{"name": z, "menge": m} for z, m in zip(selected_zutaten, mengen)],
                    "kalorien": round(kalorien,2),
                    "protein": round(protein,2),
                    "fett": round(fett,2),
                    "kohlenhydrate": round(kohlenhydrate,2)
                }
                save_json(GERICHTE_FILE, gerichte)
                st.success(f"Gericht '{gericht_name}' gespeichert.")

    # Bestehende Gerichte anzeigen
    if gerichte:
        st.subheader("Vorhandene Gerichte")
        for name, info in gerichte.items():
            st.write(f"**{name}** — Kal: {info['kalorien']}, Prot: {info['protein']}g, Fett: {info['fett']}g, KH: {info['kohlenhydrate']}g")
            st.write("Zutaten:")
            for z in info["zutaten"]:
                st.write(f"- {z['name']}: {z['menge']}g")
    else:
        st.info("Keine Gerichte vorhanden.")

# Wochenplan
def wochenplan():
    st.header("Wochenplan (Mo–Do)")
    gerichte = load_json(GERICHTE_FILE)

    tage = ["Montag", "Dienstag", "Mittwoch", "Donnerstag"]
    mahlzeiten = ["Frühstück", "Mittagessen", "Abendessen"]

    # Wochenplan laden oder neu initialisieren
    wochenplan = load_json(WOCHENPLAN_FILE)
    if not wochenplan:
        wochenplan = {tag: {m: "" for m in mahlzeiten} for tag in tage}

    for tag in tage:
        st.subheader(tag)
        for mahlzeit in mahlzeiten:
            # Suchfeld
            suchtext = st.text_input(f"{tag} - {mahlzeit} suchen", key=f"{tag}_{mahlzeit}_search")
            gefilterte_gerichte = [g for g in gerichte.keys() if suchtext.lower() in g.lower()] if suchtext else list(gerichte.keys())
            ausgewählt = st.selectbox(f"{tag} - {mahlzeit}", options=[""] + gefilterte_gerichte, index=0, key=f"{tag}_{mahlzeit}_select")
            wochenplan[tag][mahlzeit] = ausgewählt

    # Speichern-Button
    if st.button("Wochenplan speichern"):
        save_json(WOCHENPLAN_FILE, wochenplan)
        st.success("Wochenplan gespeichert.")

    # Nährwerte pro Tag berechnen & anzeigen
    for tag in tage:
        kalorien = 0
        protein = 0
        fett = 0
        kohlenhydrate = 0
        for mahlzeit in mahlzeiten:
            gericht_name = wochenplan[tag].get(mahlzeit)
            if gericht_name and gericht_name in gerichte:
                info = gerichte[gericht_name]
                kalorien += info["kalorien"]
                protein += info["protein"]
                fett += info["fett"]
                kohlenhydrate += info["kohlenhydrate"]
        st.write(f"**Nährwerte {tag}:** Kalorien: {kalorien:.1f} kcal, Protein: {protein:.1f} g, Fett: {fett:.1f} g, Kohlenhydrate: {kohlenhydrate:.1f} g")

# Einkaufsliste erstellen
def einkaufsliste():
    st.header("Einkaufsliste")
    wochenplan = load_json(WOCHENPLAN_FILE)
    gerichte = load_json(GERICHTE_FILE)
    zutaten = load_json(ZUTATEN_FILE)

    if not wochenplan or not gerichte or not zutaten:
        st.info("Bitte erst Zutaten, Gerichte und Wochenplan anlegen.")
        return

    einkauf = {}

    for tag_data in wochenplan.values():
        for gericht_name in tag_data.values():
            if gericht_name in gerichte:
                for z in gerichte[gericht_name]["zutaten"]:
                    name = z["name"]
                    menge = z["menge"]
                    if name in einkauf:
                        einkauf[name] += menge
                    else:
                        einkauf[name] = menge

    st.subheader("Benötigte Zutaten für die Woche")
    for name, menge in einkauf.items():
        hinweise = zutaten.get(name, {}).get("hinweise", "")
        st.write(f"- {name}: {menge} g | Hinweise: {hinweise}")

    # Export als Textdatei
    if st.button("Einkaufsliste als Text speichern"):
        lines = [f"{name}: {menge} g | Hinweise: {zutaten.get(name, {}).get('hinweise', '')}" for name, menge in einkauf.items()]
        text = "\n".join(lines)
        st.download_button("Download Einkaufsliste", text, file_name="einkaufsliste.txt")

# Haupt-App
def main():
    st.title("Maschinenbautechniker Ernährungsplaner")
    menu = ["Zutatenverwaltung", "Gerichtserstellung", "Wochenplan", "Einkaufsliste"]
    choice = st.sidebar.selectbox("Men