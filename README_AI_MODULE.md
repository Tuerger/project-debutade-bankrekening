# Tag Recommender AI Module

## Overzicht

Dit project bevat nu een AI-module die automatisch tag-suggesties kan doen voor transacties op basis van een trainingsset. De module gebruikt een eenvoudige maar effectieve bag-of-words benadering met TF-IDF weging.

## Bestanden

### tag_recommender.py
De kern van het AI-systeem. Bevat de `TagRecommender` klasse die:
- Trainingsdata inleest uit een Excel bestand
- Een vocabulaire opbouwt per tag
- Suggesties genereert op basis van tekstuele gelijkenissen

### static/category_test_set.xlsx
**BELANGRIJK**: Dit bestand bevat persoonlijke trainingsdata en mag **NOOIT** naar GitHub worden gepusht.

Het bestand wordt beschermd door `.gitignore` en bevat historische transacties met hun tags die gebruikt worden om het AI-model te trainen.

#### Verwachte structuur:
Het Excel bestand moet een header-rij bevatten met tenminste:
- Een kolom genaamd "Tag" (of "tags", "categorie", "category")
- Een of meer tekstkolommen zoals:
  - "Naam / Omschrijving"
  - "Mededelingen"
  - "Rekening"
  - "Tegenrekening"
  - "Code"
  - etc.

Voorbeeld:
```
Datum | Naam / Omschrijving | Rekening | ... | Tag
------|---------------------|----------|-----|----
2025-01-01 | ING rent payment | NL01 | ... | 4500;Huur gebouw
2025-01-02 | Coffee supplies | NL02 | ... | 8700;Koffie
```

## Hoe werkt het?

### 1. Training
- Bij het starten laadt `tag_recommender` het trainingsbestand
- Het tokenizeert alle tekstvelden (splits op woorden/cijfers)
- Voor elke tag bouwt het een woordfrequentie-profiel op
- IDF (Inverse Document Frequency) wordt berekend om veelvoorkomende woorden te devalueren

### 2. Suggestie genereren
Wanneer een gebruiker op "AI suggestie" klikt:
1. De transactie-gegevens worden naar `/recommend_tag` gestuurd
2. De server haalt de volledige rij op uit het Excel bestand
3. `TagRecommender.recommend()` berekent een score voor elke mogelijke tag:
   - Score = Σ (TF in tag) × (TF in transactie) × IDF
   - TF = Term Frequency (hoe vaak komt een woord voor)
   - IDF = log(1 + totaal_documenten / (1 + documenten_met_woord))
4. De top 3 tags met hoogste scores worden teruggegeven

### 3. Gebruikersinterface
- In de "Transacties zonder Tag" tabel verschijnt een "AI suggestie" knop
- Klik op de knop om suggesties op te halen
- De top suggestie wordt automatisch in het invoerveld geplaatst
- Alle 3 de suggesties worden getoond als klikbare chips met hun scores
- Klik op een chip om een andere suggestie te kiezen
- Klik "Opslaan" om de gekozen tag op te slaan

## Configuratie

### In webapp.py
```python
TRAINING_FILE_PATH = os.path.join(SCRIPT_DIR, "static", "category_test_set.xlsx")
tag_recommender = TagRecommender(TRAINING_FILE_PATH, allowed_tags=TAGS)
```

De `allowed_tags` parameter zorgt ervoor dat alleen tags uit de configuratie worden voorgesteld.

### Trainingsdata updaten
- Voeg nieuwe transacties met correcte tags toe aan `category_test_set.xlsx`
- Bij de volgende server start worden deze automatisch ingelezen
- De module detecteert automatisch wijzigingen in het bestand (via mtime check)

## Beveiliging

### .gitignore
Het bestand `.gitignore` is bijgewerkt om te voorkomen dat persoonlijke data wordt gecommit:
```
# Persoonlijke trainingsdata - NIET committen
static/category_test_set.xlsx
static/~$category_test_set.xlsx
```

**WAARSCHUWING**: Controleer altijd met `git status` dat deze bestanden niet worden toegevoegd voordat je commit.

## API Endpoints

### POST /recommend_tag
Vraag tag-suggesties op voor een specifieke transactie.

**Request body:**
```json
{
  "sheet_name": "Bankrekening",
  "row_index": 2
}
```

**Response (success):**
```json
{
  "success": true,
  "top_tag": "8700;Koffie",
  "suggestions": [
    {"tag": "8700;Koffie", "score": 2.4567},
    {"tag": "4590;Overige Huisvestingskosten", "score": 1.2345},
    {"tag": "4930;Kantoorartikelen", "score": 0.8901}
  ]
}
```

**Response (geen suggesties):**
```json
{
  "success": false,
  "message": "Geen suggesties beschikbaar op basis van trainingsset."
}
```

## Prestaties

- **Snelheid**: Suggesties worden in < 100ms gegenereerd voor typische datasets
- **Geheugen**: Minimaal (vocabulaire wordt in-memory gehouden)
- **Schaalbaarheid**: Geschikt voor duizenden trainingsvoorbeelden

## Beperkingen

1. **Alleen tekstuele kenmerken**: Bedragen, datums, en rekening-types worden niet gewogen
2. **Geen context**: Eerdere transacties worden niet meegenomen
3. **Simpel model**: Geen deep learning, alleen statistiek
4. **Nederlandse taal**: Tokenization is geoptimaliseerd voor Latijnse karakters

## Toekomstige verbeteringen

Mogelijke uitbreidingen:
- [ ] Leer van feedback (welke suggesties worden geaccepteerd?)
- [ ] Gebruik numerieke features (bedrag, datum, rekening-patroon)
- [ ] N-gram ondersteuning (woordcombinaties)
- [ ] Fuzzy matching voor typfouten
- [ ] Export van model-statistieken voor analyse

## Troubleshooting

### "Geen suggesties beschikbaar"
- Controleer of `category_test_set.xlsx` bestaat in de `static` folder
- Controleer of het bestand een "Tag" kolom bevat
- Controleer of er voldoende trainingsdata is (minimaal 10-20 voorbeelden per tag aanbevolen)

### Slechte suggesties
- Voeg meer trainingsvoorbeelden toe voor die specifieke tags
- Controleer of de tags in de trainingsset exact overeenkomen met de tags in config.json
- Verwijder ambigue of foutieve voorbeelden uit de trainingsset

### Import errors
- Zorg dat alle dependencies geïnstalleerd zijn: `pip install -r requirements.txt`
- Controleer of `tag_recommender.py` in de root directory staat

## Logging

Het systeem logt belangrijke events naar het logbestand:
```
2026-01-07 10:30:00 - WARNING - Trainingsbestand niet gevonden: static/category_test_set.xlsx
2026-01-07 10:35:00 - INFO - Trainingsdata geladen: 150 documenten
2026-01-07 10:36:00 - ERROR - Fout bij genereren tag-suggestie: ...
```

Check `log_directory` voor details bij problemen.
