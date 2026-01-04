import json
import os


class Dipendente:
    def __init__(self, matricola, stipendio, straordinario):
        self.matricola = matricola
        self.stipendio = stipendio
        self.straordinario = straordinario

    def get_stipendio(self):
        return self.stipendio

    def paga(self, ore_straordinario):
        return self.stipendio + (ore_straordinario * self.straordinario)

    def stampa(self):
        print(f"👤 Matricola: {self.matricola}")
        print(f"💰 Stipendio base: {self.stipendio:.2f} €")
        print(f"⏱️ Straordinario: {self.straordinario:.2f} €/ora")

    def to_dict(self):
        return {
            'type': 'Dipendente',
            'matricola': self.matricola,
            'stipendio': self.stipendio,
            'straordinario': self.straordinario
        }


class DipendenteA(Dipendente):
    DETRAZIONE_GIORNO = 15.0

    def __init__(self, matricola, stipendio, straordinario):
        super().__init__(matricola, stipendio, straordinario)
        self.malattia = 0

    def prendi_malattia(self, giorni):
        if giorni < 0:
            print("❌ Errore: i giorni di malattia non possono essere negativi.")
            return
        self.malattia += giorni

    def paga(self, ore_straordinario):
        paga_totale = super().paga(ore_straordinario)
        if self.malattia > 0:
            detrazione = self.malattia * self.DETRAZIONE_GIORNO
            paga_totale = max(0, paga_totale - detrazione)
        return paga_totale

    def stampa(self):
        super().stampa()
        print(f"🤒 Giorni di malattia: {self.malattia}")

    def to_dict(self):
        data = super().to_dict()
        data['type'] = 'DipendenteA'
        data['malattia'] = self.malattia
        return data


def from_dict(data):
    tipo = data['type']
    if tipo == 'DipendenteA':
        d = DipendenteA(data['matricola'], data['stipendio'], data['straordinario'])
        d.malattia = data['malattia']
        return d
    else:
        return Dipendente(data['matricola'], data['stipendio'], data['straordinario'])


def salva_dipendenti(dipendenti, filename='dipendenti.json'):
    data = [d.to_dict() for d in dipendenti]
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"💾 Dipendenti salvati in {filename}")


def carica_dipendenti(filename='dipendenti.json'):
    if not os.path.exists(filename):
        print(f"📭 File {filename} non trovato.")
        return []
    with open(filename, 'r') as f:
        data = json.load(f)
    dipendenti = [from_dict(d) for d in data]
    print(f"📂 Caricati {len(dipendenti)} dipendenti da {filename}")
    return dipendenti


def input_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("❌ Inserisci un numero valido.")


def input_int(prompt):
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("❌ Inserisci un numero intero valido.")


def crea_dipendente():
    print("\n--- 👔 Creazione nuovo dipendente ---")
    matricola = input("Matricola: ").strip()
    stipendio = input_float("Stipendio base (€): ")
    straordinario = input_float("Compenso orario straordinario (€/h): ")

    tipo = input("Ha gestione malattia? (s/n): ").strip().lower()
    return DipendenteA(matricola, stipendio, straordinario) if tipo == 's' else Dipendente(matricola, stipendio, straordinario)


def main():
    print("💼 Sistema di calcolo stipendi")
    dipendenti = carica_dipendenti()  # Carica all'avvio

    while True:
        print("\n📋 Menu principale:")
        print("1️⃣  Aggiungi nuovo dipendente")
        print("2️⃣  Visualizza tutti i dipendenti")
        print("3️⃣  Calcola stipendio")
        print("4️⃣  Aggiungi giorni di malattia")
        print("5️⃣  Salva dipendenti")
        print("6️⃣  Carica dipendenti")
        print("7️⃣  Esci")

        scelta = input("\n👉 Scelta (1-7): ").strip()

        if scelta == '1':
            dipendenti.append(crea_dipendente())
            print("✅ Dipendente aggiunto con successo!")

        elif scelta == '2':
            if not dipendenti:
                print("📭 Nessun dipendente registrato.")
            else:
                for i, d in enumerate(dipendenti, 1):
                    print(f"\n👷 Dipendente #{i}:")
                    d.stampa()

        elif scelta == '3':
            if not dipendenti:
                print("📭 Nessun dipendente registrato.")
                continue

            print("\n👥 Seleziona dipendente:")
            for i, d in enumerate(dipendenti, 1):
                print(f"{i}. {d.matricola}")

            idx = input_int("Numero dipendente: ") - 1
            if 0 <= idx < len(dipendenti):
                ore = input_float("Ore di straordinario: ")
                if ore < 0:
                    print("❌ Ore negative non valide.")
                    continue
                totale = dipendenti[idx].paga(ore)
                print(f"💶 Stipendio totale: {totale:.2f} €")
            else:
                print("❌ Scelta non valida.")

        elif scelta == '4':
            dip_a = [d for d in dipendenti if isinstance(d, DipendenteA)]
            if not dip_a:
                print("📭 Nessun dipendente con gestione malattia.")
                continue

            print("\n🤒 Dipendenti con gestione malattia:")
            for i, d in enumerate(dip_a, 1):
                print(f"{i}. {d.matricola}")

            idx = input_int("Numero dipendente: ") - 1
            if 0 <= idx < len(dip_a):
                giorni = input_int("Giorni di malattia da aggiungere: ")
                dip_a[idx].prendi_malattia(giorni)
                print("✅ Giorni aggiunti correttamente!")
            else:
                print("❌ Scelta non valida.")

        elif scelta == '5':
            salva_dipendenti(dipendenti)
            print("✅ Salvataggio completato!")

        elif scelta == '6':
            dipendenti = carica_dipendenti()
            print("✅ Caricamento completato!")

        elif scelta == '7':
            salva_dipendenti(dipendenti)  # Salva automaticamente all'uscita
            print("👋 Uscita dal programma. Arrivederci!")
            break

        else:
            print("❌ Opzione non valida. Riprova.")


if __name__ == "__main__":
    main()
