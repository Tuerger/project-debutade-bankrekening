"""
Eenvoudige tag-recommender op basis van een trainingsset in Excel.
Gebruikt een bag-of-words benadering met IDF-weging om per tag een score te berekenen.
"""
import logging
import math
import os
import re
from collections import Counter, defaultdict
from typing import Dict, List, Tuple

from openpyxl import load_workbook

TOKEN_RE = re.compile(r"[A-Za-z0-9]+")


class TagRecommender:
    """Houdt een lichtgewicht vocabulaire per tag bij en kan suggesties genereren."""

    def __init__(self, training_path: str, allowed_tags: List[str] | None = None):
        self.training_path = training_path
        self.allowed_tags = set(allowed_tags or [])
        self.tag_token_freq: defaultdict[str, Counter[str]] = defaultdict(Counter)
        self.token_doc_freq: Counter[str] = Counter()
        self.tag_totals: Counter[str] = Counter()
        self.total_docs = 0
        self.last_loaded_mtime: float | None = None

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        return [match.group(0).lower() for match in TOKEN_RE.finditer(text or "")]

    def _reset(self) -> None:
        self.tag_token_freq.clear()
        self.token_doc_freq.clear()
        self.tag_totals.clear()
        self.total_docs = 0

    def _find_columns(self, header: List[str]) -> Tuple[int | None, List[int]]:
        """Zoek de kolommen voor tag en tekstvelden."""
        normalized = [str(col).strip().lower() for col in header]
        lookup = {name: idx for idx, name in enumerate(normalized)}

        tag_col = None
        for candidate in ("tag", "tags", "categorie", "category"):
            if candidate in lookup:
                tag_col = lookup[candidate]
                break

        text_cols = []
        for candidate in (
            "naam / omschrijving",
            "naam/omschrijving",
            "mededeling",
            "mededelingen",
            "omschrijving",
            "rekening",
            "tegenrekening",
            "mutatiesoort",
            "memo",
            "code",
            "description",
        ):
            if candidate in lookup:
                text_cols.append(lookup[candidate])

        if not text_cols:
            # Geen duidelijke tekstkolommen gevonden: gebruik alle kolommen behalve de tagkolom
            text_cols = [idx for idx in range(len(header)) if idx != tag_col]

        return tag_col, text_cols

    def load(self) -> bool:
        """Laad of herlaad het trainingsbestand als het aanwezig is."""
        if not self.training_path or not os.path.exists(self.training_path):
            logging.warning("Trainingsbestand niet gevonden: %s", self.training_path)
            return False

        mtime = os.path.getmtime(self.training_path)
        if self.last_loaded_mtime and mtime <= self.last_loaded_mtime:
            return self.total_docs > 0

        self._reset()
        wb = None
        try:
            wb = load_workbook(self.training_path, read_only=True, data_only=True)
            sheet = wb.active
            first_row = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True), ())
            header = [str(val).strip() if val is not None else "" for val in first_row]
            tag_col, text_cols = self._find_columns(header)
            if tag_col is None:
                logging.warning("Geen 'Tag' kolom gevonden in trainingsbestand.")
                return False

            for row in sheet.iter_rows(min_row=2, values_only=True):
                if not row:
                    continue

                tag_val = ""
                if len(row) > tag_col and row[tag_col] is not None:
                    tag_val = str(row[tag_col]).strip()
                if not tag_val:
                    continue
                if self.allowed_tags and tag_val not in self.allowed_tags:
                    # Sla rijen met onbekende tags over om ruis te voorkomen
                    continue

                text_parts: List[str] = []
                for idx in text_cols:
                    if idx < len(row) and row[idx] not in (None, ""):
                        text_parts.append(str(row[idx]))
                tokens = self._tokenize(" ".join(text_parts))
                if not tokens:
                    continue

                self.total_docs += 1
                doc_tokens = set(tokens)
                for tok in doc_tokens:
                    self.token_doc_freq[tok] += 1
                for tok in tokens:
                    self.tag_token_freq[tag_val][tok] += 1
                    self.tag_totals[tag_val] += 1

            self.last_loaded_mtime = mtime
            return self.total_docs > 0
        except Exception as exc:  # noqa: BLE001
            logging.error("Fout bij laden trainingsdata: %s", exc)
            return False
        finally:
            if wb:
                wb.close()

    def recommend(self, transaction: Dict[str, str], top_k: int = 3) -> List[Dict[str, float | str]]:
        """Geef een lijst met tags en scores terug op basis van de transactievelden."""
        if not self.load():
            return []

        tokens: List[str] = []
        for key in (
            "mededelingen",
            "omschrijving",
            "naam",
            "rekening",
            "tegenrekening",
            "mutatiesoort",
            "code",
            "memo",
        ):
            value = transaction.get(key)
            if value:
                tokens.extend(self._tokenize(str(value)))
        if not tokens:
            return []

        tf = Counter(tokens)
        suggestions = []
        for tag, freq in self.tag_token_freq.items():
            total = self.tag_totals.get(tag, 0) or 1
            score = 0.0
            for token, count in tf.items():
                tag_tf = freq.get(token, 0)
                if tag_tf == 0:
                    continue
                idf = math.log(1 + (self.total_docs / (1 + self.token_doc_freq.get(token, 0))))
                score += (tag_tf / total) * count * idf
            if score > 0:
                suggestions.append({"tag": tag, "score": round(score, 4)})

        suggestions.sort(key=lambda item: item["score"], reverse=True)
        return suggestions[:top_k]
