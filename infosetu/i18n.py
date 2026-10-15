LANGS = [("en", "English"), ("hi", "हिंदी"), ("mr", "मराठी")]

_RAW = """
tagline|Submit and track public information requests.|सार्वजनिक सूचना अनुरोध जमा करें और ट्रैक करें।|सार्वजनिक माहिती विनंत्या सादर करा आणि ट्रॅक करा.
login|Login|लॉगिन|लॉगिन
signup|Sign Up|साइन अप|साइन अप
logout|Logout|लॉगआउट|लॉगआउट
username|Username|उपयोगकर्ता नाम|वापरकर्ता नाव
password|Password|पासवर्ड|पासवर्ड
confirm|Confirm password|पासवर्ड की पुष्टि करें|पासवर्डची पुष्टी करा
welcome|Welcome back|वापसी पर स्वागत है|पुन्हा स्वागत आहे
create_account|Create account|खाता बनाएं|खाते तयार करा
dashboard|Dashboard|डैशबोर्ड|डॅशबोर्ड
new_request|New Request|नई शिकायत|नवीन तक्रार
my_requests|My Requests|मेरी शिकायतें|माझ्या तक्रारी
total|Total Requests|कुल शिकायतें|एकूण तक्रारी
in_progress_c|In Progress|प्रगति पर|प्रगतीपथावर
completed_c|Completed|पूर्ण|पूर्ण
pending_c|Pending|लंबित|प्रलंबित
department|Department|विभाग|विभाग
category|Category|शिकायत का प्रकार|तक्रारीचा प्रकार
description|Description|शिकायत का विवरण|तक्रारीचे वर्णन
submit|Submit|जमा करें|सबमिट करा
edit|Edit|संपादित करें|संपादित करा
save|Save|सहेजें|जतन करा
view|View|देखें|पहा
search|Search|खोजें|शोधा
status|Status|स्थिति|स्थिती
date|Date|तारीख|तारीख
request_id|Request ID|शिकायत क्रमांक|तक्रार क्रमांक
remarks|Remarks|टिप्पणी|शेरा
timeline|Status timeline|स्थिति समयरेखा|स्थिती कालरेखा
notifications|Notifications|सूचनाएं|सूचना
notif_msg|Request {0} status changed to {1}|शिकायत {0} की स्थिति बदलकर {1} हुई|तक्रार {0} ची स्थिती {1} झाली
mark_read|Mark all read|सभी पढ़ा हुआ चिह्नित करें|सर्व वाचले म्हणून चिन्हित करा
recent|Recent Requests|हाल की शिकायतें|अलीकडील तक्रारी
all_status|All|सभी|सर्व
all_dept|All departments|सभी विभाग|सर्व विभाग
users|Users|उपयोगकर्ता|वापरकर्ते
requester|Requester|शिकायतकर्ता|तक्रारदार
original_lang|Original language|मूल भाषा|मूळ भाषा
by_dept|Requests by Department|विभागानुसार शिकायतें|विभागानुसार तक्रारी
update|Update|अपडेट करें|अद्यतनित करा
role|Role|भूमिका|भूमिका
joined|Joined|जुड़ने की तारीख|सामील झाले
count|Requests|शिकायतें|तक्रारी
locked|This request is being processed and can no longer be edited.|यह शिकायत प्रक्रिया में है, अब संपादित नहीं की जा सकती।|ही तक्रार प्रक्रियेत आहे, आता संपादित करता येणार नाही.
no_data|Nothing here yet.|अभी कुछ नहीं है।|अजून काही नाही.
err_login|Invalid username or password.|उपयोगकर्ता नाम या पासवर्ड गलत है।|वापरकर्ता नाव किंवा पासवर्ड चुकीचा आहे.
err_exists|Username is invalid or already taken.|उपयोगकर्ता नाम अमान्य है या पहले से मौजूद है।|वापरकर्ता नाव अवैध आहे किंवा आधीच वापरात आहे.
err_match|Passwords do not match.|पासवर्ड मेल नहीं खाते।|पासवर्ड जुळत नाहीत.
err_short|Password must be at least 6 characters.|पासवर्ड कम से कम 6 अक्षरों का होना चाहिए।|पासवर्ड किमान 6 अक्षरांचा असावा.
full_name|Full name|पूरा नाम|पूर्ण नाव
email|Email|ईमेल|ईमेल
documents|Supporting document|सहायक दस्तावेज़|सहाय्यक कागदपत्र
doc_hint|PDF, JPG or PNG, max 5 MB|PDF, JPG या PNG, अधिकतम 5 MB|PDF, JPG किंवा PNG, कमाल 5 MB
keep_doc|Leave empty to keep the current document.|मौजूदा दस्तावेज़ रखने के लिए खाली छोड़ें।|सध्याचे कागदपत्र ठेवण्यासाठी रिकामे सोडा.
download|Download document|दस्तावेज़ डाउनलोड करें|कागदपत्र डाउनलोड करा
err_fields|Name, a valid email, category and description are required.|नाम, सही ईमेल, शिकायत का प्रकार और विवरण आवश्यक हैं।|नाव, वैध ईमेल, तक्रारीचा प्रकार आणि वर्णन आवश्यक आहेत.
err_doc|A supporting document (PDF, JPG or PNG, max 5 MB) is required.|सहायक दस्तावेज़ (PDF, JPG या PNG, अधिकतम 5 MB) आवश्यक है।|सहाय्यक कागदपत्र (PDF, JPG किंवा PNG, कमाल 5 MB) आवश्यक आहे.
saved|Saved.|सहेजा गया।|जतन केले.
submitted_msg|Request submitted.|शिकायत जमा हो गई।|तक्रार सबमिट झाली.
err_script|Please write the {0} only in {1} (the language you selected). Other languages are not accepted.|कृपया {0} केवल {1} में लिखें (आपकी चुनी हुई भाषा)। अन्य भाषा स्वीकार नहीं है।|कृपया {0} फक्त {1} मध्ये लिहा (तुम्ही निवडलेली भाषा). इतर भाषा स्वीकारली जात नाही.
err_len|The {0} is too short. Please write at least {1} words with specific details (what happened, where, and since when).|{0} बहुत छोटा है। कृपया कम से कम {1} शब्दों में स्पष्ट जानकारी लिखें (क्या हुआ, कहाँ, और कब से)।|{0} खूप लहान आहे. कृपया किमान {1} शब्दांत स्पष्ट माहिती लिहा (काय झाले, कुठे, आणि केव्हापासून).
err_gib|The {0} does not look like a meaningful sentence. Please describe the real problem in proper words.|{0} अर्थपूर्ण वाक्य नहीं लगता। कृपया असली समस्या सही शब्दों में लिखें।|{0} अर्थपूर्ण वाक्य वाटत नाही. कृपया खरी समस्या योग्य शब्दांत लिहा.
err_rep|The {0} repeats the same words. Please describe the problem clearly.|{0} में वही शब्द बार-बार हैं। कृपया समस्या स्पष्ट लिखें।|{0} मध्ये तेच शब्द पुन्हा पुन्हा आहेत. कृपया समस्या स्पष्ट लिहा.
err_mixlang|The text looks like {1}, but the selected language is {0}. Please rewrite it in {0} or change the language.|यह पाठ {1} जैसा लगता है, जबकि चुनी हुई भाषा {0} है। कृपया इसे {0} में लिखें या भाषा बदलें।|हा मजकूर {1} सारखा वाटतो, पण निवडलेली भाषा {0} आहे. कृपया {0} मध्ये लिहा किंवा भाषा बदला.
err_dept_other|Your text looks related to "{0}", but you selected "{1}". Please choose the correct department.|आपका विवरण "{0}" से संबंधित लगता है, लेकिन आपने "{1}" चुना है। कृपया सही विभाग चुनें।|तुमचा मजकूर "{0}" शी संबंधित वाटतो, पण तुम्ही "{1}" निवडले आहे. कृपया योग्य विभाग निवडा.
err_dept_none|Your text does not seem related to the {0} department. Please mention the actual problem.|आपका विवरण {0} विभाग से संबंधित नहीं लगता। कृपया वास्तविक समस्या लिखें।|तुमचा मजकूर {0} विभागाशी संबंधित वाटत नाही. कृपया प्रत्यक्ष समस्या लिहा.
err_name|Please enter a valid full name (letters only, no numbers or symbols).|कृपया सही पूरा नाम लिखें (केवल अक्षर, अंक या चिह्न नहीं)।|कृपया योग्य पूर्ण नाव लिहा (फक्त अक्षरे, अंक किंवा चिन्हे नाहीत).
err_dup|You have already submitted an identical request.|आप यही शिकायत पहले ही जमा कर चुके हैं।|तुम्ही हीच तक्रार आधीच सबमिट केली आहे.
err_rate|Too many requests in a short time. Please try again after some time.|कम समय में बहुत अधिक शिकायतें। कृपया कुछ समय बाद फिर प्रयास करें।|कमी वेळात खूप तक्रारी. कृपया थोड्या वेळाने पुन्हा प्रयत्न करा.
hint_lang|Write the category and description only in {0}. Meaningless, random or unrelated text will be rejected.|शिकायत का प्रकार और विवरण केवल {0} में लिखें। अर्थहीन, बेतरतीब या असंबंधित पाठ स्वीकार नहीं किया जाएगा।|तक्रारीचा प्रकार आणि वर्णन फक्त {0} मध्ये लिहा. अर्थहीन, यादृच्छिक किंवा असंबंधित मजकूर स्वीकारला जाणार नाही.
ph_cat|e.g. No water supply|जैसे: पानी की आपूर्ति बंद|उदा. पाणीपुरवठा बंद
ph_desc|Example: There has been no water in our street for 5 days. Please fix it urgently.|उदाहरण: हमारी गली में 5 दिनों से पानी नहीं आ रहा है। कृपया जल्द ठीक करवाएं।|उदाहरण: आमच्या गल्लीत ५ दिवसांपासून पाणी येत नाही. कृपया लवकर दुरुस्ती करावी.
quality|Quality score|गुणवत्ता स्कोर|गुणवत्ता गुण
"""
T = {}
for _l in _RAW.strip().splitlines():
    k, en, hi, mr = _l.split("|")
    T[k] = {"en": en, "hi": hi, "mr": mr}

STATUSES = {
    "submitted": {"en": "Submitted", "hi": "जमा की गई", "mr": "सबमिट केली"},
    "received": {"en": "Received", "hi": "प्राप्त हुई", "mr": "प्राप्त झाली"},
    "assigned": {"en": "Sent to Department", "hi": "विभाग को भेजी गई", "mr": "विभागाकडे पाठवली"},
    "in_progress": {"en": "In Progress", "hi": "प्रगति पर", "mr": "प्रगतीपथावर"},
    "resolved": {"en": "Resolved", "hi": "समाधान किया गया", "mr": "निराकरण झाले"},
}

DEPTS = {
    "water": {"en": "Water Supply", "hi": "जल आपूर्ति", "mr": "पाणीपुरवठा"},
    "garbage": {"en": "Garbage Collection", "hi": "कचरा संग्रहण", "mr": "कचरा संकलन"},
    "health": {"en": "Health Services", "hi": "स्वास्थ्य सेवाएं", "mr": "आरोग्य सेवा"},
    "education": {"en": "Education", "hi": "शिक्षा", "mr": "शिक्षण"},
    "agriculture": {"en": "Agriculture", "hi": "कृषि", "mr": "कृषी"},
    "roads": {"en": "Roads & Transport", "hi": "सड़क एवं परिवहन", "mr": "रस्ते व वाहतूक"},
    "electricity": {"en": "Electricity", "hi": "बिजली", "mr": "वीज"},
}
