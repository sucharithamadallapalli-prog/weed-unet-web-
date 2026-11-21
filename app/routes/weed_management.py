
from flask import Blueprint, render_template, session
from flask_login import login_required

bp = Blueprint("weed_management", __name__)

ADVICE = {
    "Low": {
        "en": [
            "Scout again in 1–2 weeks.",
            "Spot-treat or hand-weed affected patches.",
            "Maintain healthy crop cover and mulch."
        ],
        "te": [
            "1–2 వారాల తర్వాత మళ్లీ పరిశీలించండి.",
            "కలుపు ఉన్న ప్రాంతాల్లో మాత్రమే చికిత్స చేయండి లేదా చేతితో తొలగించండి.",
            "పంట కవర్ మరియు మల్చ్‌ను ఆరోగ్యంగా నిర్వహించండి."
        ],
        "ta": [
            "1–2 வாரங்களுக்குப் பிறகு மீண்டும் ஆய்வு செய்யவும்.",
            "களை உள்ள பகுதிகளில் மட்டும் சிகிச்சை அளிக்கவும் அல்லது கையால் அகற்றவும்.",
            "பயிர் மூடலையும் மூடாக்கையும் நன்றாகப் பராமரிக்கவும்."
        ],
        "hi": [
            "1–2 सप्ताह बाद फिर से निरीक्षण करें।",
            "प्रभावित क्षेत्रों में ही उपचार करें या हाथ से खरपतवार हटाएँ।",
            "फसल की छतरी और मल्च को स्वस्थ बनाए रखें।"
        ]
    },

    "Moderate": {
        "en": [
            "Plan targeted herbicide application or mechanical cultivation.",
            "Use the detection mask to identify areas needing treatment.",
            "Re-image the field about 7 days after treatment."
        ],
        "te": [
            "లక్ష్యిత కలుపు మందుల వినియోగం లేదా యాంత్రిక కలుపు తొలగింపును ప్రణాళిక చేయండి.",
            "చికిత్స అవసరమైన ప్రాంతాలను గుర్తించడానికి డిటెక్షన్ మాస్క్‌ను ఉపయోగించండి.",
            "చికిత్స తర్వాత సుమారు 7 రోజులకల్లా పొలాన్ని మళ్లీ చిత్రీకరించండి."
        ],
        "ta": [
            "குறிப்பிட்ட பகுதிகளில் களைக்கொல்லி பயன்படுத்துதல் அல்லது இயந்திர முறையில் களை அகற்றுதல் திட்டமிடவும்.",
            "சிகிச்சை தேவைப்படும் பகுதிகளை அடையாளம் காண கண்டறிதல் முகமூடியைப் பயன்படுத்தவும்.",
            "சிகிச்சைக்குப் பிறகு சுமார் 7 நாட்களில் வயலை மீண்டும் படமெடுக்கவும்."
        ],
        "hi": [
            "लक्षित खरपतवारनाशक छिड़काव या यांत्रिक निराई की योजना बनाएँ।",
            "उपचार की आवश्यकता वाले क्षेत्रों की पहचान के लिए डिटेक्शन मास्क का उपयोग करें।",
            "उपचार के लगभग 7 दिन बाद खेत की दोबारा तस्वीर लें।"
        ]
    },

    "High": {
        "en": [
            "Assess the field promptly; extensive treatment may be needed.",
            "Consult a local agronomist about herbicide selection and resistance.",
            "Review crop rotation and weed seedbank management."
        ],
        "te": [
            "పొలాన్ని వెంటనే పరిశీలించండి; విస్తృత చికిత్స అవసరమవచ్చు.",
            "కలుపు మందుల ఎంపిక మరియు నిరోధకత గురించి స్థానిక వ్యవసాయ నిపుణుడిని సంప్రదించండి.",
            "పంట మార్పిడి మరియు కలుపు విత్తన నిల్వ నిర్వహణను సమీక్షించండి."
        ],
        "ta": [
            "வயலை விரைவாக ஆய்வு செய்யவும்; பரவலான சிகிச்சை தேவைப்படலாம்.",
            "களைக்கொல்லி தேர்வு மற்றும் எதிர்ப்புத் திறன் குறித்து உள்ளூர் வேளாண் நிபுணரிடம் ஆலோசிக்கவும்.",
            "பயிர் சுழற்சி மற்றும் களை விதை வங்கி மேலாண்மையை மறுபரிசீலனை செய்யவும்."
        ],
        "hi": [
            "खेत का तुरंत निरीक्षण करें; व्यापक उपचार की आवश्यकता हो सकती है।",
            "खरपतवारनाशक के चयन और प्रतिरोध के बारे में स्थानीय कृषि विशेषज्ञ से सलाह लें।",
            "फसल चक्र और खरपतवार बीज बैंक प्रबंधन की समीक्षा करें।"
        ]
    }
}


@bp.route("/weed-management")
@login_required
def index():
    language = session.get("language", "en")

    if language not in ("en", "te", "ta", "hi"):
        language = "en"

    translated_advice = {}

    for level, translations in ADVICE.items():
        translated_advice[level] = translations[language]

    return render_template(
        "weed_management.html",
        advice=translated_advice
    )
