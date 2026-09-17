# ai_service.py
import json
import uuid
from openai import OpenAI
from config import MODEL

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = __import__("os").getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        _client = OpenAI(api_key=api_key)
    return _client


def _difficulty_name(value):
    return value.split(" / ")[0]


def _competency_name(value):
    return value.split(" / ")[0]


def generate_task(language, difficulty, competency):
    difficulty_en = _difficulty_name(difficulty)
    competency_hy = _competency_name(competency)

    quiz_instruction = ""
    if competency_hy == "Կոդի ընկալում"  and difficulty_en == "Easy":
        quiz_instruction = """
Այս դեպքում առաջադրանքը պարտադիր պետք է ունենա 4 ընտրանքային պատասխան։
Միայն մեկ տարբերակն է ճիշտ։ Չներառել սխալի ուղղում, bug fixing կամ
կոդի փոփոխում։ Quiz-ը պետք է ստուգի միայն այն, թե ուսանողը հասկանում է՝
ինչ է անում կոդը։
"""
    if competency_hy == "Սխալի հայտնաբերում և ուղղում" and difficulty_en == "Easy":

        quiz_instruction = """
ԿԱՐԵՎՈՐ ՀԱՏՈՒԿ ԿԱՆՈՆ EASY ՄԱԿԱՐԴԱԿԻ ՀԱՄԱՐ։

Կոմպետենցիա՝ «Սխալի հայտնաբերում և ուղղում»
Բարդություն՝ Easy

Այս մակարդակում առաջադրանքը ՊԱՐՏԱԴԻՐ պետք է բաղկացած լինի 2 առանձին մասից։

ՄԱՍ 1 — ԹԵՍՏ. «Բացատրիր՝ ինչ է անում կոդը»

Այս մասը ՊԱՐՏԱԴԻՐ պետք է լինի choice թեստ։

"""

    prompt = f"""
Դու գիտական հետազոտության համար առաջադրանքների նախագծող ես։

Ստեղծիր մեկ կարճ, իրատեսական ծրագրավորման առաջադրանք՝
AI-ի գեներացրած կոդի հետ աշխատանքի կարողությունը չափելու համար։

Լեզու՝ {language}
Բարդություն՝ {difficulty_en}
Կոմպետենտություն՝ {competency_hy}

Պարտադիր սկզբունքներ.
- Easy / Հեշտ՝ սկսնակ մակարդակ։
- Medium / Միջին՝ մոտավորապես 1–2 տարի ծրագրավորում սովորած ուսանող։
- Hard / Բարդ՝ առաջադեմ ուսանող։
- Կոդը լինի կարճ, հասկանալի և հետազոտական նպատակով ստուգելի։
- Պահանջը լինի կարճ, պարզ և ամբողջական։
- Մի տուր լուծումը։
- Կոդը պետք է ունենա չափելի ակնկալվող արդյունք։
- Առաջադրանքը պետք է հնարավոր լինի գնահատել 0–100 սանդղակով։
- Կոդի ընկալման դեպքում ստուգիր միայն կոդի իմաստի ընկալումը։
- Սխալի հայտնաբերման դեպքում պետք է լինի իրական, լուծելի սխալ։
- Ադապտացման դեպքում պետք է լինի կարճ նոր պահանջ, որին պետք է հարմարեցնել կոդը։
- Օպտիմալացման դեպքում պահանջը պետք է թույլ տա գնահատել արդյունավետության կամ
  կոդի կառուցվածքի բարելավումը։
{quiz_instruction}

Վերադարձրու միայն JSON՝ համաձայն schema-ի։
"""

    response = get_client().responses.create(
        model=MODEL,
        input=prompt,
        max_output_tokens=1800,
        text={
            "format": {
                "type": "json_schema",
                "name": "code_task",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "code": {"type": "string"},
                        "requirements": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "expected_competency": {"type": "string"},
                        "test_hint": {"type": "string"},
                        "quiz_options": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                        "correct_option_index": {
                            "type": "integer",
                            "minimum": 0,
                            "maximum": 3,
                        },
                    },
                    "required": [
                        "title",
                        "description",
                        "code",
                        "requirements",
                        "expected_competency",
                        "test_hint",
                        "quiz_options",
                        "correct_option_index",
                    ],
                    "additionalProperties": False,
                },
            }
        },
    )

    data = json.loads(response.output_text)
    data["task_id"] = "TASK-" + uuid.uuid4().hex[:10].upper()
    return data


def evaluate_solution(
    task,
    explanation,
    student_code,
    selected_option,
    language,
    difficulty,
    competency,
):
    difficulty_en = _difficulty_name(difficulty)
    competency_hy = _competency_name(competency)

    prompt = f"""
Դու գիտական հետազոտության գնահատող ես։
Գնահատիր ուսանողի աշխատանքը խիստ, բայց արդար և reproducible rubric-ով։

ԱՌԱՋԱԴՐԱՆՔ
{json.dumps(task, ensure_ascii=False)}

ԼԵԶՈՒ
{language}

ԲԱՐԴՈՒԹՅՈՒՆ
{difficulty_en}

ԿՈՄՊԵՏԵՆՏՈՒԹՅՈՒՆ
{competency_hy}

ՈՒՍԱՆՈՂԻ ԲԱՑԱՏՐՈՒԹՅՈՒՆ
{explanation}

ՈՒՍԱՆՈՂԻ ՊԱՏԱՍԽԱՆԸ/ԿՈԴԸ
{student_code}

QUIZ ՊԱՏԱՍԽԱՆ
{selected_option}

Գնահատման կանոններ.
1. Յուրաքանչյուր չափանիշ գնահատիր 0–100։
2. total-ը հաշվիր որպես տվյալ առաջադրանքի հիմնական չափելի արդյունք՝
   համապատասխան կոմպետենտության գնահատականը։ Մի ստեղծիր պատահական միջին։
3. Կոդի ընկալում / Code Understanding:
   - Easy quiz դեպքում գնահատիր միայն ընտրած տարբերակի ճշտությունը։
   - Այս դեպքում problem_detection, adaptation և optimization թող 0։
   - Չպահանջես սխալի ուղղում։
4. Սխալի հայտնաբերում և ուղղում:
   - գնահատիր սխալի հայտնաբերման ճշտությունը,
   - պատճառի բացատրությունը,
   - ուղղված կոդի ճիշտությունը։
5. Կոդի ադապտացում:
   - գնահատիր նոր պահանջը ճիշտ հասկանալը,
   - փոփոխության համապատասխանությունը,
   - սկզբնական տրամաբանության պահպանման աստիճանը։
6. Կոդի օպտիմալացում:
   - գնահատիր correctness-ը,
   - արդյունավետության/կառուցվածքի բարելավումը,
   - ավելորդ բարդության բացակայությունը։
7. Feedback-ը գրիր կարճ, կոնկրետ և հայերեն։
8. strength և improvement դաշտերը պետք է լինեն օգտակար հետազոտական feedback,
   ոչ թե ընդհանուր գովասանք։

Վերադարձիր միայն JSON schema-ին համապատասխան։
"""

    response = get_client().responses.create(
        model=MODEL,
        input=prompt,
        max_output_tokens=1200,
        text={
            "format": {
                "type": "json_schema",
                "name": "code_evaluation",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "understanding": {"type": "integer", "minimum": 0, "maximum": 100},
                        "problem_detection": {"type": "integer", "minimum": 0, "maximum": 100},
                        "adaptation": {"type": "integer", "minimum": 0, "maximum": 100},
                        "optimization": {"type": "integer", "minimum": 0, "maximum": 100},
                        "clarity": {"type": "integer", "minimum": 0, "maximum": 100},
                        "total": {"type": "integer", "minimum": 0, "maximum": 100},
                        "feedback": {"type": "string"},
                        "strength": {"type": "string"},
                        "improvement": {"type": "string"},
                    },
                    "required": [
                        "understanding",
                        "problem_detection",
                        "adaptation",
                        "optimization",
                        "clarity",
                        "total",
                        "feedback",
                        "strength",
                        "improvement",
                    ],
                    "additionalProperties": False,
                },
            }
        },
    )
    return json.loads(response.output_text)
