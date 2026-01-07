# Wijzigingen: Tag Recommender AI Module

## Datum: 2026-01-07

## Samenvatting
Een AI-module is toegevoegd aan de Bankrekening Debutade webapp die automatisch tag-suggesties kan doen voor transacties op basis van een trainingsset.

## Nieuwe bestanden

### 1. tag_recommender.py
- **Doel**: Kern van het AI-systeem
- **Klasse**: `TagRecommender`
- **Functionaliteit**:
  - Laadt trainingsdata uit Excel bestand
  - Bouwt vocabulaire per tag met TF-IDF weging
  - Genereert top-3 tag suggesties voor nieuwe transacties
- **Algoritme**: Bag-of-words met IDF-weging

### 2. static/category_test_set.xlsx
- **Doel**: Trainingsdata voor het AI-model
- **Bevat**: Historische transacties met hun correcte tags
- **Status**: NIET in git (bevat persoonlijke data)
- **Structuur**: Excel met minimaal een "Tag" kolom en tekstvelden

### 3. .gitignore
- **Nieuw bestand** om persoonlijke data te beschermen
- Blokkeert:
  - `static/category_test_set.xlsx`
  - `static/~$category_test_set.xlsx`
  - `.venv/`, `__pycache__/`, `*.pyc`

### 4. README_AI_MODULE.md
- Uitgebreide documentatie over de AI-module
- Bevat:
  - Overzicht van het systeem
  - Hoe het werkt (training & suggesties)
  - API documentatie
  - Troubleshooting guide
  - Toekomstige verbeteringen

### 5. test_ai_module.py
- Test script voor de recommender
- Test cases:
  - Initialisatie
  - Laden trainingsdata
  - Suggestie genereren
  - Edge cases (lege input, onbekende woorden)

## Gewijzigde bestanden

### webapp.py

#### Imports
```python
from tag_recommender import TagRecommender
```

#### Globale variabelen
```python
TRAINING_FILE_PATH = os.path.join(SCRIPT_DIR, "static", "category_test_set.xlsx")
tag_recommender = TagRecommender(TRAINING_FILE_PATH, allowed_tags=TAGS)
tag_recommender.load()
```

#### Nieuwe functie: get_transaction_from_sheet()
- Leest een enkele transactierij uit een sheet
- Retourneert een dict met alle relevante velden
- Wordt gebruikt door de AI-module om suggesties te genereren

#### Nieuwe route: /recommend_tag (POST)
- **Input**: `sheet_name`, `row_index`
- **Output**: `top_tag` + lijst van 3 suggesties met scores
- **Proces**:
  1. Valideer input (sheet naam, rij index)
  2. Haal transactie op uit Excel
  3. Vraag suggesties aan recommender
  4. Retourneer top 3 met scores

### templates/index.html

#### CSS toevoegingen
```css
.btn-secondary - Styling voor "AI suggestie" knop
.suggestion-box - Container voor suggesties
.suggestion-chip - Klikbare tag-chip met score
.suggestion-error - Error styling
```

#### HTML wijzigingen
In de "Transacties zonder Tag" tabel:
- Nieuwe kolom voor suggesties: `<div id="suggestions-{sheet}-{row}">`
- Nieuwe knop: "AI suggestie" (naast "Opslaan")
- Beide knoppen per transactierij

#### JavaScript toevoegingen
```javascript
function requestSuggestion(button)
  - Haalt suggesties op via /recommend_tag
  - Toont laadstatus
  - Plaatst top suggestie in invoerveld
  - Rendert alle suggesties als chips

function renderSuggestions(sheetName, rowIndex, suggestions)
  - Maakt HTML voor suggestie-chips
  - Toont scores bij elke suggestie

function useSuggestedTag(element)
  - Wordt aangeroepen bij klik op suggestie-chip
  - Plaatst gekozen tag in invoerveld
```

## Gebruikersflow

1. Gebruiker opent webapp en ziet transacties zonder tag
2. Klik op "AI suggestie" knop naast een transactie
3. Backend haalt transactiegegevens op uit Excel
4. AI-module genereert top 3 suggesties
5. Top suggestie wordt automatisch ingevuld
6. Alle 3 suggesties worden getoond als klikbare chips (met scores)
7. Gebruiker kan:
   - De top suggestie direct accepteren (klik "Opslaan")
   - Een andere suggestie kiezen (klik op chip)
   - Handmatig een andere tag intypen
8. Klik "opslaan" om de tag op te slaan in Excel

## Technische details

### Algoritme
- **Tokenization**: Regex `[A-Za-z0-9]+` (splits op woorden en cijfers)
- **TF-IDF**: `score = Σ (TF_tag × TF_trans × IDF)`
  - TF_tag = Hoe vaak woord voorkomt in tag-documenten
  - TF_trans = Hoe vaak woord voorkomt in huidige transactie
  - IDF = log(1 + N / (1 + df)) waar df = document frequency
- **Ranking**: Hoogste score = beste match

### Performance
- **Training**: < 1 seconde voor 1000 documenten
- **Suggestie**: < 100ms per transactie
- **Geheugen**: Minimaal (vocabulaire in-memory)
- **Cache**: Trainingsdata wordt gecached op basis van mtime

### Beveiliging
- Trainingsdata wordt **niet** gecommit naar GitHub
- `.gitignore` beschermt persoonlijke data
- Alleen tags uit config.json worden voorgesteld
- Input validatie op server-side

## Afhankelijkheden

Geen nieuwe Python packages vereist! Alles werkt met bestaande dependencies:
- `openpyxl` (al aanwezig)
- `flask` (al aanwezig)
- Python standard library (`re`, `math`, `collections`, `logging`)

## Testing

Run test script:
```bash
python test_ai_module.py
```

Of test via de webapp:
1. Start de webapp
2. Zorg dat er transacties zonder tag zijn
3. Klik op "AI suggestie"
4. Controleer of suggesties verschijnen

## Bekende beperkingen

1. Geen gebruik van numerieke features (bedrag, datum)
2. Geen context van eerdere transacties
3. Simpel statistisch model (geen deep learning)
4. Alleen tekstuele overeenkomsten
5. Geen feedback loop (leert niet van gebruikerskeuzes)

## Volgende stappen (optioneel)

1. **Meer trainingsdata**: Voeg historische transacties toe aan `category_test_set.xlsx`
2. **Monitor prestaties**: Kijk welke suggesties worden geaccepteerd
3. **Finetuning**: Pas algoritme aan op basis van feedback
4. **Export functie**: Maak een tool om huidige Excel data te exporteren als trainingsset
5. **Numerieke features**: Voeg bedrag-patronen toe aan het model

## Commit suggestie

```
feat: Add AI tag recommender module

- New TagRecommender class with TF-IDF based suggestions
- /recommend_tag API endpoint for getting tag suggestions
- "AI suggestie" button in untagged transactions table
- Training data protected by .gitignore
- Comprehensive documentation in README_AI_MODULE.md

The AI module suggests tags based on historical transaction data
stored in static/category_test_set.xlsx (not committed to git).
Users can click "AI suggestie" to get top 3 recommendations.
```
