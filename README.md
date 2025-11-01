# Automated Analysis

Tämä projekti tuottaa PDF-muotoisen tilastoraportin JSON-datasta. Raportti sisältää yleisiä kaavioita, kuten histogrammeja, laatikkokaavioita, kategorioiden top-listauksia sekä korrelaatiomatriisin. Raportit versioidaan automaattisesti aikaleiman perusteella ja tallennetaan `Reports`-kansioon.

## Ympäristön valmistelu

Suosittelemme Python 3.10+ ympäristöä. Voit luoda ja alustaa virtuaaliympäristön ajamalla repositorion juuresta:

```bash
./scripts/setup_env.sh
```

Scripti luo `.venv`-kansion, aktivoi sen sekä asentaa projektin riippuvuudet. Vaihtoehtoisesti voit luoda ympäristön käsin:

```bash
python -m venv .venv
source .venv/bin/activate  # Windowsissa: .venv\Scripts\activate
pip install -r requirements.txt
```

## Raportin generointi komentoriviltä

```bash
python -m automation path/to/dataset.json --title "Oma raportin otsikko"
```

Raportti tallentuu oletuksena `Reports`-kansioon muodossa `report_YYYYMMDD_HHMMSS.pdf`. Voit ohjata raportin toiseen hakemistoon `--report-dir` -lipulla.

## Graafinen käyttöliittymä

Voit tutkia dataa ja generoida raportin PandasGUI-pohjaisen käyttöliittymän kautta:

```bash
python -m automation.gui_app path/to/dataset.json
```

`path/to/dataset.json` on vapaaehtoinen; jos polkua ei anneta, voit valita JSON-tiedoston käyttöliittymästä. Kun data on avattu, se aukeaa PandasGUI-ikkunaan, ja "Generate PDF report" -painike luo raportin `Reports`-kansioon.

## Testit

```bash
pytest
```
