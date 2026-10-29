"""
Mass Spoken English - 50 Chapter Full Curriculum Builder
Builds all 50 chapters including Foundation (1-21), Advanced Grammar (22-29),
Vocabulary Master sets (30-48), Real-Life Conversation Sheets (49), and Review Worksheets (50).
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
    
    if s.startswith("hut "): s = "S" + s
    elif s.startswith("et's "): s = "L" + s
    elif s.startswith("e would "): s = "W" + s
    elif s.startswith("he is fond "): s = "S" + s
    elif s.startswith("don't "): s = "I " + s
    elif s.startswith("did not "): s = "I " + s
    elif s.startswith("am going "): s = "I " + s
    elif s.startswith("gets "): s = "He " + s
    elif s.startswith("make you "): s = "I " + s

    s = re.sub(r'[\,\s0-9]+$', '', s)
    s = re.sub(r'\s+', ' ', s)
    return s.strip()

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

def make_quiz(examples, ch_id):
    quiz = []
    for i, ex in enumerate(examples[:8]):
        correct = ex["english"]
        words = correct.split()
        distractors = []
        if len(words) > 2:
            d1 = " ".join(reversed(words[:2])) + " " + " ".join(words[2:])
            distractors.append(d1)
        distractors.append(correct.replace("is", "was").replace("can", "should").replace("have to", "had to").replace("want", "wanted"))
        distractors.append(correct.replace("don't", "not").replace("to", "for").replace("will", "would"))
        
        filtered = [d for d in distractors if d != correct]
        opts = [correct] + filtered[:3]
        random.seed(i + ch_id)
        random.shuffle(opts)
        
        quiz.append({
            "id": i + 1,
            "question": f"Translate into English: '{ex['hindi']}'",
            "hindi_sentence": ex["hindi"],
            "options": opts,
            "correct_answer": correct,
            "explanation": f"Mass Spoken Rule: सही अनुवाद '{correct}' है।"
        })
    return quiz

def build_drills(examples):
    drills = []
    for ex in examples[:8]:
        drills.append(make_sentence_builder(ex["hindi"], ex["english"]))
    return drills

# Load existing 21 chapters from mass_spoken_curriculum.json
def get_existing_21():
    path = r'd:\EduSarthi\edusarthi_backend\edusarthi_backend\data\mass_spoken_curriculum.json'
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data["chapters"][:21]

# Chapters 22 to 50 definitions
chapters_22_to_50 = [
    {
        "id": 22,
        "title": "Use of Has to / Have to / Had to",
        "hindi_title": "मजबूरी या कर्तव्य (करना पड़ता है / करना पड़ा)",
        "category": "Daily Expressions",
        "level": "intermediate",
        "emoji": "💪",
        "definition": "जब वर्तमान, भूतकाल या भविष्य में किसी कार्य को करने की मजबूरी (Compulsion), अनिवार्यता या कर्तव्य बताना हो, तब Has to/Have to (वर्तमान), Had to (भूतकाल) और Will have to (भविष्य) का प्रयोग करते हैं।",
        "structures": [
            {"name": "Present (करना पड़ता है / करना है)", "formula": "Sub + has to / have to + V1 + Object", "hindi": "मुझे रोज़ 6 बजे उठना पड़ता है - I have to wake up at 6 AM daily"},
            {"name": "Past (करना पड़ा / पड़ता था)", "formula": "Sub + had to + V1 + Object", "hindi": "उसे जुर्माना भरना पड़ा - He had to pay the fine"},
            {"name": "Future (करना पड़ेगा)", "formula": "Sub + will have to + V1 + Object", "hindi": "तुम्हें सच बताना पड़ेगा - You will have to tell the truth"},
            {"name": "Negative Present", "formula": "Sub + does not have to / do not have to + V1 + Object", "hindi": "तुम्हें जाने की ज़रूरत नहीं है - You don't have to go"}
        ],
        "golden_rules": [
            "He/She/It/Singular के साथ 'has to' और I/We/You/They के साथ 'have to' लगता है।",
            "Negative में Does not / Do not / Did not के बाद हमेशा 'have to' ही आता है!"
        ],
        "vocabulary": [
            {"word": "Obligation", "meaning": "कर्तव्य / मजबूरी", "example": "It is my daily obligation."},
            {"word": "Pay fine", "meaning": "जुर्माना भरना", "example": "He had to pay the fine."},
            {"word": "Hard work", "meaning": "कठिन परिश्रम", "example": "Students have to do hard work."}
        ],
        "examples": [
            {"hindi": "मुझे रोज़ सुबह 6 बजे उठना पड़ता है।", "english": "I have to wake up at 6 AM every day."},
            {"hindi": "उसे दवाई लेनी पड़ी।", "english": "She had to take medicine."},
            {"hindi": "तुम्हें सच बताना पड़ेगा।", "english": "You will have to tell the truth."},
            {"hindi": "हमें वहाँ नहीं जाना पड़ा।", "english": "We did not have to go there."},
            {"hindi": "क्या तुम्हें जुर्माना भरना पड़ा?", "english": "Did you have to pay the fine?"},
            {"hindi": "छात्रों को कठिन परिश्रम करना पड़ता है।", "english": "Students have to work hard."},
            {"hindi": "उसे अपना कमरा साफ करना पड़ता है।", "english": "He has to clean his room."},
            {"hindi": "मुझे तुरंत निकलना है।", "english": "I have to leave immediately."},
            {"hindi": "क्या आपको रोज़ खाना पकाना पड़ता है?", "english": "Do you have to cook food daily?"},
            {"hindi": "कल मुझे बैंक जाना पड़ेगा।", "english": "I will have to go to the bank tomorrow."}
        ]
    },
    {
        "id": 23,
        "title": "Use of Able to",
        "hindi_title": "सक्षम होना (कर पाना / समर्थ होना)",
        "category": "Daily Expressions",
        "level": "intermediate",
        "emoji": "🏋️",
        "definition": "जब हमें किसी कार्य को करने की योग्यता या सक्षमता (Ability / Capacity) बतानी हो (कर पाता है, कर पाया, कर पाएगा), तब 'Able to' का प्रयोग तीनों Tenses में किया जाता है।",
        "structures": [
            {"name": "Present", "formula": "Sub + is / am / are + able to + V1 + Object", "hindi": "मैं अंग्रेजी बोल पाता हूँ - I am able to speak English"},
            {"name": "Past", "formula": "Sub + was / were + able to + V1 + Object", "hindi": "वह समय पर पहुँच पाई - She was able to reach on time"},
            {"name": "Future", "formula": "Sub + will be able to + V1 + Object", "hindi": "तुम मैच जीत पाओगे - You will be able to win the match"},
            {"name": "Negative", "formula": "Sub + is/am/are/was/were + not + able to + V1 + Object", "hindi": "मैं आ नहीं पाया - I was not able to come"}
        ],
        "golden_rules": [
            "Can/Could की जगह 'Able to' अधिक औपचारिक और सभी Tenses (खासकर Future: will be able to) में काम आता है।",
            "'Able to' के बाद हमेशा V1 का प्रयोग होता है।"
        ],
        "vocabulary": [
            {"word": "Capable", "meaning": "सक्षम / समर्थ", "example": "He is capable of doing this."},
            {"word": "Patient", "meaning": "मरीज / धैर्यवान", "example": "Doctor was able to save the patient."},
            {"word": "Manage", "meaning": "संभालना / प्रबंध करना", "example": "I will be able to manage everything."}
        ],
        "examples": [
            {"hindi": "मैं अब अंग्रेजी बोल पाता हूँ।", "english": "I am able to speak English now."},
            {"hindi": "वह समय पर नहीं पहुँच पाई।", "english": "She was not able to reach on time."},
            {"hindi": "क्या तुम मेरी मदद कर पाओगे?", "english": "Will you be able to help me?"},
            {"hindi": "वह कार चला पाता है।", "english": "He is able to drive a car."},
            {"hindi": "डॉक्टर मरीज को नहीं बचा पाए।", "english": "The doctor was not able to save the patient."},
            {"hindi": "हम सवाल हल कर पाए।", "english": "We were able to solve the question."},
            {"hindi": "क्या आप यह भारी बॉक्स उठा पाएंगे?", "english": "Will you be able to lift this heavy box?"},
            {"hindi": "वह डर के मारे बोल नहीं पाया।", "english": "He was not able to speak due to fear."}
        ]
    },
    {
        "id": 24,
        "title": "Use of Want to",
        "hindi_title": "कुछ करना चाहना (Want to + Verb)",
        "category": "Daily Expressions",
        "level": "intermediate",
        "emoji": "🎯",
        "definition": "जब कोई व्यक्ति किसी कार्य को करने की इच्छा या इरादा रखता है (जैसे: पढ़ना चाहता हूँ, जाना चाहता हूँ), तब 'Want to / Wants to' के साथ क्रिया का पहला रूप (V1) लगाया जाता है।",
        "structures": [
            {"name": "Affirmative (I/We/You/They)", "formula": "Sub + want to + V1 + Object", "hindi": "मैं डॉक्टर बनना चाहता हूँ - I want to become a doctor"},
            {"name": "Affirmative (He/She/It)", "formula": "Sub + wants to + V1 + Object", "hindi": "वह तुमसे मिलना चाहती है - She wants to meet you"},
            {"name": "Negative", "formula": "Sub + do not / does not + want to + V1 + Object", "hindi": "हम समय बर्बाद नहीं करना चाहते - We do not want to waste time"},
            {"name": "Interrogative", "formula": "Do / Does + Sub + want to + V1 + Object?", "hindi": "क्या तुम कुछ कहना चाहते हो? - Do you want to say something?"}
        ],
        "golden_rules": [
            "केवल वस्तु चाहिए तो 'want + Noun' (I want tea), लेकिन कोई काम करना हो तो 'want to + V1' (I want to drink tea)।",
            "बोलचाल में 'want to' को 'wanna' भी कहा जाता है।"
        ],
        "vocabulary": [
            {"word": "Intention", "meaning": "इरादा", "example": "I want to improve my skills."},
            {"word": "Participate", "meaning": "भाग लेना", "example": "She wants to participate in the race."},
            {"word": "Achieve", "meaning": "हासिल करना", "example": "I want to achieve my goals."}
        ],
        "examples": [
            {"hindi": "मैं डॉक्टर बनना चाहता हूँ।", "english": "I want to become a doctor."},
            {"hindi": "वह तुमसे बात करना चाहती है।", "english": "She wants to talk to you."},
            {"hindi": "क्या तुम कुछ कहना चाहते हो?", "english": "Do you want to say something?"},
            {"hindi": "हम समय बर्बाद नहीं करना चाहते।", "english": "We do not want to waste time."},
            {"hindi": "वे नई कार खरीदना चाहते हैं।", "english": "They want to buy a new car."},
            {"hindi": "मैं आज बाहर नहीं जाना चाहता।", "english": "I do not want to go outside today."},
            {"hindi": "क्या वह अंग्रेजी सीखना चाहती है?", "english": "Does she want to learn English?"},
            {"hindi": "तुम जीवन में क्या बनना चाहते हो?", "english": "What do you want to become in life?"}
        ]
    },
    {
        "id": 25,
        "title": "Use of Wanted to",
        "hindi_title": "कुछ करना चाहता था (Past Desires)",
        "category": "Daily Expressions",
        "level": "intermediate",
        "emoji": "⏪",
        "definition": "जब भूतकाल (Past) में किसी कार्य को करने की इच्छा थी लेकिन शायद वह काम नहीं हो सका (जैसे: बताना चाहता था, मिलना चाहता था), तब 'Wanted to + V1' का प्रयोग किया जाता है।",
        "structures": [
            {"name": "Affirmative", "formula": "Sub + wanted to + V1 + Object", "hindi": "मैं तुम्हें सच बताना चाहता था - I wanted to tell you the truth"},
            {"name": "Negative", "formula": "Sub + did not want to + V1 + Object", "hindi": "वह नौकरी छोड़ना नहीं चाहता था - He did not want to leave the job"},
            {"name": "Interrogative", "formula": "Did + Sub + want to + V1 + Object?", "hindi": "क्या तुम मुझसे मिलना चाहते थे? - Did you want to meet me?"}
        ],
        "golden_rules": [
            "Affirmative में सभी Subjects के साथ 'wanted to' लगता है।",
            "Negative में 'did not' आने के बाद 'wanted to' बदलकर 'want to' हो जाता है।"
        ],
        "vocabulary": [
            {"word": "Apologize", "meaning": "माफी मांगना", "example": "I wanted to apologize to him."},
            {"word": "Attend", "meaning": "उपस्थित होना", "example": "She wanted to attend the wedding."},
            {"word": "Explain", "meaning": "समझाना", "example": "He wanted to explain the reason."}
        ],
        "examples": [
            {"hindi": "मैं तुम्हें सच बताना चाहता था।", "english": "I wanted to tell you the truth."},
            {"hindi": "वह मीटिंग में भाग लेना चाहती थी।", "english": "She wanted to attend the meeting."},
            {"hindi": "क्या तुम मुझसे मिलना चाहते थे?", "english": "Did you want to meet me?"},
            {"hindi": "हम किसी को चोट नहीं पहुँचाना चाहते थे।", "english": "We did not want to hurt anyone."},
            {"hindi": "वह नौकरी छोड़ना चाहता था।", "english": "He wanted to quit the job."},
            {"hindi": "मैं तुम्हें परेशान नहीं करना चाहता था।", "english": "I did not want to disturb you."},
            {"hindi": "क्या वह तुमसे कुछ पूछना चाहता था?", "english": "Did he want to ask you something?"},
            {"hindi": "हम उस दिन पिकनिक जाना चाहते थे।", "english": "We wanted to go on a picnic that day."}
        ]
    },
    {
        "id": 26,
        "title": "Use of All Prepositions",
        "hindi_title": "सभी संबंधबोधक अव्यय (In, On, At, Under, By, With...)",
        "category": "Core Grammar",
        "level": "intermediate",
        "emoji": "📐",
        "definition": "Prepositions वे शब्द हैं जो किसी Noun या Pronoun का संबंध वाक्य के अन्य शब्दों से जोड़ते हैं (जैसे: कमरे में, मेज पर, 2 बजे, कार द्वारा, दोस्तों के साथ)।",
        "structures": [
            {"name": "In (अंदर/बड़ा शहर/महीना)", "formula": "in the room / in Delhi / in July", "hindi": "अंदर या बड़े स्थान में"},
            {"name": "On (सतह पर छूते हुए/दिन/तारीख)", "formula": "on the table / on Monday / on 15th August", "hindi": "सतह के ऊपर या दिन"},
            {"name": "At (निश्चित समय/छोटा स्थान)", "formula": "at 5 o'clock / at home / at the station", "hindi": "निश्चित समय या स्थान"},
            {"name": "Between vs Among", "formula": "between (दो के बीच) / among (दो से अधिक के बीच)", "hindi": "के बीच में"}
        ],
        "golden_rules": [
            "घड़ी के समय के साथ हमेशा 'At' लगाएं (at 4 PM)।",
            "दिन और तारीख के साथ हमेशा 'On' लगाएं (on Sunday)।",
            "महीने और साल के साथ हमेशा 'In' लगाएं (in 2026)।"
        ],
        "vocabulary": [
            {"word": "Distribute", "meaning": "बांटना", "example": "Distribute sweets among children."},
            {"word": "Behind", "meaning": "पीछे", "example": "The cat hid behind the door."},
            {"word": "In front of", "meaning": "के सामने", "example": "He is standing in front of the gate."}
        ],
        "examples": [
            {"hindi": "मेज पर एक किताब रखी है।", "english": "There is a book on the table."},
            {"hindi": "वह कमरे के अंदर बैठा है।", "english": "He is sitting inside the room."},
            {"hindi": "हम बस से स्कूल जाते हैं।", "english": "We go to school by bus."},
            {"hindi": "मिठाई को दोनों बच्चों के बीच बांट दो।", "english": "Distribute the sweet between the two children."},
            {"hindi": "वह 2 घंटे से मेरा इंतजार कर रहा है।", "english": "He has been waiting for me for two hours."},
            {"hindi": "मैं सोमवार को तुमसे मिलूँगा।", "english": "I will meet you on Monday."},
            {"hindi": "ट्रेन शाम 5 बजे पहुँचेगी।", "english": "The train will arrive at 5 PM."},
            {"hindi": "उसने चाकू से सेब काटा।", "english": "He cut the apple with a knife."}
        ]
    },
    {
        "id": 27,
        "title": "Use of All W.H. Words",
        "hindi_title": "सभी प्रश्नवाचक शब्द (What, When, Where, Why, How...)",
        "category": "Core Grammar",
        "level": "intermediate",
        "emoji": "❓",
        "definition": "W.H. Words का प्रयोग प्रश्न पूछने के लिए किया जाता है। इनके बिना अंग्रेजी में कोई भी बातचीत या पूछताछ संभव नहीं है।",
        "structures": [
            {"name": "W.H. Question Structure", "formula": "WH Word + Helping Verb + Subject + Main Verb + Object?", "hindi": "प्रश्न पूछने का मुख्य सूत्र"},
            {"name": "What (क्या)", "formula": "What do you want?", "hindi": "वस्तु या जानकारी"},
            {"name": "Where (कहाँ)", "formula": "Where do you live?", "hindi": "स्थान के लिए"},
            {"name": "When (कब)", "formula": "When will you come?", "hindi": "समय के लिए"},
            {"name": "Why (क्यों)", "formula": "Why are you late?", "hindi": "कारण के लिए"},
            {"name": "How (कैसे)", "formula": "How do you do this?", "hindi": "तरीके के लिए"}
        ],
        "golden_rules": [
            "W.H. Word के तुरंत बाद Helping Verb आती है (जैसे: Where ARE you going?), Helping Verb भूलना सबसे बड़ी गलती है!",
            "How many (गिने जाने योग्य) vs How much (न गिने जाने योग्य मात्रा)।"
        ],
        "vocabulary": [
            {"word": "Reason", "meaning": "कारण", "example": "Tell me the reason why you are late."},
            {"word": "Whose", "meaning": "किसका / किसकी", "example": "Whose bag is this on the floor?"},
            {"word": "Which", "meaning": "कौन सा / कौन सी", "example": "Which book do you want to read?"}
        ],
        "examples": [
            {"hindi": "तुम कहाँ जा रहे हो?", "english": "Where are you going?"},
            {"hindi": "तुमने यह मोबाइल कब खरीदा?", "english": "When did you buy this mobile?"},
            {"hindi": "यह चाबी किसकी है?", "english": "Whose key is this?"},
            {"hindi": "तुम्हें कौन सा रंग पसंद है?", "english": "Which colour do you like?"},
            {"hindi": "इस कमरे में कितने लोग हैं?", "english": "How many people are in this room?"},
            {"hindi": "तुम्हारी बोतल में कितना पानी है?", "english": "How much water is in your bottle?"},
            {"hindi": "वह मुझसे क्यों नाराज है?", "english": "Why is he angry with me?"},
            {"hindi": "तुम्हारा सबसे अच्छा दोस्त कौन है?", "english": "Who is your best friend?"}
        ]
    },
    {
        "id": 28,
        "title": "Use of All Passive Voice",
        "hindi_title": "कर्मवाच्य (Passive Voice - काम किया जाता है / किया गया)",
        "category": "Advanced Grammar",
        "level": "advanced",
        "emoji": "🔄",
        "definition": "जब वाक्य में काम करने वाले (Subject) से ज़्यादा उस कार्य (Object) को महत्व दिया जाता है, तब Passive Voice का प्रयोग करते हैं (जैसे: अंग्रेजी बोली जाती है, चोर पकड़ा गया)।",
        "structures": [
            {"name": "Present Simple Passive", "formula": "Obj + is / am / are + V3 + (by Sub)", "hindi": "अंग्रेजी पूरी दुनिया में बोली जाती है - English is spoken all over the world"},
            {"name": "Past Simple Passive", "formula": "Obj + was / were + V3 + (by Sub)", "hindi": "चोर पुलिस द्वारा पकड़ा गया - The thief was caught by the police"},
            {"name": "Future Simple Passive", "formula": "Obj + will be + V3", "hindi": "यह सड़क बनाई जाएगी - This road will be built"},
            {"name": "Continuous Passive", "formula": "Obj + is/am/are/was/were + being + V3", "hindi": "खाना पकाया जा रहा है - Food is being cooked"}
        ],
        "golden_rules": [
            "Passive Voice के हर वाक्य में क्रिया का हमेशा तीसरा रूप (V3) ही प्रयोग होता है!",
            "अखबारों, समाचारों और वैज्ञानिक रिपोर्ट्स में 80% Passive Voice का ही उपयोग होता है।"
        ],
        "vocabulary": [
            {"word": "Construct", "meaning": "निर्माण करना", "example": "The bridge was constructed in two years."},
            {"word": "Arrest", "meaning": "गिरफ्तार करना", "example": "The criminal was arrested yesterday."},
            {"word": "Announce", "meaning": "घोषणा करना", "example": "Results will be announced tomorrow."}
        ],
        "examples": [
            {"hindi": "अंग्रेजी पूरी दुनिया में बोली जाती है।", "english": "English is spoken all over the world."},
            {"hindi": "चोर पुलिस द्वारा पकड़ा गया।", "english": "The thief was caught by the police."},
            {"hindi": "यह सड़क अगले महीने बनाई जाएगी।", "english": "This road will be built next month."},
            {"hindi": "खाना पकाया जा रहा है।", "english": "The food is being cooked."},
            {"hindi": "मैच भारत द्वारा जीता गया।", "english": "The match was won by India."},
            {"hindi": "सभी कमरों को साफ किया जा चुका है।", "english": "All rooms have been cleaned."},
            {"hindi": "पेड़ तूफान में काट दिए गए।", "english": "Trees were cut down in the storm."},
            {"hindi": "उसे अस्पताल ले जाया गया।", "english": "He was taken to the hospital."}
        ]
    },
    {
        "id": 29,
        "title": "Verb List & 3 Forms of Verbs",
        "hindi_title": "क्रियाओं के तीन रूप (V1, V2, V3 Forms Master)",
        "category": "Core Grammar",
        "level": "intermediate",
        "emoji": "📝",
        "definition": "अंग्रेजी बोलने में सबसे बड़ा रोल क्रिया के रूपों का होता है: V1 (Present), V2 (Past), V3 (Past Participle)। इन्हें सही समय पर सही रूप में लगाना जरूरी है।",
        "structures": [
            {"name": "V1 (Base/Present)", "formula": "Go, Eat, See, Write, Speak", "hindi": "वर्तमान काल में"},
            {"name": "V2 (Simple Past)", "formula": "Went, Ate, Saw, Wrote, Spoke", "hindi": "साधारण भूतकाल में"},
            {"name": "V3 (Perfect Tenses & Passive)", "formula": "Gone, Eaten, Seen, Written, Spoken", "hindi": "चुका है/था व पैसिव में"}
        ],
        "golden_rules": [
            "Past Indefinite के सकारात्मक वाक्य में हमेशा V2 आता है (I went, He saw)।",
            "Has / Have / Had / Will have और Passive Voice में हमेशा V3 आता है।"
        ],
        "vocabulary": [
            {"word": "Arise - Arose - Arisen", "meaning": "उठना / उत्पन्न होना", "example": "A new problem arose."},
            {"word": "Break - Broke - Broken", "meaning": "तोड़ना", "example": "He broke the glass."},
            {"word": "Choose - Chose - Chosen", "meaning": "चुनना", "example": "She has chosen the best dress."}
        ],
        "examples": [
            {"hindi": "उसने मुझे एक पत्र लिखा।", "english": "He wrote a letter to me."},
            {"hindi": "मैंने अपनी चाबी खो दी है।", "english": "I have lost my key."},
            {"hindi": "उसने अदालत में सच बोला।", "english": "She spoke the truth in court."},
            {"hindi": "पक्षी आसमान में ऊँचा उड़ गए।", "english": "Birds flew high in the sky."},
            {"hindi": "उसने अपना वादा पूरा निभाया।", "english": "He kept his promise completely."},
            {"hindi": "हमने कल एक नया पाठ सीखा।", "english": "We learned a new lesson yesterday."},
            {"hindi": "उसने मुझे उपहार दिया।", "english": "She gave me a beautiful gift."},
            {"hindi": "ट्रेन समय से पहले आ गई।", "english": "The train came before time."}
        ]
    },
    {
        "id": 30,
        "title": "W.H. Words Practice & Question Making",
        "hindi_title": "उन्नत प्रश्न निर्माण अभ्यास (Advanced Question Drills)",
        "category": "Daily Expressions",
        "level": "intermediate",
        "emoji": "📚",
        "definition": "रोज़मर्रा की बातचीत में सवाल पूछने के तरीके (How long, How far, With whom, Since when) की विशेष प्रैक्टिस।",
        "structures": [
            {"name": "Duration (कितनी देर)", "formula": "How long will it take?", "hindi": "कितना समय लगेगा"},
            {"name": "Distance (कितनी दूर)", "formula": "How far is your house?", "hindi": "तुम्हारा घर कितनी दूर है"},
            {"name": "Association (किसके साथ)", "formula": "With whom are you going?", "hindi": "किसके साथ जा रहे हो"}
        ],
        "golden_rules": [
            "प्रश्न बनाते समय Subject से पहले Helping Verb लगाना कभी न भूलें।",
            "उत्तर में 'Because' तब आता है जब सवाल 'Why' से हो।"
        ],
        "vocabulary": [
            {"word": "Destination", "meaning": "गंतव्य / मंजिल", "example": "How far is the destination?"},
            {"word": "Companion", "meaning": "साथी", "example": "With whom did you travel?"},
            {"word": "Frequency", "meaning": "कितनी बार", "example": "How often do you exercise?"}
        ],
        "examples": [
            {"hindi": "तुम्हें यहाँ आने में कितना समय लगा?", "english": "How long did it take you to come here?"},
            {"hindi": "तुम्हारा ऑफिस यहाँ से कितनी दूर है?", "english": "How far is your office from here?"},
            {"hindi": "तुम किसके साथ बाजार जा रहे हो?", "english": "With whom are you going to the market?"},
            {"hindi": "तुम कब से इस कंपनी में काम कर रहे हो?", "english": "Since when have you been working here?"},
            {"hindi": "तुम हफ्ते में कितनी बार कसरत करते हो?", "english": "How often do you exercise in a week?"},
            {"hindi": "इस मोबाइल की कीमत क्या है?", "english": "What is the price of this mobile?"},
            {"hindi": "तुमने कल रात क्या खाया था?", "english": "What did you eat last night?"},
            {"hindi": "उसे कौन सा गाना सबसे ज्यादा पसंद है?", "english": "Which song does she like the most?"}
        ]
    },
    {
        "id": 31,
        "title": "Basic Spoken Words & Short Phrases",
        "hindi_title": "रोज़ बोले जाने वाले छोटे वाक्यांश (Daily Short Phrases)",
        "category": "Vocabulary Master",
        "level": "beginner",
        "emoji": "🗣️",
        "definition": "छोटे-छोटे 2-3 शब्दों के जादुई वाक्यांश जो आपकी बातचीत को तुरंत स्वाभाविक और धाराप्रवाह बनाते हैं (जैसे: कोई बात नहीं, चिंता मत करो, जैसी आपकी मर्जी)।",
        "structures": [
            {"name": "Courtesy Phrases", "formula": "No problem / Never mind / My pleasure / Excuse me", "hindi": "शिष्टाचार के शब्द"},
            {"name": "Encouraging Phrases", "formula": "Cheer up / Keep it up / Well done / Go ahead", "hindi": "हौसला बढ़ाने वाले शब्द"}
        ],
        "golden_rules": [
            "जब कोई 'Thank you' कहे तो 'Welcome' के बजाय 'My pleasure' या 'Glad to help' कहना ज्यादा प्रभावशाली है।",
            "किसी का ध्यान आकर्षित करने के लिए 'Excuse me' बोलें।"
        ],
        "vocabulary": [
            {"word": "Never mind", "meaning": "कोई बात नहीं / जाने दो", "example": "Never mind, it doesn't matter."},
            {"word": "As you wish", "meaning": "जैसी आपकी मर्जी", "example": "We can eat now, as you wish."},
            {"word": "Hurry up", "meaning": "जल्दी करो", "example": "Hurry up, we are getting late."}
        ],
        "examples": [
            {"hindi": "कोई बात नहीं, अगली बार ध्यान रखना।", "english": "No problem, take care next time."},
            {"hindi": "जैसी आपकी मर्जी।", "english": "As you wish."},
            {"hindi": "मुझ पर पूरा भरोसा रखो।", "english": "Trust me completely."},
            {"hindi": "चिंता मत करो, सब ठीक हो जाएगा।", "english": "Don't worry, everything will be fine."},
            {"hindi": "जल्दी करो, हमें देर हो रही है।", "english": "Hurry up, we are getting late."},
            {"hindi": "मेरी बात ध्यान से सुनो।", "english": "Listen to me carefully."},
            {"hindi": "मुझे एक मिनट का समय दो।", "english": "Give me a minute, please."},
            {"hindi": "क्या आपको मेरी बात समझ आई?", "english": "Did you understand my point?"}
        ]
    },
    {
        "id": 32,
        "title": "Daily Use Vocabulary & Common Expressions",
        "hindi_title": "दैनिक दिनचर्या शब्दावली (Everyday Life Words)",
        "category": "Vocabulary Master",
        "level": "intermediate",
        "emoji": "📅",
        "definition": "सुबह जागने से लेकर रात को सोने तक इस्तेमाल होने वाले महत्वपूर्ण दैनिक जीवन के शब्द और वाक्य।",
        "structures": [
            {"name": "Morning Routine", "formula": "I wake up -> brush teeth -> take bath -> have breakfast", "hindi": "सुबह की दिनचर्या"},
            {"name": "House & Chores", "formula": "Clean the room -> wash dishes -> do laundry", "hindi": "घर के कामकाज"}
        ],
        "golden_rules": [
            "नाश्ता करने के लिए 'take breakfast' या 'have breakfast' बोलें, 'eat breakfast' से ज्यादा प्राकृतिक है।",
            "पंखा चालू/बंद करने के लिए 'open/close' नहीं, 'turn on / turn off' बोलें।"
        ],
        "vocabulary": [
            {"word": "Chores", "meaning": "घर के छोटे-मोटे काम", "example": "I do daily household chores."},
            {"word": "Hungry", "meaning": "भूखा", "example": "I am feeling very hungry."},
            {"word": "Exhausted", "meaning": "बहुत थका हुआ", "example": "I am exhausted after a long day."}
        ],
        "examples": [
            {"hindi": "मैं रोज़ सुबह 7 बजे उठता हूँ।", "english": "I wake up at 7 AM daily."},
            {"hindi": "मुझे बहुत तेज भूख लग रही है।", "english": "I am feeling very hungry."},
            {"hindi": "कृपया कमरे का पंखा चालू कर दो।", "english": "Please turn on the room fan."},
            {"hindi": "अपनी जुबान पर लगाम रखो।", "english": "Mind your language, please."},
            {"hindi": "दिनभर के काम के बाद मैं थक गया हूँ।", "english": "I am exhausted after working all day."},
            {"hindi": "क्या तुमने अपना नाश्ता कर लिया?", "english": "Have you had your breakfast?"},
            {"hindi": "मैं जूते के फीते बांध रहा हूँ।", "english": "I am tying my shoelaces."},
            {"hindi": "अलमारी का दरवाजा खुला मत छोड़ो।", "english": "Don't leave the wardrobe door open."}
        ]
    },
    {
        "id": 33,
        "title": "Industry, Business & Office Vocabulary",
        "hindi_title": "कार्यालय और व्यापारिक शब्दावली (Corporate English)",
        "category": "Vocabulary Master",
        "level": "advanced",
        "emoji": "🏭",
        "definition": "ऑफिस, कॉर्पोरेट, बिजनेस मीटिंग्स और क्लाइंट डीलिंग में बोले जाने वाले पेशेवर शब्द और वाक्य।",
        "structures": [
            {"name": "Meeting & Scheduling", "formula": "The meeting is scheduled at [Time]", "hindi": "मीटिंग तय करना"},
            {"name": "Reporting & Deadlines", "formula": "Submit the report before the deadline", "hindi": "डेडलाइन पर कार्य"}
        ],
        "golden_rules": [
            "ऑफिस में 'I cannot do' के बजाय 'I will explore other alternatives' बोलना पेशेवर माना जाता है।",
            "ईमेल में 'Dear Sir' के साथ 'Please find attached...' का उपयोग करें।"
        ],
        "vocabulary": [
            {"word": "Deadline", "meaning": "अंतिम समय सीमा", "example": "We must meet the project deadline."},
            {"word": "Resignation", "meaning": "इस्तीफा", "example": "He submitted his resignation today."},
            {"word": "Promotion", "meaning": "पदोन्नति / तरक्की", "example": "She received a well-deserved promotion."}
        ],
        "examples": [
            {"hindi": "मुझे आज एक महत्वपूर्ण ईमेल भेजनी है।", "english": "I have to send an important email today."},
            {"hindi": "बॉस ने नई परियोजना को मंजूरी दे दी।", "english": "The boss approved the new project."},
            {"hindi": "हमारी मीटिंग दोपहर 3 बजे निर्धारित है।", "english": "Our meeting is scheduled for 3 PM."},
            {"hindi": "उसे कंपनी में पदोन्नति मिली।", "english": "He got a promotion in the company."},
            {"hindi": "कृपया यह रिपोर्ट समय सीमा से पहले भेजें।", "english": "Please submit this report before the deadline."},
            {"hindi": "क्लाइंट हमारे काम से बहुत संतुष्ट है।", "english": "The client is very satisfied with our work."},
            {"hindi": "हम अगले हफ्ते नया उत्पाद लॉन्च करेंगे।", "english": "We will launch a new product next week."},
            {"hindi": "वार्षिक बजट कल प्रस्तुत किया जाएगा।", "english": "The annual budget will be presented tomorrow."}
        ]
    },
    {
        "id": 34,
        "title": "Body Parts & Diseases Vocabulary",
        "hindi_title": "शरीर के अंग, बीमारियां व दवाइयां (Health & Medical)",
        "category": "Vocabulary Master",
        "level": "intermediate",
        "emoji": "🏥",
        "definition": "डॉक्टर के पास जाने, बीमारी बताने और स्वास्थ्य संबंधी समस्याओं को अंग्रेजी में व्यक्त करने के लिए आवश्यक शब्दावली।",
        "structures": [
            {"name": "Symptom Statement", "formula": "I have a headache / stomach ache / sore throat", "hindi": "दर्द या लक्षण बताना"},
            {"name": "Duration", "formula": "I have had fever since yesterday", "hindi": "बीमारी का समय"}
        ],
        "golden_rules": [
            "दर्द बताने के लिए: सिरदर्द = headache, पेट दर्द = stomach ache, पीठ दर्द = backache, दांत दर्द = toothache।",
            "दवा खाने के लिए 'eat medicine' नहीं, 'take medicine' बोलें।"
        ],
        "vocabulary": [
            {"word": "Prescription", "meaning": "डॉक्टर का पर्चा / नुस्खा", "example": "Follow the doctor's prescription."},
            {"word": "Sprain", "meaning": "मोच आना", "example": "He has a sprain in his ankle."},
            {"word": "Symptoms", "meaning": "रोग के लक्षण", "example": "What are the common symptoms of cold?"}
        ],
        "examples": [
            {"hindi": "मेरे सिर में बहुत तेज दर्द है।", "english": "I have a severe headache."},
            {"hindi": "उसे दो दिन से तेज बुखार है।", "english": "She has a high fever for two days."},
            {"hindi": "डॉक्टर ने उसे आराम करने की सलाह दी।", "english": "The doctor advised him to take rest."},
            {"hindi": "मेरे पैर में मोच आ गई है।", "english": "I have a sprain in my leg."},
            {"hindi": "खाना खाने के बाद यह दवाई लेना।", "english": "Take this medicine after having food."},
            {"hindi": "क्या आपको कोई एलर्जी है?", "english": "Do you have any kind of allergy?"},
            {"hindi": "मेरी आँखें स्क्रीन देखने से दुख रही हैं।", "english": "My eyes are hurting from looking at the screen."},
            {"hindi": "रक्तचाप सामान्य सीमा में है।", "english": "The blood pressure is in the normal range."}
        ]
    },
    {
        "id": 35,
        "title": "Flowers & Fruits Vocabulary",
        "hindi_title": "फूल और फलों के अंग्रेजी नाम (Flora & Fruits)",
        "category": "Vocabulary Master",
        "level": "beginner",
        "emoji": "🌺",
        "definition": "दैनिक जीवन में उपयोग होने वाले विभिन्न फूलों, फलों और उनके गुणों से संबंधित उपयोगी शब्द।",
        "structures": [
            {"name": "Describing Fruits", "formula": "This fruit is sweet / sour / ripe / raw", "hindi": "फल का स्वाद व स्थिति"},
            {"name": "Flowers", "formula": "Rose smells sweet / Marigold blooms in winter", "hindi": "फूलों की विशेषताएं"}
        ],
        "golden_rules": [
            "पके हुए फल को 'Ripe fruit' और कच्चे फल को 'Raw / Unripe fruit' कहते हैं।",
            "खट्टा फल 'Sour' और मीठा फल 'Sweet' कहलाता है।"
        ],
        "vocabulary": [
            {"word": "Pomegranate", "meaning": "अनार", "example": "Pomegranate is rich in vitamins."},
            {"word": "Marigold", "meaning": "गेंदा का फूल", "example": "Marigold flowers look bright yellow."},
            {"word": "Fragrance", "meaning": "सुगंध / महक", "example": "Rose has a sweet fragrance."}
        ],
        "examples": [
            {"hindi": "अनार सेहत के लिए बहुत अच्छा होता है।", "english": "Pomegranate is very good for health."},
            {"hindi": "सूरजमुखी का फूल सूर्य की ओर मुड़ता है।", "english": "The sunflower turns towards the sun."},
            {"hindi": "बाजार में ताजे मीठे फल उपलब्ध हैं।", "english": "Fresh sweet fruits are available in the market."},
            {"hindi": "गुलाब के फूल से बहुत अच्छी महक आती है।", "english": "The rose flower has a wonderful fragrance."},
            {"hindi": "यह आम अभी कच्चा है।", "english": "This mango is still raw."},
            {"hindi": "पपीता पाचन के लिए फायदेमंद है।", "english": "Papaya is beneficial for digestion."}
        ]
    },
    {
        "id": 36,
        "title": "Birds, Animals & Astrology Vocabulary",
        "hindi_title": "पक्षी, पशु, प्रकृति और ज्योतिष शब्दावली",
        "category": "Vocabulary Master",
        "level": "intermediate",
        "emoji": "🐦",
        "definition": "जीव-जंतुओं, पक्षियों, खगोल विज्ञान (Astronomy) और ज्योतिष (Horoscope, Zodiac) से जुड़े उपयोगी शब्द।",
        "structures": [
            {"name": "Animal Actions", "formula": "The lion roars / The bird chirps / The eagle soars", "hindi": "पशु-पक्षियों की आवाजें"},
            {"name": "Astrological Terms", "formula": "Zodiac sign / Lunar eclipse / Solar eclipse", "hindi": "ज्योतिष व ग्रहण"}
        ],
        "golden_rules": [
            "चिड़ियों के चहचहाने को 'Chirp' और शेर की दहाड़ को 'Roar' कहते हैं।",
            "चंद्र ग्रहण = 'Lunar eclipse', सूर्य ग्रहण = 'Solar eclipse'।"
        ],
        "vocabulary": [
            {"word": "Peacock", "meaning": "मोर", "example": "Peacock is our national bird."},
            {"word": "Horoscope", "meaning": "जन्मकुंडली / राशिफल", "example": "He reads his horoscope every morning."},
            {"word": "Eclipse", "meaning": "ग्रहण", "example": "There is a solar eclipse today."}
        ],
        "examples": [
            {"hindi": "मोर भारत का राष्ट्रीय पक्षी है।", "english": "Peacock is the national bird of India."},
            {"hindi": "चील आसमान में बहुत ऊँचा उड़ती है।", "english": "The eagle flies very high in the sky."},
            {"hindi": "आज रात पूर्ण चंद्रग्रहण है।", "english": "There is a total lunar eclipse tonight."},
            {"hindi": "आपकी राशि क्या है?", "english": "What is your zodiac sign?"},
            {"hindi": "पक्षी सुबह-सुबह चहचहाते हैं।", "english": "Birds chirp early in the morning."},
            {"hindi": "चीता सबसे तेज दौड़ने वाला जानवर है।", "english": "Cheetah is the fastest running animal."}
        ]
    },
    {
        "id": 37,
        "title": "Maths & Quantitative Vocabulary",
        "hindi_title": "गणित, आंकड़े और नाप-तौल शब्दावली (Maths & Numbers)",
        "category": "Vocabulary Master",
        "level": "intermediate",
        "emoji": "🔢",
        "definition": "गणितीय संक्रियाओं (जोड़, घटाव, गुणा, भाग), प्रतिशत, औसत, और वित्तीय आंकड़ों को अंग्रेजी में बोलने के नियम।",
        "structures": [
            {"name": "Basic Operations", "formula": "Addition (+) / Subtraction (-) / Multiplication (x) / Division (/)", "hindi": "मूल गणितीय क्रियाएं"},
            {"name": "Fractions & Percentages", "formula": "Half (1/2) / Quarter (1/4) / Percentage (%)", "hindi": "हिस्सा व प्रतिशत"}
        ],
        "golden_rules": [
            "दशमलव संख्या को 'Point' बोलें, जैसे: 3.14 = 'Three point one four'।",
            "वर्गमूल = 'Square root', घनमूल = 'Cube root'।",
            "बराबर को 'Equals' या 'Is equal to' बोलें।"
        ],
        "vocabulary": [
            {"word": "Calculation", "meaning": "गणना / हिसाब", "example": "His mental calculation is very fast."},
            {"word": "Average", "meaning": "औसत", "example": "The average score of the team was 85."},
            {"word": "Percentage", "meaning": "प्रतिशत", "example": "She scored a high percentage in exams."}
        ],
        "examples": [
            {"hindi": "इस संख्या का वर्गमूल क्या है?", "english": "What is the square root of this number?"},
            {"hindi": "उसने परीक्षा में 90 प्रतिशत अंक प्राप्त किए।", "english": "He scored 90 percent marks in the exam."},
            {"hindi": "दोनों संख्याओं का औसत निकालो।", "english": "Calculate the average of both numbers."},
            {"hindi": "दस में पांच जोड़ने पर पंद्रह आता है।", "english": "Adding five to ten gives fifteen."},
            {"hindi": "इस कमरे की लंबाई और चौड़ाई नापो।", "english": "Measure the length and width of this room."},
            {"hindi": "यह समस्या गणितीय गणना पर आधारित है।", "english": "This problem is based on mathematical calculation."}
        ]
    },
    {
        "id": 38,
        "title": "Foods & Kitchen Vocabulary",
        "hindi_title": "खान-पान, मसाले और रसोई शब्दावली (Culinary & Kitchen)",
        "category": "Vocabulary Master",
        "level": "intermediate",
        "emoji": "🍕",
        "definition": "रसोई के सामान, खाना पकाने के तरीके (उबालना, तलना, भूनना), मसाले और खाने-पीने से संबंधित सभी शब्द।",
        "structures": [
            {"name": "Cooking Actions", "formula": "Knead dough / Chop vegetables / Boil water / Fry onions", "hindi": "खाना पकाने की क्रियाएं"},
            {"name": "Taste Descriptors", "formula": "Spicy / Salty / Crispy / Bland / Sweet", "hindi": "स्वाद के प्रकार"}
        ],
        "golden_rules": [
            "आटा गूंधने को 'Knead the dough' कहते हैं।",
            "सब्जी बारीक काटने को 'Chop' और छीलने को 'Peel' कहते हैं।"
        ],
        "vocabulary": [
            {"word": "Ingredients", "meaning": "सामग्री / संघटक", "example": "Mix all ingredients in a bowl."},
            {"word": "Delicious", "meaning": "स्वादिष्ट / लजीज", "example": "The homemade curry is delicious."},
            {"word": "Spices", "meaning": "मसाले", "example": "Indian food is famous for its spices."}
        ],
        "examples": [
            {"hindi": "आटा गूंधने में मेरी मदद करो।", "english": "Help me knead the dough."},
            {"hindi": "यह खाना बहुत स्वादिष्ट है।", "english": "This food is very delicious."},
            {"hindi": "दूध को उबालने के लिए रख दो।", "english": "Put the milk on to boil."},
            {"hindi": "कृपया प्याज को बारीक काट लो।", "english": "Please chop the onions finely."},
            {"hindi": "सब्जी में थोड़ा नमक कम है।", "english": "There is a little less salt in the vegetables."},
            {"hindi": "आलू को छीलकर टुकड़ों में काटें।", "english": "Peel the potatoes and cut them into pieces."}
        ]
    },
    {
        "id": 39,
        "title": "Relations & Family Vocabulary",
        "hindi_title": "पारिवारिक रिश्ते और संबंध (Kinship & Relations)",
        "category": "Vocabulary Master",
        "level": "beginner",
        "emoji": "👨‍👩‍👧",
        "definition": "पारिवारिक रिश्तों (भतीजा, भांजी, सास, ससुर, देवर, भाभी, चचेरा भाई) को अंग्रेजी में सही ढंग से पुकारने की शब्दावली।",
        "structures": [
            {"name": "In-Laws (ससुराल के रिश्ते)", "formula": "Father-in-law / Mother-in-law / Brother-in-law", "hindi": "ससुराल के संबंधी"},
            {"name": "Blood Relations", "formula": "Siblings (सगे भाई-बहन) / Maternal uncle (मामा)", "hindi": "सगे रिश्ते"}
        ],
        "golden_rules": [
            "सगे भाई-बहन के लिए 'Siblings' शब्द का प्रयोग करें।",
            "मामा/मौसा/चाचा सभी को 'Uncle' कहा जाता है, अंतर स्पष्ट करने के लिए 'Maternal' (माता पक्ष) व 'Paternal' (पिता पक्ष) लगाएं।"
        ],
        "vocabulary": [
            {"word": "Nephew", "meaning": "भतीजा या भांजा", "example": "My nephew is very intelligent."},
            {"word": "Niece", "meaning": "भतीजी या भांजी", "example": "My niece loves painting."},
            {"word": "Siblings", "meaning": "सगे भाई-बहन", "example": "How many siblings do you have?"}
        ],
        "examples": [
            {"hindi": "मेरा भतीजा बहुत शरारती है।", "english": "My nephew is very naughty."},
            {"hindi": "मेरे दो सगे भाई-बहन हैं।", "english": "I have two siblings."},
            {"hindi": "मेरे मामा जी कल शहर आएंगे।", "english": "My maternal uncle will come to town tomorrow."},
            {"hindi": "वे मेरे ससुराल वाले हैं।", "english": "They are my in-laws."},
            {"hindi": "हम सब मिलकर दिवाली मनाते हैं।", "english": "We celebrate Diwali together as a family."},
            {"hindi": "उसकी भाभी एक शिक्षिका हैं।", "english": "His sister-in-law is a teacher."}
        ]
    },
    {
        "id": 40,
        "title": "Stationery & Education Vocabulary",
        "hindi_title": "स्टेशनरी और अध्ययन सामग्री (Stationery & School)",
        "category": "Vocabulary Master",
        "level": "beginner",
        "emoji": "✏️",
        "definition": "स्कूल, कॉलेज और ऑफिस की लेखन सामग्री और अध्ययन से संबंधित उपयोगी अंग्रेजी शब्द।",
        "structures": [
            {"name": "Requesting Items", "formula": "Can you lend me your [Item]?", "hindi": "उधार मांगना"},
            {"name": "School Actions", "formula": "Staple papers / Highlight text / Erase mistake", "hindi": "लेखन क्रियाएं"}
        ],
        "golden_rules": [
            "Stationery (सामान) में 'e' आता है, जबकि Stationary (स्थिर/रुका हुआ) में 'a' आता है!",
            "पेंसिल छीलने को 'Sharpen the pencil' कहते हैं।"
        ],
        "vocabulary": [
            {"word": "Stapler", "meaning": "स्टेपलर", "example": "Please staple these sheets together."},
            {"word": "Highlighter", "meaning": "हाइलाइटर पेन", "example": "Use a yellow highlighter for main points."},
            {"word": "Syllabus", "meaning": "पाठ्यक्रम", "example": "We have completed the entire syllabus."}
        ],
        "examples": [
            {"hindi": "कृपया मुझे एक स्टेपलर दे दो।", "english": "Please give me a stapler."},
            {"hindi": "इस महत्वपूर्ण वाक्य को हाइलाइट करो।", "english": "Highlight this important sentence."},
            {"hindi": "वार्षिक परीक्षा अगले महीने शुरू होगी।", "english": "The annual examination will start next month."},
            {"hindi": "क्या मैं तुम्हारी पेंसिल ले सकता हूँ?", "english": "Can I borrow your pencil?"},
            {"hindi": "अपनी कॉपी में साफ़-सुथरा लिखो।", "english": "Write neatly in your notebook."},
            {"hindi": "कागज को कैंची से काटो।", "english": "Cut the paper with scissors."}
        ]
    },
    {
        "id": 41,
        "title": "Factory, Production & Sports Vocabulary",
        "hindi_title": "उद्योग, निर्माण और खेलकूद शब्दावली",
        "category": "Vocabulary Master",
        "level": "intermediate",
        "emoji": "⚽",
        "definition": "कारखानों में काम आने वाले तकनीकी शब्द तथा क्रिकेट, फुटबॉल आदि खेलों की कमेंट्री व नियमों के शब्द।",
        "structures": [
            {"name": "Sports Results", "formula": "Team A defeated Team B by 5 wickets / 2 goals", "hindi": "खेल का परिणाम"},
            {"name": "Factory Terms", "formula": "Raw material -> Production line -> Quality check", "hindi": "उत्पादन प्रक्रिया"}
        ],
        "golden_rules": [
            "खेल में मैच ड्रा होने को 'Tied / Drawn match' कहते हैं।",
            "कच्चे माल को 'Raw material' और तैयार उत्पाद को 'Finished goods' कहते हैं।"
        ],
        "vocabulary": [
            {"word": "Tournament", "meaning": "प्रतियोगिता / टूर्नामेंट", "example": "Our school won the cricket tournament."},
            {"word": "Referee", "meaning": "निर्णायक / रेफरी", "example": "The referee blew the final whistle."},
            {"word": "Manufacturing", "meaning": "उत्पादन / निर्माण", "example": "The factory specializes in shoe manufacturing."}
        ],
        "examples": [
            {"hindi": "हमारी टीम ने टूर्नामेंट जीत लिया।", "english": "Our team won the tournament."},
            {"hindi": "कारखाने में नई मशीनें लगाई गई हैं।", "english": "New machines have been installed in the factory."},
            {"hindi": "रेफरी ने सही फैसला सुनाया।", "english": "The referee gave the right decision."},
            {"hindi": "भारत ने मैच में शानदार प्रदर्शन किया।", "english": "India performed brilliantly in the match."},
            {"hindi": "उत्पादन की गुणवत्ता की जांच की जा रही है।", "english": "The quality of production is being checked."},
            {"hindi": "खिलाड़ियों ने मैदान पर कड़ा अभ्यास किया।", "english": "The players practiced hard on the field."}
        ]
    },
    {
        "id": 42,
        "title": "Sound, Music & Weather Vocabulary",
        "hindi_title": "ध्वनि, संगीत और मौसम शब्दावली (Atmosphere & Acoustics)",
        "category": "Vocabulary Master",
        "level": "intermediate",
        "emoji": "🎵",
        "definition": "विभिन्न प्रकार की आवाजों (फुसफुसाना, गड़गड़ाहट), संगीत की विधाओं और मौसम (धुंध, बूंदाबांदी, तूफान) के शब्द।",
        "structures": [
            {"name": "Weather Report", "formula": "It is raining / drizzling / freezing / humid today", "hindi": "मौसम बताना"},
            {"name": "Sounds", "formula": "Whisper (फुसफुसाना) / Echo (गूंज) / Rustle (सरसराहट)", "hindi": "आवाज़ों के प्रकार"}
        ],
        "golden_rules": [
            "हल्की बारिश को 'Drizzle' और मूसलाधार बारिश को 'Downpour' कहते हैं।",
            "हवा में नमी होने पर 'Humid' कहा जाता है।"
        ],
        "vocabulary": [
            {"word": "Drizzle", "meaning": "बूंदाबांदी होना", "example": "It is drizzling outside, carry an umbrella."},
            {"word": "Thunder", "meaning": "बिजली की गड़गड़ाहट", "example": "The thunder was loud and scary."},
            {"word": "Melody", "meaning": "मधुर धुन", "example": "She played a soft melody on the piano."}
        ],
        "examples": [
            {"hindi": "बाहर हल्की बूंदाबांदी हो रही है।", "english": "It is drizzling outside."},
            {"hindi": "बादलों की गड़गड़ाहट बहुत तेज थी।", "english": "The thunder was very loud."},
            {"hindi": "यह गाना बहुत मधुर और शांत है।", "english": "This song is very melodious and calm."},
            {"hindi": "आज मौसम काफी सुहावना है।", "english": "The weather is quite pleasant today."},
            {"hindi": "हवा में सूखे पत्ते सरसरा रहे हैं।", "english": "Dry leaves are rustling in the wind."},
            {"hindi": "कमरे में किसी ने धीरे से फुसफुसाया।", "english": "Someone whispered softly in the room."}
        ]
    },
    {
        "id": 43,
        "title": "Colours, Law & Judiciary Vocabulary",
        "hindi_title": "रंग, कानून, अदालत और संविधान शब्दावली",
        "category": "Vocabulary Master",
        "level": "advanced",
        "emoji": "🎨",
        "definition": "अदालती कार्यवाही, संविधान, कानूनी अधिकार, गवाह और न्यायिक प्रणाली के महत्वपूर्ण शब्द।",
        "structures": [
            {"name": "Courtroom Terms", "formula": "Judge pronounced the verdict / Lawyer presented evidence", "hindi": "न्यायालयीन प्रक्रिया"},
            {"name": "Rights & Constitution", "formula": "Fundamental rights are guaranteed by the constitution", "hindi": "संवैधानिक अधिकार"}
        ],
        "golden_rules": [
            "फैसले को 'Verdict' या 'Judgement' कहा जाता है।",
            "वकील को 'Advocate' या 'Lawyer' कहते हैं।"
        ],
        "vocabulary": [
            {"word": "Verdict", "meaning": "अदालत का फैसला", "example": "The jury delivered a unanimous verdict."},
            {"word": "Evidence", "meaning": "सबूत / साक्ष्य", "example": "There was no strong evidence against him."},
            {"word": "Constitution", "meaning": "संविधान", "example": "The constitution protects our rights."}
        ],
        "examples": [
            {"hindi": "अदालत ने अपना अंतिम फैसला सुना दिया।", "english": "The court announced its final verdict."},
            {"hindi": "गवाह ने सच बोलने की शपथ ली।", "english": "The witness took an oath to speak the truth."},
            {"hindi": "संविधान सभी नागरिकों को समानता देता है।", "english": "The constitution gives equality to all citizens."},
            {"hindi": "वकील ने ठोस सबूत पेश किए।", "english": "The lawyer presented concrete evidence."},
            {"hindi": "आरोपी को जमानत पर रिहा कर दिया गया।", "english": "The accused was released on bail."},
            {"hindi": "कानून के समक्ष सब बराबर हैं।", "english": "Everyone is equal before the law."}
        ]
    },
    {
        "id": 44,
        "title": "Professions & Occupations Vocabulary",
        "hindi_title": "व्यवसाय, पेशा और आजीविका (Careers & Jobs)",
        "category": "Professional",
        "level": "intermediate",
        "emoji": "👔",
        "definition": "अलग-अलग व्यवसायों, सरकारी व निजी नौकरियों, स्वरोजगार और कारीगरों के अंग्रेजी नाम।",
        "structures": [
            {"name": "Stating Profession", "formula": "He is an architect / She works as a software engineer", "hindi": "पेशा बताना"},
            {"name": "Work Description", "formula": "Surgeon performs operations / Pilot flies airplanes", "hindi": "काम का विवरण"}
        ],
        "golden_rules": [
            "पेशा बताने से पहले Vowel sound पर 'An' (an engineer) और Consonant sound पर 'A' (a doctor) अवश्य लगाएं।",
            "व्यवसायी को 'Entrepreneur' या 'Businessman' कहते हैं।"
        ],
        "vocabulary": [
            {"word": "Architect", "meaning": "वास्तुकार / नक्शा बनाने वाला", "example": "An architect designs beautiful buildings."},
            {"word": "Surgeon", "meaning": "शल्य चिकित्सक / सर्जन", "example": "The surgeon performed a complex operation."},
            {"word": "Entrepreneur", "meaning": "उद्यमी / नया व्यापारी", "example": "He is a successful tech entrepreneur."}
        ],
        "examples": [
            {"hindi": "वह एक बहुत कुशल वास्तुकार है।", "english": "He is a very skilled architect."},
            {"hindi": "सर्जन ने सफल ऑपरेशन किया।", "english": "The surgeon performed a successful operation."},
            {"hindi": "पत्रकार ने मंत्री से तीखे सवाल पूछे।", "english": "The journalist asked sharp questions to the minister."},
            {"hindi": "नल ठीक करने के लिए प्लंबर को बुलाओ।", "english": "Call the plumber to fix the water tap."},
            {"hindi": "वह एक प्रसिद्ध वैज्ञानिक बनना चाहती है।", "english": "She wants to become a famous scientist."},
            {"hindi": "बिजली का काम करने के लिए इलेक्ट्रीशियन आया।", "english": "The electrician came to do the electrical work."}
        ]
    },
    {
        "id": 45,
        "title": "Buildings, Architecture & Travel Vocabulary",
        "hindi_title": "इमारतें, स्थापत्य और यात्रा शब्दावली (Travel & Places)",
        "category": "Professional",
        "level": "intermediate",
        "emoji": "🏢",
        "definition": "हवाई अड्डा, रेलवे स्टेशन, होटल बुकिंग, दर्शनीय स्थल और भव्य इमारतों से जुड़े शब्द।",
        "structures": [
            {"name": "Booking & Travel", "formula": "I want to reserve a ticket / book a hotel room", "hindi": "यात्रा की बुकिंग"},
            {"name": "Airport Formalities", "formula": "Boarding pass / Baggage claim / Departure terminal", "hindi": "एयरपोर्ट के नियम"}
        ],
        "golden_rules": [
            "सामान के लिए 'Luggage' या 'Baggage' का प्रयोग होता है (ये हमेशा Uncountable होते हैं, कभी 'luggages' न कहें)।",
            "होटल में रुकने को 'Stay at a hotel' कहते हैं।"
        ],
        "vocabulary": [
            {"word": "Skyscraper", "meaning": "गगनचुंबी इमारत", "example": "Dubai has the tallest skyscraper."},
            {"word": "Reservation", "meaning": "आरक्षण / बुकिंग", "example": "I made a flight reservation online."},
            {"word": "Monument", "meaning": "ऐतिहासिक स्मारक", "example": "Taj Mahal is a world-famous monument."}
        ],
        "examples": [
            {"hindi": "दुबई में दुनिया की सबसे ऊंची गगनचुंबी इमारत है।", "english": "Dubai has the tallest skyscraper in the world."},
            {"hindi": "कृपया हवाई अड्डे पर अपना बोर्डिंग पास दिखाएं।", "english": "Please show your boarding pass at the airport."},
            {"hindi": "हमने होटल का कमरा पहले से बुक कर लिया है।", "english": "We have reserved the hotel room in advance."},
            {"hindi": "यात्रियों को सामान की जांच करानी होगी।", "english": "Passengers must get their luggage checked."},
            {"hindi": "ताजमहल एक विश्व प्रसिद्ध ऐतिहासिक स्मारक है।", "english": "The Taj Mahal is a world-famous monument."},
            {"hindi": "हमारी उड़ान समय पर प्रस्थान करेगी।", "english": "Our flight will depart on schedule."}
        ]
    },
    {
        "id": 46,
        "title": "Advanced Spoken Vocabulary & Confidence",
        "hindi_title": "धाराप्रवाह अंग्रेजी और आत्मविश्वास (Fluency Master)",
        "category": "Professional",
        "level": "advanced",
        "emoji": "⭐",
        "definition": "अंग्रेजी बोलते समय झिझक (Hesitation) दूर करने, आत्मविश्वास बढ़ाने और प्रभावशाली शब्दों का प्रयोग करने की कला।",
        "structures": [
            {"name": "Expressing Confidence", "formula": "I am confident that... / Without any doubt...", "hindi": "आत्मविश्वास से बोलना"},
            {"name": "Clarifying Points", "formula": "To be honest... / In my personal opinion...", "hindi": "विचार स्पष्ट करना"}
        ],
        "golden_rules": [
            "अंग्रेजी बोलते समय गलती होने के डर से रुके नहीं, बोलते रहें (Fluency over perfection)।",
            "सोचने के लिए 'Um, Ah' के बजाय 'Well, Actually, As far as I know' जैसे फिलर वर्ड्स इस्तेमाल करें।"
        ],
        "vocabulary": [
            {"word": "Fluency", "meaning": "धाराप्रवाह बोलना", "example": "Daily practice will build your fluency."},
            {"word": "Hesitate", "meaning": "हिचकिचाना", "example": "Do not hesitate when speaking in public."},
            {"word": "Articulate", "meaning": "साफ़ और स्पष्ट बोलना", "example": "She is an articulate and bold speaker."}
        ],
        "examples": [
            {"hindi": "अंग्रेजी बोलते समय बिल्कुल मत हिचकिचाओ।", "english": "Do not hesitate while speaking English."},
            {"hindi": "उसने बड़े आत्मविश्वास के साथ भाषण दिया।", "english": "He delivered the speech with great confidence."},
            {"hindi": "नियमित अभ्यास से आप धाराप्रवाह बोल पाएंगे।", "english": "Regular practice will help you speak fluently."},
            {"hindi": "मेरे विचार से यह सबसे अच्छा विकल्प है।", "english": "In my opinion, this is the best option."},
            {"hindi": "उसने अपनी बात बहुत स्पष्ट तरीके से रखी।", "english": "She expressed her point very articulately."},
            {"hindi": "गलतियों से कभी मत डरो, उनसे सीखो।", "english": "Never fear mistakes, learn from them."}
        ]
    },
    {
        "id": 47,
        "title": "Phrasal Verbs Master",
        "hindi_title": "महत्वपूर्ण फ्रेज़ल वर्ब्स (Give up, Break down, Call off...)",
        "category": "Advanced Grammar",
        "level": "advanced",
        "emoji": "📦",
        "definition": "Verb + Preposition के मेल से बनने वाले Phrasal Verbs, जिनका अर्थ मूल क्रिया से एकदम अलग और बहुत प्रभावशाली होता है।",
        "structures": [
            {"name": "Give up (हार मानना / छोड़ना)", "formula": "Don't give up your dreams", "hindi": "प्रयास छोड़ना"},
            {"name": "Break down (खराब होना / रो पड़ना)", "formula": "The car broke down on the road", "hindi": "मशीन का खराब होना"},
            {"name": "Call off (रद्द करना)", "formula": "They called off the strike", "hindi": "हड़ताल या कार्यक्रम रद्द करना"}
        ],
        "golden_rules": [
            "नेटिव स्पीकर्स (अंग्रेज) साधारण क्रियाओं के स्थान पर 70% Phrasal Verbs का ही प्रयोग करते हैं।",
            "Look after = देखभाल करना, Look for = ढूंढना, Look into = जांच करना।"
        ],
        "vocabulary": [
            {"word": "Call off", "meaning": "रद्द करना", "example": "The match was called off due to heavy rain."},
            {"word": "Look after", "meaning": "देखभाल करना", "example": "She looks after her elderly parents."},
            {"word": "Run out of", "meaning": "खत्म हो जाना", "example": "We have run out of cooking gas."}
        ],
        "examples": [
            {"hindi": "मुसीबतों में कभी हार मत मानो।", "english": "Never give up in difficult times."},
            {"hindi": "हमारी कार रास्ते में अचानक खराब हो गई।", "english": "Our car broke down suddenly on the way."},
            {"hindi": "बारिश के कारण मैच रद्द कर दिया गया।", "english": "The match was called off due to heavy rain."},
            {"hindi": "वह अपने छोटे भाई की अच्छी देखभाल करती है।", "english": "She looks after her younger brother very well."},
            {"hindi": "रसोई में दूध खत्म हो गया है।", "english": "We have run out of milk in the kitchen."},
            {"hindi": "पुलिस मामले की गहराई से जांच कर रही है।", "english": "The police are looking into the matter thoroughly."}
        ]
    },
    {
        "id": 48,
        "title": "Everyday Idioms & Expressions",
        "hindi_title": "दैनिक जीवन के प्रसिद्ध मुहावरे (English Idioms)",
        "category": "Advanced Grammar",
        "level": "advanced",
        "emoji": "🌅",
        "definition": "अंग्रेजी के वे मुहावरे जो बातचीत को खूबसूरत और देसी मुहावरों की तरह असरदार बनाते हैं।",
        "structures": [
            {"name": "Piece of cake (बाएं हाथ का खेल / बहुत आसान)", "formula": "This task is a piece of cake", "hindi": "बहुत सरल काम"},
            {"name": "Once in a blue moon (ईद का चांद / कभी-कभार)", "formula": "He visits us once in a blue moon", "hindi": "बहुत कम दिखने वाला"},
            {"name": "Under the weather (तबीयत नासाज होना)", "formula": "I am feeling under the weather", "hindi": "अस्वस्थ महसूस करना"}
        ],
        "golden_rules": [
            "मुहावरों का शाब्दिक (Word-by-word) अनुवाद नहीं किया जाता, उनका भावार्थ समझा जाता है।",
            "'Break a leg' का मतलब टांग तोड़ना नहीं, बल्कि 'शुभकामनाएं (Good luck)' होता है!"
        ],
        "vocabulary": [
            {"word": "Piece of cake", "meaning": "बेहद आसान काम", "example": "Passing this quiz is a piece of cake."},
            {"word": "Break a leg", "meaning": "शुभकामनाएं (Good luck)", "example": "Break a leg for your stage performance!"},
            {"word": "Spill the beans", "meaning": "राज़ खोल देना", "example": "Don't spill the beans about the party."}
        ],
        "examples": [
            {"hindi": "यह परीक्षा मेरे लिए बाएं हाथ का खेल थी।", "english": "This exam was a piece of cake for me."},
            {"hindi": "वह कभी-कभार ही हमसे मिलने आता है।", "english": "He visits us once in a blue moon."},
            {"hindi": "आज मेरी तबीयत थोड़ी ठीक नहीं लग रही है।", "english": "I am feeling a bit under the weather today."},
            {"hindi": "अपने इंटरव्यू के लिए शुभकामनाएं!", "english": "Break a leg for your job interview!"},
            {"hindi": "उसने पार्टी का सारा राज़ खोल दिया।", "english": "He spilled the beans about the surprise party."},
            {"hindi": "मुश्किल समय में धैर्य बनाए रखो।", "english": "Hang in there during tough times."}
        ]
    },
    {
        "id": 49,
        "title": "Real-Life Conversation Sheets",
        "hindi_title": "वास्तविक बातचीत अभ्यास (Doctor, Shop, Hotel, Interview)",
        "category": "Conversation Sheets",
        "level": "advanced",
        "emoji": "💬",
        "definition": "दैनिक जीवन की 5 सबसे मुख्य परिस्थितियों (इंटरव्यू, डॉक्टर, खरीदारी, होटल व रेस्टोरेंट) में की जाने वाली बातचीत की पूरी गाइड।",
        "structures": [
            {"name": "At the Doctor's", "formula": "Doctor, I have a complaint of [Symptoms]", "hindi": "डॉक्टर से बातचीत"},
            {"name": "Shopping & Bargaining", "formula": "Could you show me a smaller size? Any discount?", "hindi": "दुकानदार से बात"},
            {"name": "Hotel Check-in", "formula": "I have a reservation under the name [Name]", "hindi": "होटल में बातचीत"}
        ],
        "golden_rules": [
            "दुकान या होटल में हमेशा 'Could you please...' से शुरुआत करें, यह 'Can you' से अधिक विनम्र होता है।",
            "इंटरव्यू में 'Yes Sir / No Sir' के साथ एक संक्षिप्त कारण अवश्य जोड़ें।"
        ],
        "vocabulary": [
            {"word": "Discount", "meaning": "छूट / बट्टा", "example": "Can you offer any discount on this item?"},
            {"word": "Recommendation", "meaning": "सिफारिश / सुझाव", "example": "What is your chef's recommendation?"},
            {"word": "Vacancy", "meaning": "खाली पद / कमरा", "example": "Is there any room vacancy available tonight?"}
        ],
        "examples": [
            {"hindi": "मुझे दो दिनों से सिरदर्द की शिकायत है।", "english": "I have been suffering from a headache for two days."},
            {"hindi": "क्या आप मुझे इस शर्ट पर कोई छूट दे सकते हैं?", "english": "Can you give me any discount on this shirt?"},
            {"hindi": "मुझे एक नॉन-एसी सिंगल कमरा चाहिए।", "english": "I want a single non-AC room for two nights."},
            {"hindi": "आपके यहाँ मेन कोर्स में क्या खास है?", "english": "What is special in your main course menu?"},
            {"hindi": "क्या मैं क्रेडिट कार्ड से भुगतान कर सकता हूँ?", "english": "Can I pay by credit card?"},
            {"hindi": "कृपया बिल ले आइए।", "english": "Could you please bring the bill?"},
            {"hindi": "क्या आप मुझे स्टेशन का रास्ता बता सकते हैं?", "english": "Could you please guide me to the railway station?"},
            {"hindi": "आपसे मिलकर बहुत खुशी हुई।", "english": "It was a great pleasure meeting you."}
        ]
    },
    {
        "id": 50,
        "title": "Master Review & Final Practice Worksheets",
        "hindi_title": "सम्पूर्ण पाठ्यक्रम समीक्षा (Comprehensive Final Test)",
        "category": "Review & Worksheets",
        "level": "advanced",
        "emoji": "🏆",
        "definition": "पूरे Mass Spoken English कोर्स के सभी 49 अध्यायों (Be Verb, Modals, Tenses, Prepositions, Phrasal Verbs) का व्यापक रिवीज़न और मास्टर टेस्ट।",
        "structures": [
            {"name": "Conditional Sentences", "formula": "If + Present Simple, Future Simple", "hindi": "यदि तुम मेहनत करोगे तो सफल होगे - If you work hard, you will succeed"},
            {"name": "Reported Speech", "formula": "He said that he would come tomorrow", "hindi": "परोक्ष कथन"},
            {"name": "Complex Mixed Sentences", "formula": "Although he was ill, he attended the class", "hindi": "मिश्रित वाक्य"}
        ],
        "golden_rules": [
            "अंग्रेजी सीखने का अंतिम नियम: रोज़ाना कम से कम 15 मिनट बोलकर अभ्यास करें!",
            "सोचना भी अंग्रेजी में शुरू करें (Think in English to speak in English)!"
        ],
        "vocabulary": [
            {"word": "Perseverance", "meaning": "दृढ़ता / लगन", "example": "Perseverance leads to complete success."},
            {"word": "Mastery", "meaning": "महारत / निपुणता", "example": "You have achieved mastery in spoken English."},
            {"word": "Accomplishment", "meaning": "उपलब्धि", "example": "Completing this 50-chapter course is an accomplishment."}
        ],
        "examples": [
            {"hindi": "यदि तुम मेहनत करोगे तो अवश्य सफल हो जाओगे।", "english": "If you work hard, you will definitely succeed."},
            {"hindi": "उसने कहा था कि वह कल सुबह आएगा।", "english": "He said that he would come tomorrow morning."},
            {"hindi": "हमें अपने महान देश पर गर्व होना चाहिए।", "english": "We should always be proud of our great country."},
            {"hindi": "उसने मुझे समय रहते सही चेतावनी दी थी।", "english": "He had warned me in time."},
            {"hindi": "यद्यपि वह बीमार था, फिर भी वह काम पर आया।", "english": "Although he was ill, he still came to work."},
            {"hindi": "अब मैं आत्मविश्वास के साथ अंग्रेजी बोल सकता हूँ।", "english": "Now I can speak English with complete confidence."},
            {"hindi": "अभ्यास ही मनुष्य को निपुण बनाता है।", "english": "Practice makes a man perfect."},
            {"hindi": "मैंने आज अपना स्पोकन इंग्लिश कोर्स पूरा कर लिया।", "english": "I have completed my spoken English course today."}
        ]
    }
]

def main():
    existing_21 = get_existing_21()
    print(f"Loaded existing {len(existing_21)} chapters.")

    all_50 = list(existing_21)

    for ch in chapters_22_to_50:
        exs = ch.get("examples", [])
        ch["sentence_builder_drills"] = build_drills(exs)
        ch["worksheet_quiz"] = make_quiz(exs, ch["id"])
        all_50.append(ch)

    curriculum = {
        "metadata": {
            "source": "Mass Spoken English Complete Course (Full 50 Chapters)",
            "total_chapters": len(all_50),
            "description": "Complete 50-Chapter Spoken English Course with formulas, rules, interactive sentence builder drills, flashcards, and quizzes."
        },
        "chapters": all_50
    }

    out_path = r'd:\EduSarthi\edusarthi_backend\edusarthi_backend\data\mass_spoken_curriculum.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(curriculum, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS! Generated {out_path} with {len(all_50)} chapters!")

if __name__ == '__main__':
    main()

