"""
Script to extract, clean, and structure all 21 chapters of Mass Spoken English
from mass_spoken_english_ocr.txt into edusarthi_backend/edusarthi_backend/data/mass_spoken_curriculum.json
"""
import json
import re
import random

def clean_text(s: str) -> str:
    s = s.strip()
    s = re.sub(r'^[0-9lL|I\.\,\-\s\*\#\>]+', '', s)
    s = re.sub(r'\s+', ' ', s)
    s = s.replace('बह', 'वह').replace('नही', 'नहीं').replace('तुम्हे', 'तुम्हें').replace('डाटने', 'डांटने')
    return s.strip()

def clean_english(s: str) -> str:
    s = s.strip()
    s = re.sub(r'^\(?[SNIW0-9\.\,\-]+\)?\s*', '', s)
    s = re.sub(r'^[0-9lL|I\.\,\-\s\*\#\>\\]+', '', s)
    s = s.replace('‘', '').replace('’', "'").replace('“', '').replace('”', '')
    s = s.replace('Ishe', 'Is he').replace('Iam', 'I am').replace('Tcan', 'I can')
    s = s.replace('व can', 'I can').replace('व could', 'I could')
    s = s.replace('Thaye', 'I have').replace('T have', 'I have').replace('T want', 'I want')
    s = s.replace('व्‌ wanted', 'I wanted').replace('T was', 'I was')
    s = s.replace('Hae', 'you').replace('Lam', 'I am').replace('] am', 'I am')
    s = s.replace('J am', 'I am')
    s = s.replace('noughty', 'naughty').replace('alway', 'away')
    
    # Common OCR drop of first capital letter
    if s.startswith("hut "):
        s = "S" + s
    elif s.startswith("et's "):
        s = "L" + s
    elif s.startswith("e would "):
        s = "W" + s
    elif s.startswith("he is fond "):
        s = "S" + s
    elif s.startswith("don't "):
        s = "I " + s
    elif s.startswith("did not "):
        s = "I " + s
    elif s.startswith("am going "):
        s = "I " + s
    elif s.startswith("gets "):
        s = "He " + s
    elif s.startswith("make you "):
        s = "I " + s

    # Clean trailing digits or garbage
    s = re.sub(r'[\,\s0-9]+$', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

def is_clean_hindi_sentence(s: str) -> bool:
    if len(s) < 5 or len(s) > 80:
        return False
    bad_words = [
        'definition', 'helping verb', 'singular', 'plural', 'प्रयोग करते', 'नियम',
        'संबंधित', 'अनुसार', 'structure', 'example', 'chapter', 'objective pronoun',
        'english classes', 'mass study', 'join online'
    ]
    s_low = s.lower()
    for b in bad_words:
        if b in s_low:
            return False
    dev_count = len(re.findall(r'[\u0900-\u097F]', s))
    return dev_count >= 5

def is_clean_english_sentence(s: str) -> bool:
    if len(s) < 4 or len(s) > 85:
        return False
    if re.search(r'[\u0900-\u097F]', s):
        return False
    # Must have typical English sentence markers
    return bool(re.search(
        r'\b(I|He|She|It|We|You|They|This|That|These|Those|There|Let|Good|The|Do|Does|Did|Is|Am|Are|Was|Were|Will|Can|Could|Should|May|Must|Would|What|Where|Why|When|Who|How|Shut|Talk|Throw|Don\'t)\b',
        s, re.IGNORECASE
    ))

def make_sentence_builder(hindi: str, english: str):
    clean_en = re.sub(r'[?!.]+$', '', english).strip()
    words = clean_en.split()
    scrambled = words.copy()
    random.seed(len(hindi) + len(english))
    random.shuffle(scrambled)
    if scrambled == words and len(words) > 2:
        scrambled[0], scrambled[1] = scrambled[1], scrambled[0]
    return {
        "hindi": hindi,
        "english": english,
        "target_words": words,
        "scrambled_words": scrambled
    }

def main():
    with open(r'd:\EduSarthi\data mass spoken\mass_spoken_english_ocr.txt', 'r', encoding='utf-8', errors='ignore') as f:
        full_text = f.read()

    pages = full_text.split('===== PAGE ')

    curriculum = {
        "metadata": {
            "source": "Mass Spoken English Complete Course",
            "total_chapters": 21,
            "total_pages": 150,
            "description": "Comprehensive Hindi-to-English Spoken English Course with formulas, examples, worksheets, and interactive drills."
        },
        "chapters": []
    }

    chapters_meta = [
        {
            "id": 1,
            "title": "Self Introduction",
            "hindi_title": "अपना परिचय देना सीखें",
            "category": "Foundation",
            "level": "beginner",
            "emoji": "👋",
            "page_start": 3,
            "page_end": 5,
            "definition": "जब भी हम किसी इंटरव्यू, ऑफिस मीटिंग, फैमिली गैदरिंग या नए लोगों से मिलते हैं, तो हमें अपना परिचय (Self Introduction) देना होता है। Mass Spoken तरीके से स्टेप-बाय-स्टेप परिचय देना सबसे आसान है।",
            "structures": [
                {"name": "Formal Greeting", "formula": "Good morning / Good afternoon / Good evening Sir/Madam", "hindi": "बड़ों व फॉर्मल जगह पर"},
                {"name": "Name", "formula": "My name is [Full Name] / I am [Name]", "hindi": "नाम बताने का सही तरीका"},
                {"name": "Place", "formula": "I belong to [City] / I am from [City]", "hindi": "कहाँ से हैं"},
                {"name": "Qualification", "formula": "I have completed [Degree] / I am pursuing [Course]", "hindi": "पढ़ाई व शिक्षा"},
                {"name": "Closing", "formula": "That's all about me, thank you!", "hindi": "परिचय समाप्त करने का तरीका"}
            ],
            "golden_rules": [
                "कभी भी 'Myself Rohit' न कहें – यह व्याकरण की दृष्टि से गलत है। 'My name is...' या 'I am...' कहें।",
                "उम्र या एडजेक्टिव जोड़ें: 'I am punctual, self-motivated and hardworking.'",
                "अंत में हमेशा 'That's all about me, thank you' कहकर धन्यवाद दें।"
            ],
            "vocabulary": [
                {"word": "Punctual", "meaning": "समय का पाबंद", "example": "I am a punctual person."},
                {"word": "Self-motivated", "meaning": "खुद से प्रेरित", "example": "She is self-motivated."},
                {"word": "Belong to", "meaning": "का निवासी होना", "example": "I belong to Patna."},
                {"word": "Pursuing", "meaning": "कर रहा हूँ / जारी है", "example": "I am pursuing graduation."}
            ],
            "manual_examples": [
                {"hindi": "मेरा नाम रोहित कुमार है।", "english": "My name is Rohit Kumar."},
                {"hindi": "मैं पटना, बिहार से हूँ।", "english": "I belong to Patna, Bihar."},
                {"hindi": "मैं एक शिक्षक हूँ।", "english": "I am a teacher."},
                {"hindi": "मैंने पटना विश्वविद्यालय से स्नातक पूरा किया है।", "english": "I have completed graduation from Patna University."},
                {"hindi": "मेरी रुचि किताबें पढ़ने में है।", "english": "My hobby is reading books."},
                {"hindi": "मेरी ताकत मेरा संचार कौशल है।", "english": "My strength is my communication skill."},
                {"hindi": "मैं समय का पाबंद और मेहनती हूँ।", "english": "I am punctual and hardworking."},
                {"hindi": "मेरे बारे में बस इतना ही, धन्यवाद।", "english": "That's all about me, thank you."}
            ]
        },
        {
            "id": 2,
            "title": "Basics of English",
            "hindi_title": "अंग्रेजी की बुनियाद (वर्णमाला और कर्ता)",
            "category": "Foundation",
            "level": "beginner",
            "emoji": "📖",
            "page_start": 6,
            "page_end": 7,
            "definition": "अंग्रेजी वर्णमाला (Alphabet) में कुल 26 अक्षरस होते हैं। इन्हें दो भागों में बांटा गया है: Vowels (स्वर) 5 (A, E, I, O, U) और Consonants (व्यंजन) 21। इसके अलावा 'Y' को Semi-vowel कहा जाता है क्योंकि इसका उच्चारण कभी स्वर तो कभी व्यंजन जैसा होता है।",
            "structures": [
                {"name": "Singular Subject", "formula": "He (वह - लड़का), She (वह - लड़की), It (यह/वह), Single Name (राम)", "hindi": "एकवचन कर्ता"},
                {"name": "Plural Subject", "formula": "I (मैं), We (हम), You (तुम/आप), They (वे), 2 Names (राम और रहीम)", "hindi": "बहुवचन कर्ता"}
            ],
            "golden_rules": [
                "Trick: EDUCATION शब्द में पांचों Vowels (A, E, I, O, U) आते हैं!",
                "Semi-vowel 'Y': University में 'य' (Consonant sound) है, जबकि Cry में 'ई' (Vowel sound) है।",
                "अंग्रेजी का कोई भी वाक्य बिना Subject और Verb के अधूरा होता है।"
            ],
            "vocabulary": [
                {"word": "Subject", "meaning": "कर्ता (काम करने वाला)", "example": "He is the subject of this sentence."},
                {"word": "Vowel", "meaning": "स्वर (A, E, I, O, U)", "example": "There are five vowels."},
                {"word": "Consonant", "meaning": "व्यंजन", "example": "There are 21 consonants in English."}
            ],
            "manual_examples": [
                {"hindi": "वह स्कूल जाता है।", "english": "He goes to school."},
                {"hindi": "हम अंग्रेजी सीखते हैं।", "english": "We learn English."},
                {"hindi": "तुम एक अच्छे विद्यार्थी हो।", "english": "You are a good student."},
                {"hindi": "यह एक सुंदर बगीचा है।", "english": "It is a beautiful garden."},
                {"hindi": "वे क्रिकेट खेलते हैं।", "english": "They play cricket."},
                {"hindi": "राम और रहीम दोस्त हैं।", "english": "Ram and Rahim are friends."}
            ]
        },
        {
            "id": 3,
            "title": "Greetings",
            "hindi_title": "अभिवादन के वाक्य (Greetings & Manners)",
            "category": "Foundation",
            "level": "beginner",
            "emoji": "🤝",
            "page_start": 8,
            "page_end": 8,
            "definition": "बोलचाल में अभिवादन (Greetings) सबसे महत्वपूर्ण हिस्सा है। समय और रिश्ते के अनुसार सही अभिवादन शब्द का प्रयोग किया जाता है।",
            "structures": [
                {"name": "Morning (सुबह से 12 बजे तक)", "formula": "Good morning [Father/Mother/Sir/Madam]!", "hindi": "सुबह का अभिवादन"},
                {"name": "Afternoon (12 से शाम 5 बजे तक)", "formula": "Good afternoon [Sir/Brother/Madam]!", "hindi": "दोपहर का अभिवादन"},
                {"name": "Evening (शाम 5 बजे के बाद)", "formula": "Good evening [Everyone/Sir/Father]!", "hindi": "शाम को मिलने पर"},
                {"name": "Night Departure (रात को विदा लेते समय)", "formula": "Good night / Sweet dreams!", "hindi": "रात को विदा लेते समय"},
                {"name": "Informal (दोस्तों के साथ)", "formula": "Hi / Hello / Goodbye guys / Farewell dear!", "hindi": "अनौपचारिक अभिवादन"}
            ],
            "golden_rules": [
                "रात 8 या 9 बजे भी जब किसी से पहली बार मिलते हैं, तो 'Good evening' ही बोलते हैं, 'Good night' केवल विदा लेते समय बोला जाता है!",
                "दिन में विदा लेते समय 'Good day to you, Sir' या 'Have a nice day' बोलें।"
            ],
            "vocabulary": [
                {"word": "Greeting", "meaning": "अभिवादन", "example": "Always start with a warm greeting."},
                {"word": "Farewell", "meaning": "विदाई", "example": "Farewell dear friend!"},
                {"word": "Pleasure", "meaning": "खुशी", "example": "Pleasure meeting you."}
            ],
            "manual_examples": [
                {"hindi": "नमस्ते माताजी!", "english": "Good morning Mother!"},
                {"hindi": "नमस्ते सर!", "english": "Good afternoon Sir!"},
                {"hindi": "नमस्ते पिताजी!", "english": "Good evening father!"},
                {"hindi": "शुभ रात्रि!", "english": "Good night!"},
                {"hindi": "अच्छा चलते हैं दोस्तों!", "english": "Goodbye guys!"},
                {"hindi": "अलविदा प्रिय मित्र!", "english": "Farewell dear friend!"},
                {"hindi": "आपका दिन शुभ हो सर!", "english": "Good day to you Sir!"},
                {"hindi": "हैलो राहुल, कैसे हो?", "english": "Hello Rahul, how are you?"}
            ]
        },
        {
            "id": 4,
            "title": "Be Verb (is, am, are, was, were, will be)",
            "hindi_title": "स्थिति या होना (Be Verb)",
            "category": "Core Grammar",
            "level": "beginner",
            "emoji": "✨",
            "page_start": 9,
            "page_end": 14,
            "definition": "जब हमें किसी व्यक्ति, वस्तु या स्थान की स्थिति (State of being), गुण या पहचान बतानी हो (कोई काम नहीं हो रहा हो), तब Be Verb का प्रयोग किया जाता है।",
            "structures": [
                {"name": "Present Affirmative", "formula": "Sub + is / am / are + Obj", "hindi": "वर्तमान: है / हूँ / हो"},
                {"name": "Present Negative", "formula": "Sub + is / am / are + not + Obj", "hindi": "वर्तमान: नहीं है"},
                {"name": "Present Interrogative", "formula": "Is / Am / Are + Sub + Obj?", "hindi": "वर्तमान: क्या... है?"},
                {"name": "Past Affirmative", "formula": "Sub + was / were + Obj", "hindi": "भूतकाल: था / थी / थे"},
                {"name": "Past Negative", "formula": "Sub + was / were + not + Obj", "hindi": "भूतकाल: नहीं था"},
                {"name": "Future Affirmative", "formula": "Sub + will be + Obj", "hindi": "भविष्य: होगा / बनेगा / रहेगी"}
            ],
            "golden_rules": [
                "He / She / It / Singular Name के साथ Present में 'is' और Past में 'was' लगता है।",
                "I के साथ Present में 'am' और Past में 'was' लगता है।",
                "You / We / They / Plural के साथ Present में 'are' और Past में 'were' लगता है।",
                "भविष्य में सभी Subjects के साथ 'will be' का प्रयोग किया जाता है।"
            ],
            "vocabulary": [
                {"word": "Clever", "meaning": "चालाक / होशियार", "example": "He is very clever."},
                {"word": "Naughty", "meaning": "शरारती", "example": "The child is naughty."},
                {"word": "Religious", "meaning": "धार्मिक", "example": "She is very religious."},
                {"word": "Absent", "meaning": "अनुपस्थित", "example": "She was absent yesterday."}
            ]
        },
        {
            "id": 5,
            "title": "Imperative Sentences",
            "hindi_title": "आदेश, सलाह और निवेदन (Imperative)",
            "category": "Daily Expressions",
            "level": "beginner",
            "emoji": "📢",
            "page_start": 15,
            "page_end": 18,
            "definition": "जब हम किसी को कोई आदेश (Order), सलाह (Advice), निर्देश (Instruction) या निवेदन (Request) करते हैं, तब Imperative Sentences का प्रयोग करते हैं। इनमें Subject (You) छिपा रहता है और वाक्य सीधे Verb से शुरू होता है।",
            "structures": [
                {"name": "Order / Advice", "formula": "V1 + Object", "hindi": "ऐसा करो"},
                {"name": "Prohibition (मना करना)", "formula": "Don't + V1 + Object", "hindi": "ऐसा मत करो"},
                {"name": "Polite Request", "formula": "Please + V1 + Object / Kindly + V1 + Object", "hindi": "कृपया ऐसा करें"},
                {"name": "Always / Never", "formula": "Always + V1 + Object / Never + V1 + Object", "hindi": "हमेशा / कभी नहीं"}
            ],
            "golden_rules": [
                "Imperative वाक्यों में क्रिया का पहला रूप (V1) ही प्रयोग होता है।",
                "मना करने के लिए हमेशा 'Don't' से वाक्य शुरू करें, जैसे: 'Don't shout!'",
                "विनम्रता के लिए वाक्य के शुरू या अंत में 'Please' जोड़ें।"
            ],
            "vocabulary": [
                {"word": "Peep", "meaning": "झांकना", "example": "Don't peep into his house."},
                {"word": "Drag", "meaning": "घसीटना", "example": "Don't drag the table."},
                {"word": "Make fun", "meaning": "मजाक उड़ाना / मस्ती करना", "example": "Don't make fun of others."},
                {"word": "Quarrel", "meaning": "झगड़ा करना", "example": "Don't quarrel with friends."}
            ]
        },
        {
            "id": 6,
            "title": "Has / Have / Had / Will have",
            "hindi_title": "पास होना (Possession & Relation)",
            "category": "Core Grammar",
            "level": "beginner",
            "emoji": "🔑",
            "page_start": 19,
            "page_end": 24,
            "definition": "जब हमें अंग्रेजी में यह बताना हो कि हमारे पास क्या वस्तु है, रिश्ता है, बीमारी है या विशेषता है, तब Has/Have (वर्तमान), Had (भूतकाल) और Will have (भविष्य) का प्रयोग करते हैं।",
            "structures": [
                {"name": "Present Affirmative", "formula": "Sub + has / have + Object", "hindi": "पास है"},
                {"name": "Present Negative", "formula": "Sub + does not have / do not have + Object", "hindi": "पास नहीं है"},
                {"name": "Present Interrogative", "formula": "Do / Does + Sub + have + Object?", "hindi": "क्या पास है?"},
                {"name": "Past Affirmative", "formula": "Sub + had + Object", "hindi": "पास था"},
                {"name": "Past Negative", "formula": "Sub + did not have + Object", "hindi": "पास नहीं था"},
                {"name": "Future Affirmative", "formula": "Sub + will have + Object", "hindi": "पास होगा"}
            ],
            "golden_rules": [
                "Present में He, She, It, Singular के साथ 'has' और I, We, You, They के साथ 'have' लगता है।",
                "Negative वाक्यों में Does not / Do not / Did not लगने के बाद हमेशा 'have' आता है, 'has' या 'had' नहीं आता!",
                "बीमारी या सिरदर्द बताने के लिए: 'I have a headache / cold'."
            ],
            "vocabulary": [
                {"word": "Possession", "meaning": "अधिकार / पास होना", "example": "He has a new car."},
                {"word": "Facilities", "meaning": "सुविधाएं", "example": "We have all modern facilities."},
                {"word": "Satisfaction", "meaning": "संतुष्टि", "example": "Do you have satisfaction?"},
                {"word": "Nuclear weapons", "meaning": "परमाणु हथियार", "example": "India has nuclear weapons."}
            ]
        },
        {
            "id": 7,
            "title": "Demonstrative Pronoun (This, That, These, Those)",
            "hindi_title": "संकेतवाचक सर्वनाम (यह, वह, ये, वो)",
            "category": "Foundation",
            "level": "beginner",
            "emoji": "👉",
            "page_start": 25,
            "page_end": 29,
            "definition": "वे सर्वनाम जो किसी व्यक्ति, वस्तु या स्थान की ओर इशारा (Demonstrate) करने के लिए प्रयुक्त होते हैं। पास और दूर, तथा एकवचन और बहुवचन के अनुसार इनका चुनाव किया जाता है।",
            "structures": [
                {"name": "This (यह - पास, एकवचन)", "formula": "This is / was [Object]", "hindi": "यह एक किताब है - This is a book"},
                {"name": "That (वह - दूर, एकवचन)", "formula": "That is / was [Object]", "hindi": "वह एक कार है - That is a car"},
                {"name": "These (ये - पास, बहुवचन)", "formula": "These are / were [Objects]", "hindi": "ये मेरी किताबें हैं - These are my books"},
                {"name": "Those (वे - दूर, बहुवचन)", "formula": "Those are / were [Objects]", "hindi": "वे लड़के हैं - Those are boys"}
            ],
            "golden_rules": [
                "Near (पास) + Singular (एकवचन) = THIS",
                "Far (दूर) + Singular (एकवचन) = THAT",
                "Near (पास) + Plural (बहुवचन) = THESE",
                "Far (दूर) + Plural (बहुवचन) = THOSE"
            ],
            "vocabulary": [
                {"word": "Bangles", "meaning": "चूड़ियाँ", "example": "These are my bangles."},
                {"word": "Restaurant", "meaning": "भोजनालय / रेस्टोरेंट", "example": "That is a very good restaurant."},
                {"word": "Evidence", "meaning": "सबूत", "example": "This is important evidence."}
            ]
        },
        {
            "id": 8,
            "title": "Use of Want / Wants",
            "hindi_title": "वस्तु चाहिए / चाहना (Want & Wants)",
            "category": "Daily Expressions",
            "level": "beginner",
            "emoji": "🎯",
            "page_start": 30,
            "page_end": 33,
            "definition": "जब हमें वर्तमान में यह बताना हो कि हमें कोई वस्तु (Object) चाहिए या हम कुछ चाहते हैं, तब Want / Wants का प्रयोग किया जाता है।",
            "structures": [
                {"name": "Affirmative", "formula": "Sub + want / wants + Object", "hindi": "मुझे किताब चाहिए - I want a book"},
                {"name": "Negative", "formula": "Sub + do not / does not + want + Object", "hindi": "उसे पैसे नहीं चाहिए - He does not want money"},
                {"name": "Interrogative", "formula": "Do / Does + Sub + want + Object?", "hindi": "क्या आपको पानी चाहिए? - Do you want water?"},
                {"name": "WH Question", "formula": "WH + do / does + Sub + want + Object?", "hindi": "आपको क्या चाहिए? - What do you want?"}
            ],
            "golden_rules": [
                "He, She, It, Singular Name के साथ 'wants' आता है।",
                "I, We, You, They, Plural के साथ 'want' आता है।",
                "Does not या Do not आने पर हमेशा मूल रूप 'want' ही रहता है।"
            ],
            "vocabulary": [
                {"word": "Dictionary", "meaning": "शब्दकोश", "example": "I want an English dictionary."},
                {"word": "Comfort", "meaning": "आराम / सुविधा", "example": "We want comfort."},
                {"word": "Opportunity", "meaning": "अवसर / मौका", "example": "They want an opportunity."}
            ]
        },
        {
            "id": 9,
            "title": "Use of Wanted",
            "hindi_title": "वस्तु चाहिए थी / चाहता था (Wanted)",
            "category": "Daily Expressions",
            "level": "beginner",
            "emoji": "⏪",
            "page_start": 34,
            "page_end": 37,
            "definition": "जब हमें भूतकाल (Past) में यह बताना हो कि हमें कोई वस्तु चाहिए थी या हम किसी वस्तु की इच्छा रखते थे, तब Wanted का प्रयोग किया जाता है।",
            "structures": [
                {"name": "Affirmative", "formula": "Sub + wanted + Object", "hindi": "मुझे नमक चाहिए था - I wanted some salt"},
                {"name": "Negative", "formula": "Sub + did not want + Object", "hindi": "मुझे मदद नहीं चाहिए थी - I did not want help"},
                {"name": "Interrogative", "formula": "Did + Sub + want + Object?", "hindi": "क्या उसे कार चाहिए थी? - Did he want a car?"},
                {"name": "WH Question", "formula": "Why / What + did + Sub + want + Object?", "hindi": "तुम्हें क्या चाहिए था? - What did you want?"}
            ],
            "golden_rules": [
                "भूतकाल के साधारण वाक्य में सभी Subjects (Singular और Plural) के साथ 'wanted' ही लगता है।",
                "Negative और Interrogative में 'did' आ जाने के बाद 'wanted' का 'want' हो जाता है (Did + want)।"
            ],
            "vocabulary": [
                {"word": "Salt", "meaning": "नमक", "example": "I wanted some salt."},
                {"word": "Knowledge", "meaning": "ज्ञान", "example": "He wanted knowledge of English."},
                {"word": "Clue / Evidence", "meaning": "सुराग / सबूत", "example": "The police wanted evidence."}
            ]
        },
        {
            "id": 10,
            "title": "Use of Going to",
            "hindi_title": "काम करने वाले हैं (Going to - Future Plans)",
            "category": "Daily Expressions",
            "level": "intermediate",
            "emoji": "🚶",
            "page_start": 38,
            "page_end": 43,
            "definition": "'Going to' का मतलब होता है कि कोई काम निकट भविष्य में करने वाले हैं या कोई घटना बस घटने वाली है। इसका प्रयोग Present, Past और Future तीनों में किया जाता है।",
            "structures": [
                {"name": "Present (करने वाले हैं)", "formula": "Sub + is / am / are + going to + V1 + Object", "hindi": "मैं चाय पीने वाला हूँ - I am going to take tea"},
                {"name": "Past (करने वाले थे)", "formula": "Sub + was / were + going to + V1 + Object", "hindi": "वह मुझे कॉल करने वाला था - He was going to call me"},
                {"name": "Future (करने वाले होंगे)", "formula": "Sub + will be + going to + V1 + Object", "hindi": "वह तैरने वाला होगा - He will be going to swim"},
                {"name": "WH Question", "formula": "WH + is/am/are/was/were + Sub + going to + V1 + Obj?", "hindi": "तुम कब जाने वाले हो? - When are you going to leave?"}
            ],
            "golden_rules": [
                "'Going to' के बाद हमेशा क्रिया का पहला रूप (V1) आता है।",
                "बोलचाल में 'going to' को अक्सर 'gonna' भी बोला जाता है (जैसे: I'm gonna call you)।"
            ],
            "vocabulary": [
                {"word": "Stroll / Walk", "meaning": "टहलना", "example": "Grandpa is going to stroll."},
                {"word": "Plant trees", "meaning": "पेड़ लगाना", "example": "We are going to plant trees."},
                {"word": "Assist / Help", "meaning": "सहायता करना", "example": "Are they going to assist us?"}
            ]
        },
        {
            "id": 11,
            "title": "Use of There (There is / There are / There was / There will be)",
            "hindi_title": "किसी स्थान पर किसी चीज का होना (Use of There)",
            "category": "Core Grammar",
            "level": "intermediate",
            "emoji": "📍",
            "page_start": 44,
            "page_end": 49,
            "definition": "जब हमें यह बताना हो कि किसी स्थान, कमरे, शहर, थैले या वस्तु के अंदर कोई वस्तु या व्यक्ति मौजूद है (या नहीं है), तब 'There' को Dummy Subject के रूप में प्रयोग किया जाता है।",
            "structures": [
                {"name": "Present (एकवचन)", "formula": "There is + Singular Object + in / at [Place]", "hindi": "कमरे में एक पंखा है - There is a fan in the room"},
                {"name": "Present (बहुवचन)", "formula": "There are + Plural Objects + in / at [Place]", "hindi": "पेड़ पर पक्षी हैं - There are birds on the tree"},
                {"name": "Past (था/थी/थे)", "formula": "There was / were + Object + [Place]", "hindi": "गाँव में अस्पताल नहीं था - There was no hospital in the village"},
                {"name": "Future (होगा/होगी)", "formula": "There will be + Object + [Place]", "hindi": "मीटिंग में भीड़ होगी - There will be crowd in the meeting"}
            ],
            "golden_rules": [
                "There के बाद 'is' या 'are' आगे आने वाले Object के अनुसार तय होता है। अगर Object एकवचन है तो 'is', बहुवचन है तो 'are'।",
                "Negative में अक्सर 'no' या 'not any' का प्रयोग होता है (There is no water / There are no cars)।"
            ],
            "vocabulary": [
                {"word": "Queue / Line", "meaning": "कतार / पंक्ति", "example": "There was a long queue at the bank."},
                {"word": "Cockroach", "meaning": "तिलचट्टा / कॉकरोच", "example": "There was a cockroach in his pocket."},
                {"word": "Crowd", "meaning": "भीड़", "example": "There will be a huge crowd."}
            ]
        },
        {
            "id": 12,
            "title": "Use of Let (Let me, Let him, Let them)",
            "hindi_title": "करने दो / होने दो (Use of Let)",
            "category": "Daily Expressions",
            "level": "intermediate",
            "emoji": "🤲",
            "page_start": 50,
            "page_end": 53,
            "definition": "ऐसे वाक्य जिनमें किसी को कोई कार्य करने देने की अनुमति या छूट मांगी या दी जाती है (जैसे: मुझे जाने दो, उसे बोलने दो), उनमें 'Let' का प्रयोग किया जाता है।",
            "structures": [
                {"name": "Affirmative", "formula": "Let + Objective Pronoun (me/him/her/them/us) + V1 + Object", "hindi": "मुझे सफाई पेश करने दो - Let me explain myself"},
                {"name": "Negative", "formula": "Don't let + Objective Pronoun + V1 + Object", "hindi": "उन्हें बहस मत करने दो - Don't let them argue"},
                {"name": "Polite", "formula": "Please let + Objective Pronoun + V1 + Object", "hindi": "कृपया मुझे जाने दें - Please let me go"}
            ],
            "golden_rules": [
                "Let के तुरंत बाद हमेशा Objective Pronoun (me, him, her, them, us) आता है, Subjective (I, he, they) नहीं!",
                "Let के बाद क्रिया का केवल पहला रूप (V1) आता है, 'to' नहीं लगाया जाता (Let him go, NOT Let him to go)।"
            ],
            "vocabulary": [
                {"word": "Explain myself", "meaning": "अपनी सफाई पेश करना", "example": "Let me explain myself."},
                {"word": "Truth come out", "meaning": "सच सामने आना", "example": "Let the truth come out."},
                {"word": "Argue", "meaning": "बहस करना", "example": "Don't let them argue."}
            ]
        },
        {
            "id": 13,
            "title": "Use of Let's",
            "hindi_title": "चलो / आओ मिलकर करें (Use of Let's)",
            "category": "Daily Expressions",
            "level": "intermediate",
            "emoji": "🤝",
            "page_start": 54,
            "page_end": 56,
            "definition": "'Let's' (Let us का संकुचित रूप) का प्रयोग तब किया जाता है जब हम किसी प्रस्ताव (Proposal) या सुझाव (Suggestion) के साथ किसी काम को मिलकर करने की बात करते हैं (चलो ऐसा करते हैं)।",
            "structures": [
                {"name": "Affirmative", "formula": "Let's + V1 + Object", "hindi": "चलो एक तस्वीर लेते हैं - Let's take a picture"},
                {"name": "Negative", "formula": "Let's not + V1 + Object", "hindi": "चलो झगड़ा नहीं करते हैं - Let's not quarrel"},
                {"name": "Question Tag", "formula": "Let's + V1 + Object, shall we?", "hindi": "चलो चलते हैं, चलें क्या? - Let's go, shall we?"}
            ],
            "golden_rules": [
                "Negative बनाते समय 'Don't let's' के बजाय 'Let's not' बोलना अधिक मानक और स्वाभाविक है।",
                "हमेशा क्रिया का पहला रूप (V1) ही प्रयोग करें।"
            ],
            "vocabulary": [
                {"word": "Surprise", "meaning": "आश्चर्यचकित करना / सरप्राइज देना", "example": "Let's surprise Neha."},
                {"word": "Attack", "meaning": "हमला करना", "example": "Let's not attack."},
                {"word": "Celebrate", "meaning": "जश्न मनाना", "example": "Let's celebrate together."}
            ]
        },
        {
            "id": 14,
            "title": "Use of Would like to",
            "hindi_title": "पसंद करूँगा / चाहूँगा (Polite Desires)",
            "category": "Polite Expressions",
            "level": "intermediate",
            "emoji": "💭",
            "page_start": 57,
            "page_end": 60,
            "definition": "जब कोई व्यक्ति अपनी इच्छा (Wish), पसंद या निवेदन को बेहद विनम्र और शिष्ट (Polite) तरीके से व्यक्त करना चाहता है, तब 'Would like to' का प्रयोग किया जाता है।",
            "structures": [
                {"name": "Affirmative", "formula": "Sub + would like to + V1 + Object", "hindi": "मैं एक गाना सुनना चाहूँगा - I would like to listen to a song"},
                {"name": "Negative", "formula": "Sub + would not like to + V1 + Object", "hindi": "तुम अपना भेद नहीं खोलना चाहोगे - You would not like to reveal your secret"},
                {"name": "Interrogative", "formula": "Would + Sub + like to + V1 + Object?", "hindi": "क्या आप बाहर चलना चाहोगे? - Would you like to go out?"},
                {"name": "WH Question", "formula": "What / Where + would + Sub + like to + V1 + Obj?", "hindi": "आप क्या लेना पसंद करेंगे? - What would you like to take?"}
            ],
            "golden_rules": [
                "रेस्टोरेंट, ऑफिस और फॉर्मल बातचीत में 'I want' के स्थान पर 'I would like to' बोलना बहुत सभ्य माना जाता है।",
                "संक्षेप में 'I would' को \"I'd\" लिखा और बोला जाता है (I'd like to order tea)."
            ],
            "vocabulary": [
                {"word": "Reveal secret", "meaning": "भेद / राज़ खोलना", "example": "He would not like to reveal the secret."},
                {"word": "Go out", "meaning": "बाहर जाना", "example": "Would you like to go out?"},
                {"word": "Participate", "meaning": "भाग लेना", "example": "I'd like to participate."}
            ]
        },
        {
            "id": 15,
            "title": "Use of Need to",
            "hindi_title": "करने की आवश्यकता / ज़रूरत है (Need to)",
            "category": "Daily Expressions",
            "level": "intermediate",
            "emoji": "⚡",
            "page_start": 61,
            "page_end": 62,
            "definition": "जब वर्तमान में किसी कार्य को करने की अनिवार्यता, ज़रूरत या आवश्यकता व्यक्त करनी हो, तब 'Need to' का प्रयोग किया जाता है।",
            "structures": [
                {"name": "Affirmative (I/We/You/They)", "formula": "Sub + need to + V1 + Object", "hindi": "मुझे अंग्रेजी सीखने की ज़रूरत है - I need to learn English"},
                {"name": "Affirmative (He/She/It)", "formula": "Sub + needs to + V1 + Object", "hindi": "उसे आराम करने की ज़रूरत है - He needs to take rest"},
                {"name": "Negative", "formula": "Sub + do not / does not + need to + V1 + Object", "hindi": "तुम्हें चिंता करने की ज़रूरत नहीं है - You don't need to worry"},
                {"name": "Interrogative", "formula": "Do / Does + Sub + need to + V1 + Object?", "hindi": "क्या मुझे जाने की आवश्यकता है? - Do I need to go?"}
            ],
            "golden_rules": [
                "Singular subject (He/She/It) के साथ 'needs to' और Plural (I/We/You/They) के साथ 'need to' आता है।",
                "Do not / Does not आने पर हमेशा 'need to' ही रहेगा।"
            ],
            "vocabulary": [
                {"word": "Necessity", "meaning": "आवश्यकता", "example": "It is a daily necessity."},
                {"word": "Improve", "meaning": "सुधारना", "example": "You need to improve your handwriting."},
                {"word": "Concentrate", "meaning": "ध्यान लगाना", "example": "He needs to concentrate on studies."}
            ]
        },
        {
            "id": 16,
            "title": "Use of Needed to",
            "hindi_title": "करने की ज़रूरत थी (Needed to - Past Necessity)",
            "category": "Daily Expressions",
            "level": "intermediate",
            "emoji": "📋",
            "page_start": 63,
            "page_end": 66,
            "definition": "जब भूतकाल (Past) में किसी कार्य को करने की ज़रूरत या आवश्यकता थी, तब 'Needed to' का प्रयोग किया जाता है।",
            "structures": [
                {"name": "Affirmative", "formula": "Sub + needed to + V1 + Object", "hindi": "उसे घर की सफाई करने की ज़रूरत थी - She needed to clean the house"},
                {"name": "Negative", "formula": "Sub + did not need to + V1 + Object", "hindi": "तुम्हें बच्चों को डांटने की ज़रूरत नहीं थी - You didn't need to scold children"},
                {"name": "Interrogative", "formula": "Did + Sub + need to + V1 + Object?", "hindi": "क्या उसे बर्तन मांजने की ज़रूरत थी? - Did she need to wash the dishes?"}
            ],
            "golden_rules": [
                "साधारण भूतकाल में सभी Subjects के साथ 'needed to' लगता है।",
                "Negative में 'did not' के बाद 'needed to' बदलकर 'need to' हो जाता है (Did not need to + V1)।"
            ],
            "vocabulary": [
                {"word": "Scold", "meaning": "डांटना", "example": "You didn't need to scold children."},
                {"word": "Wash dishes", "meaning": "बर्तन मांजना", "example": "Did she need to wash dishes?"},
                {"word": "Worry", "meaning": "चिंता करना", "example": "You didn't need to worry about me."}
            ]
        },
        {
            "id": 17,
            "title": "Use of Fond of",
            "hindi_title": "शौकीन होना (Fond of - Passions & Hobbies)",
            "category": "Daily Expressions",
            "level": "intermediate",
            "emoji": "❤️",
            "page_start": 67,
            "page_end": 72,
            "definition": "जब हमें यह बताना हो कि हमें किसी चीज़ का शौक है, या हम किसी काम को करने के शौकीन हैं (जैसे: क्रिकेट खेलने का शौक, संगीत सुनने का शौक), तब 'Fond of' का प्रयोग करते हैं।",
            "structures": [
                {"name": "Present", "formula": "Sub + is / am / are + fond of + V1-ing / Noun", "hindi": "उसे संगीत सुनने का शौक है - She is fond of listening to music"},
                {"name": "Past", "formula": "Sub + was / were + fond of + V1-ing / Noun", "hindi": "वह क्रिकेट खेलने का शौकीन था - He was fond of playing cricket"},
                {"name": "Future", "formula": "Sub + will be + fond of + V1-ing / Noun", "hindi": "वह किताबें पढ़ने का शौकीन होगा - He will be fond of reading books"},
                {"name": "Negative", "formula": "Sub + is/am/are/was/were + not + fond of + V1-ing", "hindi": "मुझे मीठा खाने का शौक नहीं है - I am not fond of eating sweets"}
            ],
            "golden_rules": [
                "'Fond of' में Preposition 'of' होने के कारण इसके बाद आने वाली क्रिया में हमेशा 'ing' (Gerund / V4) लगता है (fond of playing, fond of dancing)।",
                "यदि कोई संज्ञा (Noun) हो तो सीधे Noun आ जाता है: 'fond of tea / chocolates'."
            ],
            "vocabulary": [
                {"word": "Biography", "meaning": "आत्मकथा / जीवनी", "example": "I am fond of reading biographies."},
                {"word": "Festivals", "meaning": "त्योहार", "example": "She is fond of celebrating festivals."},
                {"word": "Passionate", "meaning": "उत्साही / शौकीन", "example": "He is fond of photography."}
            ]
        },
        {
            "id": 18,
            "title": "Use of About to",
            "hindi_title": "बस होने ही वाला है (About to - Imminent Action)",
            "category": "Daily Expressions",
            "level": "intermediate",
            "emoji": "⏰",
            "page_start": 73,
            "page_end": 77,
            "definition": "जब हमें यह बताना हो कि कोई काम बस तुरंत होने ही वाला है या कोई व्यक्ति कोई काम बस करने ही वाला था/होगा, तब 'About to' का प्रयोग किया जाता है।",
            "structures": [
                {"name": "Present (होने ही वाला है)", "formula": "Sub + is / am / are + about to + V1 + Object", "hindi": "ट्रेन छूटने ही वाली है - The train is about to leave"},
                {"name": "Past (होने ही वाला था)", "formula": "Sub + was / were + about to + V1 + Object", "hindi": "मैं तुम्हें आमंत्रित करने वाला था - I was about to invite you"},
                {"name": "Future (होने ही वाला होगा)", "formula": "Sub + will be + about to + V1 + Object", "hindi": "वह खाना पकाने वाली होगी - She will be about to cook food"},
                {"name": "Interrogative", "formula": "Are / Is / Was + Sub + about to + V1 + Object?", "hindi": "क्या आप सोने जाने वाले हैं? - Are you about to go to bed?"}
            ],
            "golden_rules": [
                "'About to' के बाद हमेशा Verb का मूल रूप (V1) आता है।",
                "इसका उपयोग तब होता है जब कार्य अगले कुछ ही सेकंड या मिनट में शुरू होने वाला हो।"
            ],
            "vocabulary": [
                {"word": "Invite", "meaning": "आमंत्रित करना", "example": "I was about to invite you."},
                {"word": "Shake / Rustle", "meaning": "हिलना", "example": "Leaves are about to shake in the wind."},
                {"word": "Go to bed", "meaning": "सोने जाना", "example": "Are you about to go to bed?"}
            ]
        },
        {
            "id": 19,
            "title": "Use of Make / Get (Causative Verbs)",
            "hindi_title": "काम करवाना (Causative Verbs - Make & Get)",
            "category": "Advanced Grammar",
            "level": "advanced",
            "emoji": "🔨",
            "page_start": 78,
            "page_end": 83,
            "definition": "जब Subject खुद काम न करके किसी अन्य व्यक्ति से काम करवाता है (प्रेरणार्थक क्रिया), तब Make या Get का प्रयोग Causative Verbs के रूप में किया जाता है।",
            "structures": [
                {"name": "Make (दबाव या निर्देश देकर करवाना - Present)", "formula": "Sub + make / makes + Objective Pronoun + V1 + Object", "hindi": "वह मुझसे कपड़े धुलवाती है - She makes me wash clothes"},
                {"name": "Make (Past)", "formula": "Sub + made + Objective Pronoun + V1 + Object", "hindi": "उसने मुझसे पत्र लिखवाया - He made me write a letter"},
                {"name": "Get (राजी करके या भुगतान करके करवाना)", "formula": "Sub + get / gets + Object + V3 (Past Participle)", "hindi": "मैंने बाल कटवाए - I got my hair cut"},
                {"name": "Future Causative", "formula": "Sub + will make + Obj Pro + V1", "hindi": "वह मुझसे अंग्रेजी बुलवाएगा - He will make me speak English"}
            ],
            "golden_rules": [
                "Make के बाद Person (Objective pronoun) आता है और क्रिया का पहला रूप (V1) लगता है (He made me laugh)।",
                "Get के बाद Thing (Object) आने पर क्रिया का तीसरा रूप (V3) लगता है (I got my car washed)।"
            ],
            "vocabulary": [
                {"word": "Wash clothes", "meaning": "कपड़े धोना", "example": "She makes me wash clothes."},
                {"word": "Paint the house", "meaning": "घर पेंट करवाना", "example": "Did you get the house painted?"},
                {"word": "Speak English", "meaning": "अंग्रेजी बुलवाना", "example": "He makes me speak English."}
            ]
        },
        {
            "id": 20,
            "title": "All Modals (Can, Should, May, Must, Used to, Could, etc.)",
            "hindi_title": "सभी मोडाल्स (Can, Should, May, Must, Could...)",
            "category": "Modals Master",
            "level": "intermediate",
            "emoji": "🎛️",
            "page_start": 84,
            "page_end": 123,
            "definition": "Modals सहायक क्रियाएं (Auxiliary Verbs) होती हैं जो क्षमता, अनुमति, सलाह, संभावना, अनिवार्यता या भूतकाल की आदतों को व्यक्त करती हैं।",
            "structures": [
                {"name": "Can (सकता है - क्षमता/योग्यता)", "formula": "Sub + can + V1 + Object", "hindi": "मैं यह सवाल हल कर सकता हूँ - I can solve this question"},
                {"name": "Should (चाहिए - सलाह/सुझाव)", "formula": "Sub + should + V1 + Object", "hindi": "तुम्हें फल खाने चाहिए - You should eat fruits"},
                {"name": "May (सकता है - औपचारिक अनुमति/संभावना)", "formula": "May + I + V1 + Object?", "hindi": "क्या मैं अंदर आ सकता हूँ? - May I come in?"},
                {"name": "Must (चाहिए ही - अनिवार्यता/कर्तव्य)", "formula": "Sub + must + V1 + Object", "hindi": "हमें ट्रैफिक नियमों का पालन करना ही चाहिए - We must obey traffic rules"},
                {"name": "Used to (करता था - पुरानी आदत)", "formula": "Sub + used to + V1 + Object", "hindi": "मैं शिक्षकों की नकल किया करता था - I used to mimic teachers"},
                {"name": "Could (कर सका / कर पाया)", "formula": "Sub + could + V1 + Object", "hindi": "वह समय पर पहुँच सका - He could reach on time"},
                {"name": "Should have (करना चाहिए था)", "formula": "Sub + should have + V3 + Object", "hindi": "हमें झगड़ा नहीं करना चाहिए था - We should not have fought"},
                {"name": "Could have (कर सकता था)", "formula": "Sub + could have + V3 + Object", "hindi": "मैं जल्दी आ सकता था - I could have come early"},
                {"name": "Must have (अवश्य किया होगा)", "formula": "Sub + must have + V3 + Object", "hindi": "उसने दवा ली होगी - He must have taken medicine"}
            ],
            "golden_rules": [
                "साधारण Modals (Can, Could, Should, May, Might, Must, Used to) के बाद हमेशा क्रिया का पहला रूप (V1) आता है।",
                "Past Modals (Should have, Could have, Must have, Would have) के बाद हमेशा क्रिया का तीसरा रूप (V3) आता है!"
            ],
            "vocabulary": [
                {"word": "Traffic rules", "meaning": "यातायात के नियम", "example": "We must obey traffic rules."},
                {"word": "Solve", "meaning": "हल करना", "example": "I can solve this question."},
                {"word": "Mimic", "meaning": "नकल उतारना", "example": "He used to mimic teachers."},
                {"word": "Fight / Quarrel", "meaning": "झगड़ा करना", "example": "We should not have fought."}
            ]
        },
        {
            "id": 21,
            "title": "All Tenses (Present, Past, Future - Complete Guide)",
            "hindi_title": "सभी काल (Present, Past, Future - 12 Tenses)",
            "category": "Tenses Master",
            "level": "intermediate",
            "emoji": "⏳",
            "page_start": 124,
            "page_end": 150,
            "definition": "Tense क्रिया का वह रूप है जिसके द्वारा हमें समय (Time of action) और कार्य की स्थिति (State of action) का पता चलता है। कुल 3 मुख्य काल होते हैं और प्रत्येक के 4 प्रकार होते हैं, कुल 12 Tenses होते हैं।",
            "structures": [
                {"name": "Present Simple (ता है, ती है, ते हैं)", "formula": "Sub + V1/V5 (s/es) + Object", "hindi": "वह चाय पीता है - He takes tea"},
                {"name": "Present Continuous (रहा है, रही है)", "formula": "Sub + is/am/are + V1-ing + Object", "hindi": "वह क्रिकेट खेल रहा है - He is playing cricket"},
                {"name": "Present Perfect (चुका है, लिया है)", "formula": "Sub + has/have + V3 + Object", "hindi": "वह काम कर चुकी है - She has worked"},
                {"name": "Present Perfect Continuous (से रहा है)", "formula": "Sub + has/have been + V1-ing + since/for + time", "hindi": "वह 7 बजे से पढ़ रहा है - He has been reading since 7 o'clock"},
                {"name": "Past Simple (आ, ई, ए, ता था)", "formula": "Sub + V2 + Object", "hindi": "उसने चाय बनाई - She prepared tea"},
                {"name": "Past Continuous (रहा था, रहे थे)", "formula": "Sub + was/were + V1-ing + Object", "hindi": "वह मेरा इंतज़ार कर रहा था - He was waiting for me"},
                {"name": "Past Perfect (चुका था, दिया था)", "formula": "Sub + had + V3 + Object", "hindi": "ट्रेन जा चुकी थी - The train had left"},
                {"name": "Future Simple (गा, गी, गे)", "formula": "Sub + will + V1 + Object", "hindi": "वह पार्टी में नाचेगा - He will dance at the party"},
                {"name": "Future Continuous (रहा होगा)", "formula": "Sub + will be + V1-ing + Object", "hindi": "मैं क्रिकेट खेल रहा हूँगा - I will be playing cricket"},
                {"name": "Future Perfect (चुका होगा)", "formula": "Sub + will have + V3 + Object", "hindi": "वे क्रिकेट खेल चुके होंगे - They will have played cricket"}
            ],
            "golden_rules": [
                "Present Simple में He, She, It, Singular के साथ क्रिया में s/es लगता है (takes, plays, goes)।",
                "Past Simple के सकारात्मक वाक्य में क्रिया का दूसरा रूप (V2) आता है (prepared, went, saw)। Negative में Did not + V1 आता है।",
                "निश्चित समय (Exact time: 7 o'clock, Monday, 2020) के लिए 'since', और अवधि (Duration: 2 hours, 5 days) के लिए 'for' का प्रयोग होता है।"
            ],
            "vocabulary": [
                {"word": "Routine", "meaning": "दैनिक दिनचर्या", "example": "He follows a strict routine."},
                {"word": "Prepare", "meaning": "तैयार करना / बनाना", "example": "She prepared tea for guests."},
                {"word": "Steal", "meaning": "चुराना", "example": "He has been stealing money."}
            ]
        }
    ]

    for ch in chapters_meta:
        p_start = ch["page_start"]
        p_end = ch["page_end"]
        extracted_pairs = []

        # Start with manual clean examples if available
        if "manual_examples" in ch:
            extracted_pairs.extend(ch["manual_examples"])

        for p_idx in range(p_start, min(p_end + 1, len(pages))):
            page_content = pages[p_idx]
            for line in page_content.split('\n'):
                line = line.strip()
                if not line or line.startswith('Join Online') or line.startswith('VI ISS') or line.startswith('Download'):
                    continue

                if '|' in line:
                    parts = [p.strip() for p in line.split('|') if p.strip()]
                    if len(parts) >= 2:
                        h_c = clean_text(parts[0])
                        e_c = clean_english(parts[1])
                        if is_clean_hindi_sentence(h_c) and is_clean_english_sentence(e_c):
                            extracted_pairs.append({"hindi": h_c, "english": e_c})
                elif re.search(r'[\u0900-\u097F].*[a-zA-Z]', line):
                    m = re.split(r'\s*\|\s*|\s*\(?[SNIW\.H0-9]+\)?\s*', line)
                    if len(m) >= 2:
                        h_c = clean_text(m[0])
                        e_c = clean_english(m[1])
                        if is_clean_hindi_sentence(h_c) and is_clean_english_sentence(e_c):
                            extracted_pairs.append({"hindi": h_c, "english": e_c})

        seen = set()
        clean_examples = []
        for pair in extracted_pairs:
            key = pair["hindi"] + pair["english"]
            if key not in seen:
                seen.add(key)
                en = pair["english"]
                if not en.endswith(('.', '?', '!')):
                    en += '?' if '?' in pair["hindi"] else '.'
                pair["english"] = en
                clean_examples.append(pair)

        ch["examples"] = clean_examples[:12]

        builder_drills = []
        for ex in ch["examples"][:6]:
            builder = make_sentence_builder(ex["hindi"], ex["english"])
            builder_drills.append(builder)
        ch["sentence_builder_drills"] = builder_drills

        worksheet_quiz = []
        for i, ex in enumerate(ch["examples"][:6]):
            correct = ex["english"]
            distractors = []
            words = correct.split()
            if len(words) > 2:
                d1 = " ".join(reversed(words[:2])) + " " + " ".join(words[2:])
                distractors.append(d1)
            distractors.append(correct.replace("is", "was").replace("can", "should").replace("want", "wanted"))
            distractors.append(correct.replace("don't", "not").replace("to", "for"))
            
            filtered_opts = [d for d in distractors if d != correct]
            opts = [correct] + filtered_opts[:3]
            random.seed(i + ch["id"])
            random.shuffle(opts)
            
            worksheet_quiz.append({
                "id": i + 1,
                "question": f"Translate into English: '{ex['hindi']}'",
                "hindi_sentence": ex["hindi"],
                "options": opts,
                "correct_answer": correct,
                "explanation": f"Mass Spoken Rule: सही अनुवाद '{correct}' है।"
            })
        ch["worksheet_quiz"] = worksheet_quiz

        curriculum["chapters"].append(ch)

    out_path = r'd:\EduSarthi\edusarthi_backend\edusarthi_backend\data\mass_spoken_curriculum.json'
    with open(out_path, 'w', encoding='utf-8') as out_f:
        json.dump(curriculum, out_f, ensure_ascii=False, indent=2)

    print(f"Successfully generated {out_path} with {len(curriculum['chapters'])} chapters!")

if __name__ == '__main__':
    main()
