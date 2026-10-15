"""Rule-based request analyzer (no internet / no paid AI needed).
Checks: language script, minimum detail, gibberish, repetition, Hindi-vs-Marathi mix-up,
department relevance, and a valid name. Returns (error_messages, quality_score)."""
import re
import unicodedata


def N(s):
    return unicodedata.normalize("NFD", s).replace("\u200c", "").replace("\u200d", "")


EN_COMMON = set("""a about above after again all also am an and any are as at be because been before being below between
both but by can could did do does doing down during each few for from further had has have having he her here hers him his
how i if in into is it its just me more most my no nor not now of off on once only or other our ours out over own same she
should so some such than that the their them then there these they this those through to too under until up us very was we
were what when where which while who whom why will with would you your yours since days day week weeks month months year
years last past near area street colony ward house people residents resident family families please kindly request urgent
urgently still many much every daily never always often already yet one two three four five six seven eight nine ten
nothing nobody none cannot don't can't isn't hasn't haven't didn't doesn't wasn't aren't it's there's we've problem issue
complaint repair fix resolve action immediately soon need needs required happening happened facing face faced getting got
get come comes coming stopped broken damaged blocked working work works inspect restore stable local places place side
main since morning evening night time times people children students old new two lakh""".split())

HI_STOP = set(map(N, """है हैं था थे थी में का की के से को पर और नहीं यह यहाँ यहां वह हम हमारे हमारी हमारा मेरे मेरा मेरी
रहा रही रहे गया गई गए कर करें करना कृपया लिए बहुत भी तक दिन दिनों पिछले जल्द अब सकता सकते हो हुआ हुई हुए जिससे क्योंकि
लेकिन तथा या एक कोई सभी क्षेत्र इस उस उन इन जो कि तो ही वाले वाली चुका चुकी आई आया आये रहती रहता सात पांच दो तीन चार
बाद पास साथ कारण समस्या शिकायत ऊपर नीचे आसपास लोग बच्चों बुजुर्गों खतरा सुनिश्चित नियमित""".split()))

MR_STOP = set(map(N, """आहे आहेत होते होती होता झाले झाली झाला मध्ये च्या चा ची चे चं ला ना आणि नाही नाहीत हे ही हा तो ती ते
आम्ही आमच्या आमचा आमची माझ्या माझे माझा गेल्या पासून साठी कृपया तसेच खूप दिवस दिवसांपासून येत येते येणारे जात जाते करावी करा
केली केले करून येथे तेथे परिसरात परिसरातील अजून फार सुद्धा देखील पण किंवा एक कोणी सर्व या त्या ज्या की तर रोज दररोज वाया सुरू
समस्या तक्रार आठ सात पाच दोन तीन चार लोक मुले धोका तातडीने कमी""".split()))

HI_ONLY = set(map(N, "है हैं नहीं और के को में से रहा रही रहे गया गई गए था थी थे हमारे हमारी हमारा लिए पिछले".split()))
MR_ONLY = set(map(N, """आहे आहेत नाही नाहीत आणि मध्ये च्या साठी झाले झाली झाला होते होती गेल्या आमच्या आमची आमचा पासून करावी
तसेच दिवसांपासून""".split()))

KEYS = {
 "water": {
  "en": "water|=tap|=taps|=pipe|=pipes|pipeline|leak|tanker|drinking|sewage|drain|contaminat|borewell|=well|=wells|=sewer",
  "hi": "पानी|जल |जलापूर्ति|नल|पाइप|लीक|टैंकर|पेयजल|गंदा|दूषित|बोरवेल|नाली|सीवर",
  "mr": "पाणी|जल |नळ|पाईप|पाइप|गळती|टँकर|गढूळ|दूषित|विहीर|बोअरवेल|गटार"},
 "garbage": {
  "en": "garbage|waste|trash|litter|dustbin|sweep|sanitation|dump|=clean|=cleaning|stink|smell|mosquito|hygiene|collection|filth|rubbish|sewer",
  "hi": "कचरा|कचरे|कूड़ा|कूड़े|सफाई|गंदगी|बदबू|मच्छर|डंप|स्वच्छता|दुर्गंध|नाला|नाली",
  "mr": "कचर|कचऱ|केरकचरा|घाण|सफाई|स्वच्छता|दुर्गंध|डास|कचराकुंडी|गटार|सांडपाणी"},
 "health": {
  "en": "health|hospital|clinic|doctor|medicine|nurse|patient|vaccin|ambulance|dispensary|treatment|disease|fever|pharmacy|medical|drug|=opd|checkup|surgery|sick",
  "hi": "स्वास्थ्य|अस्पताल|डॉक्टर|डाक्टर|दवा|मरीज|इलाज|टीका|एम्बुलेंस|एंबुलेंस|बुखार|नर्स|क्लिनिक|चिकित्सा|ओपीडी|खांसी|बीमार|उपचार",
  "mr": "आरोग्य|रुग्णालय|दवाखाना|डॉक्टर|डाॅक्टर|औषध|रुग्ण|उपचार|लसीकरण|रुग्णवाहिका|परिचारिका|क्लिनिक|तपासणी|ओपीडी|आजार|ताप "},
 "education": {
  "en": "school|teacher|=class|classroom|student|education|college|exam|scholarship|=book|=books|textbook|principal|=fee|=fees|uniform|anganwadi|library|=meal|syllabus|admission|tuition",
  "hi": "स्कूल|विद्यालय|शिक्षक|शिक्षा|छात्र|विद्यार्थी|कक्षा|कॉलेज|परीक्षा|छात्रवृत्ति|किताब|पुस्तक|मध्याह्न|प्रधानाचार्य|आंगनवाड़ी|फीस|शुल्क|प्रवेश|पाठ्य",
  "mr": "शाळा|शिक्षक|शिक्षण|विद्यार्थी|वर्ग|महाविद्यालय|परीक्षा|शिष्यवृत्ती|पुस्तक|गणवेश|मुख्याध्यापक|अंगणवाडी|फी|शुल्क|प्रवेश|अभ्यासक्रम"},
 "agriculture": {
  "en": "agricultur|farm|crop|=seed|=seeds|fertili|irrigation|soil|harvest|tractor|subsidy|pesticide|mandi|livestock|drought|=field|=fields|cattle",
  "hi": "कृषि|किसान|फसल|खेत|बीज|खाद|सिंचाई|मिट्टी|ट्रैक्टर|सब्सिडी|कीटनाशक|मंडी|सूखा|पशु|मवेशी",
  "mr": "कृषी|शेतकरी|पीक|शेत|बियाणे|खत |खते|सिंचन|माती|ट्रॅक्टर|अनुदान|कीटकनाशक|बाजार समिती|दुष्काळ|पशु|जनावर"},
 "roads": {
  "en": "road|pothole|highway|bridge|traffic|=bus|=buses|transport|footpath|pavement|signal|streetlight|speed|accident|crossing|vehicle|parking|metro|flyover",
  "hi": "सड़क|गड्ढ|राजमार्ग|ब्रिज|पुलिया|फ्लाईओवर|यातायात|ट्रैफिक|बस स्टॉप|बस सेवा|बसें|परिवहन|फुटपाथ|सिग्नल|स्ट्रीट लाइट|दुर्घटना|हादसा|वाहन|पार्किंग|रास्ता|रास्ते",
  "mr": "रस्त|खड्ड|महामार्ग|उड्डाणपूल|वाहतूक|बस स्टॉप|बसस्थानक|बस सेवा|परिवहन|पदपथ|सिग्नल|पथदिवा|अपघात|वाहन|पार्किंग"},
 "electricity": {
  "en": "electric|power|voltage|transformer|=wire|=wires|wiring|cable|outage|blackout|=meter|=pole|=poles|fuse|load shedding|=light|=lights|lighting|current|=bulb",
  "hi": "बिजली|विद्युत|पावर|वोल्टेज|ट्रांसफार्मर|ट्रांसफॉर्मर|केबल|वायर|कटौती|मीटर|खंभा|बत्ती|लाइट|करंट|फ्यूज|लोडशेडिंग",
  "mr": "वीज|विद्युत|पॉवर|व्होल्टेज|ट्रान्सफॉर्मर|केबल|वायर|मीटर|खांब|लाईट|करंट|फ्यूज|भारनियमन|दिवे"},
}
KEYS = {s: {l: [N(k) if l != "en" else k for k in v.split("|")] for l, v in d.items()} for s, d in KEYS.items()}
EN_KEYWORDS = {k.lstrip("=") for d in KEYS.values() for k in d["en"]}
KEYMASH = ("qwer", "asdf", "zxcv", "hjkl", "sdfg", "dfgh", "wert", "erty", "rtyu", "tyui", "yuio", "uiop", "xcvb", "cvbn", "vbnm")
ACRONYM = re.compile(r"\b[A-Z]{2,6}\b")
MIN_WORDS = 8


def tokens(text, lang):
    if lang == "en":
        return re.findall(r"[a-z]+(?:'[a-z]+)?", text.lower())
    return re.findall(r"[\u0900-\u0963\u0971-\u097F]+", text)


def script_ok(text, lang):
    if lang != "en":
        text = ACRONYM.sub(" ", text)
    lat = dev = oth = 0
    for c in text:
        o = ord(c)
        if o < 128 and c.isalpha():
            lat += 1
        elif 0x900 <= o <= 0x963 or 0x971 <= o <= 0x97F:
            dev += 1
        elif c.isalpha():
            oth += 1
    tot = lat + dev + oth
    if tot == 0:
        return False
    if lang == "en":
        return dev == 0 and oth / tot <= 0.03
    return (lat + oth) / tot <= 0.05


def en_gib(w):
    if len(w) < 3:
        return False
    v = sum(c in "aeiouy" for c in w)
    return (v == 0 or (len(w) >= 5 and v / len(w) < 0.2) or re.search(r"[^aeiouy]{5,}", w) is not None
            or re.search(r"(.)\1\1", w) is not None or any(k in w for k in KEYMASH))


def is_known(w, lang):
    if lang == "en":
        return w in EN_COMMON or any(w == k or (len(k) >= 4 and w.startswith(k)) for k in EN_KEYWORDS)
    stop = HI_STOP if lang == "hi" else MR_STOP
    n = N(w)
    return n in stop or any(len(k.strip()) >= 2 and k.strip() in n for d in KEYS.values() for k in d[lang])


def repeated(toks):
    if len(toks) < 4:
        return False
    if len(set(toks)) / len(toks) < 0.5:
        return True
    return max(toks.count(w) for w in set(toks)) / len(toks) > 0.4 and len(toks) >= 5


def meaningful(toks, lang, is_desc):
    known = sum(1 for w in toks if is_known(w, lang))
    if lang == "en":
        gib = sum(1 for w in toks if not is_known(w, "en") and en_gib(w))
        if gib / len(toks) > 0.25:
            return False, known
    if is_desc:
        return known >= 3 and known / len(toks) >= 0.2, known
    return True, known


def mixed_with(toks, lang):
    """Return 'hi'/'mr' if the text looks like the OTHER Devanagari language, else None."""
    if lang not in ("hi", "mr"):
        return None
    dt = {N(w) for w in toks}
    hi_n, mr_n = len(dt & HI_ONLY), len(dt & MR_ONLY)
    other, other_n, own_n = ("mr", mr_n, hi_n) if lang == "hi" else ("hi", hi_n, mr_n)
    return other if other_n >= 2 and other_n > own_n else None


def hits(text, toks, lang, slug):
    padded = " " + N(text) + " "
    n = 0
    for k in KEYS[slug][lang]:
        if lang == "en":
            n += sum(1 for w in toks if (w == k[1:] if k.startswith("=") else w.startswith(k)))
        elif k in padded:
            n += 1
    return n


def name_ok(name):
    n = name.strip()
    if len(n) < 2 or len(n) > 60:
        return False
    if not all(unicodedata.category(c)[0] in "LM" or c in " .'-" for c in n):
        return False
    low = n.lower()
    if re.search(r"(.)\1\1", low) or any(k in low for k in KEYMASH):
        return False
    latin = re.sub(r"[^a-z]", "", low)
    return not (len(latin) >= 4 and not re.search(r"[aeiouy]", latin))


def analyze(d, lang, slug, tr, lang_name, dept_label):
    errs, score, ok_fields = [], 50, True
    if not name_ok(d["full_name"]):
        errs.append(tr("err_name"))
    texts = {}
    for key, text, is_desc in (("category", d["category"], False), ("description", d["description"], True)):
        fname, text = tr(key), text.strip()
        if not script_ok(text, lang):
            errs.append(tr("err_script").format(fname, lang_name)); ok_fields = False; continue
        toks = tokens(text, lang)
        if is_desc and (len(toks) < MIN_WORDS or len(text) < 30):
            errs.append(tr("err_len").format(fname, MIN_WORDS)); ok_fields = False; continue
        if not is_desc and (len(text) < 3 or not toks):
            errs.append(tr("err_gib").format(fname)); ok_fields = False; continue
        other = mixed_with(toks, lang) if is_desc else None
        if other:
            errs.append(tr("err_mixlang").format(lang_name, {"hi": "हिंदी", "mr": "मराठी"}[other])); ok_fields = False; continue
        if repeated(toks):
            errs.append(tr("err_rep").format(fname)); ok_fields = False; continue
        good, known = meaningful(toks, lang, is_desc)
        if not good:
            errs.append(tr("err_gib").format(fname)); ok_fields = False; continue
        texts[key] = (text, toks, known)
    if ok_fields and len(texts) == 2:
        both = texts["category"][0] + " " + texts["description"][0]
        btoks = tokens(both, lang)
        own = hits(both, btoks, lang, slug)
        if own == 0:
            best = max(((hits(both, btoks, lang, s), s) for s in KEYS if s != slug), default=(0, None))
            if best[0] > 0:
                errs.append(tr("err_dept_other").format(dept_label(best[1]), dept_label(slug)))
            else:
                errs.append(tr("err_dept_none").format(dept_label(slug)))
        else:
            dtoks, known = texts["description"][1], texts["description"][2]
            score += min(30, len(dtoks)) + (10 if own >= 2 else 0) + (10 if known / len(dtoks) >= 0.35 else 0)
    return errs, min(100, score)
