
import csv
import io


CSV_TRANSLATIONS = {
    "en": {
        "id": "ID",
        "field": "Field",
        "original": "Original Image",
        "weed_percent": "Weed Coverage (%)",
        "severity": "Severity",
        "created_at": "Created At",
        "Low": "Low",
        "Moderate": "Moderate",
        "Medium": "Medium",
        "High": "High",
        "Severe": "Severe",
    },
    "te": {
        "id": "ఐడి",
        "field": "పొలం",
        "original": "అసలు చిత్రం",
        "weed_percent": "కలుపు విస్తీర్ణం (%)",
        "severity": "తీవ్రత",
        "created_at": "సృష్టించిన సమయం",
        "Low": "తక్కువ",
        "Moderate": "మధ్యస్థం",
        "Medium": "మధ్యస్థం",
        "High": "ఎక్కువ",
        "Severe": "తీవ్రమైన",
    },
    "ta": {
        "id": "ஐடி",
        "field": "வயல்",
        "original": "அசல் படம்",
        "weed_percent": "களை பரப்பளவு (%)",
        "severity": "தீவிரம்",
        "created_at": "உருவாக்கிய நேரம்",
        "Low": "குறைவு",
        "Moderate": "மிதமான",
        "Medium": "நடுத்தரம்",
        "High": "அதிகம்",
        "Severe": "மிக அதிகம்",
    },
    "hi": {
        "id": "आईडी",
        "field": "खेत",
        "original": "मूल छवि",
        "weed_percent": "खरपतवार क्षेत्र (%)",
        "severity": "तीव्रता",
        "created_at": "बनाने का समय",
        "Low": "कम",
        "Moderate": "मध्यम",
        "Medium": "मध्यम",
        "High": "अधिक",
        "Severe": "गंभीर",
    },
}


def analyses_to_csv(rows, language="en"):
    translations = CSV_TRANSLATIONS.get(
        language, CSV_TRANSLATIONS["en"]
    )

    # utf-8-sig helps Excel display Telugu, Tamil and Hindi correctly.
    buf = io.StringIO(newline="")
    writer = csv.writer(buf)

    writer.writerow([
        translations["id"],
        translations["field"],
        translations["original"],
        translations["weed_percent"],
        translations["severity"],
        translations["created_at"],
    ])

    for analysis in rows:
        severity = str(analysis.severity or "")
        translated_severity = translations.get(severity, severity)

        writer.writerow([
            analysis.id,
            analysis.field.name if analysis.field else "",
            analysis.original or "",
            analysis.weed_percent,
            translated_severity,
            (
                analysis.created_at.isoformat()
                if analysis.created_at
                else ""
            ),
        ])

    # Add a UTF-8 BOM for better compatibility with Excel.
    return "\ufeff" + buf.getvalue()


def summary(rows):
    if not rows:
        return {"count": 0, "avg": 0, "max": 0}

    percentages = [a.weed_percent for a in rows]

    return {
        "count": len(percentages),
        "avg": round(sum(percentages) / len(percentages), 2),
        "max": max(percentages),
    }
