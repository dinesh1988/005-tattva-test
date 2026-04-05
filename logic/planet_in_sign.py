"""Planet-in-Sign (Natal Rasi) Interpretations.

For each of the 7 classical planets in each of the 12 signs this module
provides the Vedic interpretation text and nature rating sourced from
VedAstro C# HoroscopeDataListStatic.cs (EventTag.Horoscope).

Rahu and Ketu are not included in the C# source data for this category.

Lookup key: (planet_name: str, sign_num: int) -> dict
  sign_num is 1-based: Aries=1 ... Pisces=12
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .time import AstroTime
from .consts import Planet
from .house_queries import get_planet_sign_num, get_planet_sign_name

# ---------------------------------------------------------------------------
# Sign names indexed 1–12
# ---------------------------------------------------------------------------

SIGN_NAMES = [
    "", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

_G = "Good"
_B = "Bad"

# ---------------------------------------------------------------------------
# Data table: (planet_name, sign_num) -> {nature, description}
# ---------------------------------------------------------------------------

_PLANET_IN_SIGN_DATA: Dict[Tuple[str, int], dict] = {

    # ── Sun ─────────────────────────────────────────────────────────────────
    ("Sun", 1): {
        "nature": _G,
        "description": (
            "Active intelligent famous traveler; wealthy warrior; variable fortune ambitious "
            "phlegmatic powerful marked personality impulsive irritable pioneering initiative."
        ),
    },
    ("Sun", 2): {
        "nature": _G,
        "description": (
            "Clever reflective attracted by perfumes and dealer in them hated by women slow to "
            "action musician self-confident delicious drinks happy meals tactful original "
            "sociable intelligent; prominent nose."
        ),
    },
    ("Sun", 3): {
        "nature": _G,
        "description": (
            "Learned; astronomer scholarly; grammarian polite wealthy critical assimilative "
            "good conversationalist shy reserved lacking in originality."
        ),
    },
    ("Sun", 4): {
        "nature": _G,
        "description": (
            "Somewhat harsh indolent wealthy unhappy constipation sickly travelling independent "
            "expert astrologer."
        ),
    },
    ("Sun", 5): {
        "nature": _G,
        "description": (
            "Stubborn fixed views strong cruel independent organizing capacity and talents for "
            "propaganda humanitarian frequenting solitary places generous famous."
        ),
    },
    ("Sun", 6): {
        "nature": _G,
        "description": (
            "Linguist poet mathematician taste for literature well scholarly artistic good "
            "memory reasoning faculty effeminate body frank lucid comprehension learned in "
            "religious lore reserved wanting adulation."
        ),
    },
    ("Sun", 7): {
        "nature": _G,
        "description": (
            "Manufacture of liquors popular; tactless base drunkard loose morals arrogant "
            "wicked frank submissive pompous."
        ),
    },
    ("Sun", 8): {
        "nature": _G,
        "description": (
            "Adventurous bold rearing thieves and robbers reckless cruel stubborn unprincipled "
            "impulsive idiotic indolent surgical skill dexterous military ability."
        ),
    },
    ("Sun", 9): {
        "nature": _G,
        "description": (
            "Short-tempered spoils reliable rich obstinate respected by all happy popular "
            "religious wealthy musician."
        ),
    },
    ("Sun", 10): {
        "nature": _G,
        "description": (
            "Mean-minded stubborn ignorant miserly pushful unhappy boring active meddlesome "
            "obliging humorous witty affable prudent firm."
        ),
    },
    ("Sun", 11): {
        "nature": _B,
        "description": (
            "Poor unhappy stubborn unlucky unsuccessful medium height rare faculties "
            "self-esteem."
        ),
    },
    ("Sun", 12): {
        "nature": _B,
        "description": (
            "Pearl merchant peaceful wealthy uneventful religious prodigal loved by women."
        ),
    },

    # ── Moon ────────────────────────────────────────────────────────────────
    ("Moon", 1): {
        "nature": _G,
        "description": (
            "Round eyes impulsive fond of travel irritable fond of women vegetable diet quick "
            "to decide and act haughty inflexible sores in the head dexterous tickle-minded "
            "war-like enterprising good position; self-respect valiant ambitious liable to "
            "hydrophobia if the Moon is afflicted large thighs popular restless idiosyncratic; "
            "versatile."
        ),
    },
    ("Moon", 2): {
        "nature": _G,
        "description": (
            "Liberal powerful; happy ability to command intelligent handsome influential fond "
            "of fair sex happy in middle life and old age great strides in life beautiful gait "
            "large thighs and hips phlegmatic afflictions rich patience respected love-intrigues "
            "inconsistent wavering mind sound judgment voracious eater and reader lucky popular "
            "influenced by women passionate indolent."
        ),
    },
    ("Moon", 3): {
        "nature": _G,
        "description": (
            "Well read creative fond of women learned in scriptures able persuasive curly hair "
            "powerful speaker clever; witty dexterous fond of music elevated nose thought "
            "reader subtle long life."
        ),
    },
    ("Moon", 4): {
        "nature": _G,
        "description": (
            "Wise powerful charming influenced by women wealthy kind good a bit stout sensitive "
            "impetuous unprofitable voyages meditative much immovable property scientist middle "
            "stature prudent frugal piercing; conventional."
        ),
    },
    ("Moon", 5): {
        "nature": _G,
        "description": (
            "Bold irritable large cheeks; blonde broad face brown eyes repugnant to women; "
            "likes meat frequenting forests and hills colic troubles inclined to be unhappy "
            "haughty mental anxiety liberal generous deformed body steady aristocratic settled "
            "views proud ambitious."
        ),
    },
    ("Moon", 6): {
        "nature": _G,
        "description": (
            "Lovely complexion almond eyes modest sunken shoulders and arms charming attractive "
            "principled affluent comfortable soft body sweet speech honest truthful modest "
            "virtuous; intelligent; phlegmatic fond of women; acute insight conceited in "
            "self-estimation pensive conversationalist many daughters loquacious astrologer and "
            "clairvoyant or attracted towards them skilled in arts like music and dancing few "
            "sons."
        ),
    },
    ("Moon", 7): {
        "nature": _G,
        "description": (
            "Reverence and respect for learned and holy people saints and gods tall raised nose "
            "thin deformed limbs sickly constitution rejected by kinsmen intelligent principled "
            "wealthy; business-like obliging love for arts far-seeing idealistic clever mutable "
            "amicable losses through women loves women just not ambitious aspiring."
        ),
    },
    ("Moon", 8): {
        "nature": _G,
        "description": (
            "Broad eyes wide chest round shanks and thighs isolation from parents or preceptors "
            "brown complexion; straight-forward frank; open-minded cruel; simulator malicious "
            "sterility agitated unhappy; wealthy impetuous obstinate."
        ),
    },
    ("Moon", 9): {
        "nature": _G,
        "description": (
            "Face broad teeth large skilled in fine arts; indistinct shoulders disfigured nails "
            "and arms; deep and inventive intellect; yielding to praise good speech upright; "
            "help from wife and women; happy marriage many children good inheritance benefactor "
            "patron of arts and literature; ceremonial-minded; showy unexpected gifts author "
            "reflective mentality inflexible to threats."
        ),
    },
    ("Moon", 10): {
        "nature": _G,
        "description": (
            "Ever attached to wife and children virtuous good eyes; slender waist quick in "
            "perception clever active crafty somewhat selfish sagacious strategic liberal; "
            "merciless unscrupulous inconsistent low morals niggardly and mean."
        ),
    },
    ("Moon", 11): {
        "nature": _B,
        "description": (
            "Fair-looking well-formed body tall large teeth belly low youngish sensual sudden "
            "elevations and depressions pure-minded; artistic; intuitional; diplomatic lonely; "
            "peevish; artistic taste energetic emotional esoteric mystical; grateful healing "
            "power."
        ),
    },
    ("Moon", 12): {
        "nature": _B,
        "description": (
            "Fixed dealer in pearls and fond of wife and children perfect build long nose "
            "bright body annihilating enemies subservient to opposite sex; handsome learned "
            "steady; simple good reputation loose morals adventurous many children spiritually "
            "inclined later in life."
        ),
    },

    # ── Mars ────────────────────────────────────────────────────────────────
    ("Mars", 1): {
        "nature": _G,
        "description": (
            "Organizing capacity commanding rich social scars in the body sensual; dark "
            "mathematician active powerful inspiring; pioneering; able statesmanly; frank "
            "generous careful not economical in domestic dealings vague imaginations combative "
            "tendencies hard-hearted; versatile."
        ),
    },
    ("Mars", 2): {
        "nature": _G,
        "description": (
            "Influenced by women timid rough body stubborn sensual liking for magic and sports "
            "somewhat unprincipled selfish tyrannical not soft-hearted rash emotional animal "
            "instinct strong sensitive."
        ),
    },
    ("Mars", 3): {
        "nature": _G,
        "description": (
            "Loving family and children taste in refinement scientific middle stature well "
            "built learned ambitious; quick rash ingenious skilled in music fearless tactless "
            "peevish unhappy subservient diplomatic humiliating detective."
        ),
    },
    ("Mars", 4): {
        "nature": _G,
        "description": (
            "Intelligent wealthy rich travels and voyages wicked; perverted love of "
            "agriculture; medical and surgical proficiency; fickle-minded defective sight bold "
            "dashing headlong speculative unkind; egoistic."
        ),
    },
    ("Mars", 5): {
        "nature": _G,
        "description": (
            "Tendency to occultism astrology astronomy and mathematics love for parents regard "
            "and respect for elders and preceptors independent thinking peevish; liberal "
            "victorious stomach troubles worried by mental complaints generous noble author "
            "early in life successful combative restless."
        ),
    },
    ("Mars", 6): {
        "nature": _G,
        "description": (
            "Imitable explosive trouble in digestive organs no marital harmony; general love "
            "for the fair sex revengeful self-confident; conceited affable boastful; "
            "materialistic ceremonial-minded positive indiscriminative pretentious deceptive "
            "scientific enterprises."
        ),
    },
    ("Mars", 7): {
        "nature": _G,
        "description": (
            "Tall body symmetrically built complexion fair and swarthy ambitious "
            "self-confident perceptive faculties materialistic love for family self-earned "
            "wealth affable warlike foresight business-like deceived by women sanguine "
            "temperament kind gentle fond of adulation easily ruffled boastful."
        ),
    },
    ("Mars", 8): {
        "nature": _G,
        "description": (
            "Middle stature clever; diplomatic positive tendency indulgent tenacious memory "
            "malicious aggressive proud haughty; great strides in life."
        ),
    },
    ("Mars", 9): {
        "nature": _G,
        "description": (
            "Gentlemanly many foes famous minister; statesman open frank pleasure loving few "
            "children liable to extremes conservative; indifferent exacting impatient severe "
            "quarrelsome; litigation troubles good citizen."
        ),
    },
    ("Mars", 10): {
        "nature": _G,
        "description": (
            "Rich; high political position many sons brave generous; love for children middle "
            "stature industrious indefatigable successful; penetrating bold tactful respected "
            "generous gallant influential."
        ),
    },
    ("Mars", 11): {
        "nature": _B,
        "description": (
            "Unhappy miserable poor not truthful independent unwise wandering impulsive; "
            "controversial; combative well-versed in dialects free quick in forgiving and "
            "forgetting conventional danger on water morose meditative."
        ),
    },
    ("Mars", 12): {
        "nature": _B,
        "description": (
            "Fair complexion; troubles in love affairs; few children passionate restless "
            "antagonistic exacting uncertainty of feeling faithful unclean colic indolent "
            "willful."
        ),
    },

    # ── Mercury ─────────────────────────────────────────────────────────────
    ("Mercury", 1): {
        "nature": _G,
        "description": (
            "Evil-minded middle stature obstinate clever social great endurance materialistic "
            "tendencies; unscrupulous wavering mind antagonistic fond of speculation; impulsive "
            "greedy dangerous connections deceitful swerving from rectitude."
        ),
    },
    ("Mercury", 2): {
        "nature": _G,
        "description": (
            "High position well built clever; logical mental harmony many children liberal "
            "persevering opinionative wealthy practicable friends among women of eminence "
            "inclination to sensual pleasures well read showy."
        ),
    },
    ("Mercury", 3): {
        "nature": _G,
        "description": (
            "Inclination to physical labor boastful sweet speech tall; active cultured tactful "
            "dexterous to mothers indolent inventive; taste in literature arts and sciences "
            "winning manners liable to throat and bronchial troubles musician mirthful studious."
        ),
    },
    ("Mercury", 4): {
        "nature": _G,
        "description": (
            "Witty likes music disliked by relations low stature speculative diplomatic "
            "discreet flexible restless sensual though religious liable to consumption strong "
            "parental love dislike for chastity."
        ),
    },
    ("Mercury", 5): {
        "nature": _G,
        "description": (
            "Few children; wanderer idiotic proud indolent not fond of women; boastful; "
            "orator; good memory low mothers poor early marriage independent in thinking "
            "impulsive positive will remunerative profession likes travelling."
        ),
    },
    ("Mercury", 6): {
        "nature": _G,
        "description": (
            "Learned virtuous liberal; fearless ingenious; handsome irritable refined subtle "
            "intuitive sociable no self-control morbid imaginations dyspeptic difficulties "
            "eloquent author priest astronomer."
        ),
    },
    ("Mercury", 7): {
        "nature": _G,
        "description": (
            "Fair complexion sanguine disposition; inclination to excesses perceptive faculties "
            "material tendencies frugal agreeable; courteous; philosophical faithful; "
            "ceremonial-minded sociable discreet."
        ),
    },
    ("Mercury", 8): {
        "nature": _G,
        "description": (
            "Short curly hair incentive to indulgence liable to disease of the generative "
            "organ general debility crafty malicious selfish subtle indiscreet bold reckless."
        ),
    },
    ("Mercury", 9): {
        "nature": _G,
        "description": (
            "Taste in sciences respected by polished society tall well built learned rash "
            "superstitious vigorous executive diplomatic cunning just capable."
        ),
    },
    ("Mercury", 10): {
        "nature": _G,
        "description": (
            "Selfless business tendencies economical debtor inconsistent low stature cunning "
            "inventive active; restless suspicious drudging."
        ),
    },
    ("Mercury", 11): {
        "nature": _B,
        "description": (
            "Middle stature licentious proud quarrelsome frank sociable rapid strides in life "
            "famous scholar cowardly weak constitution."
        ),
    },
    ("Mercury", 12): {
        "nature": _B,
        "description": (
            "A dependent serves others dexterous peevish indolent petty-minded respect for "
            "gods and Brahmins."
        ),
    },

    # ── Jupiter ─────────────────────────────────────────────────────────────
    ("Jupiter", 1): {
        "nature": _G,
        "description": (
            "Love of grandeur powerful wealthy prudent many children courteous generous firm "
            "sympathetic happy marriage patient nature harmonious refined high position."
        ),
    },
    ("Jupiter", 2): {
        "nature": _G,
        "description": (
            "Stately elegant self-importance liberal dutiful sons just sympathetic well read "
            "creative ability despotic healthy happy marriage liked by all inclination to "
            "self-gratification."
        ),
    },
    ("Jupiter", 3): {
        "nature": _G,
        "description": (
            "Oratorial ability tall well-built benevolent pure-hearted; scholarly; sagacious "
            "diplomatic linguist or poet elegant incentive."
        ),
    },
    ("Jupiter", 4): {
        "nature": _G,
        "description": (
            "Well read dignified; wealthy; comfortable intelligent swarthy complexion inclined "
            "to social gossip mathematician faithful."
        ),
    },
    ("Jupiter", 5): {
        "nature": _G,
        "description": (
            "Commanding appearance tall; great easily offended ambitious active happy "
            "intelligent wise prudent generous broad-minded literary harmonious surroundings "
            "likes hills and dales."
        ),
    },
    ("Jupiter", 6): {
        "nature": _G,
        "description": (
            "Middle stature ambitious selfish stoical resignation affectionate fortunate "
            "stingy lovable a beautiful wife great endurance learned."
        ),
    },
    ("Jupiter", 7): {
        "nature": _G,
        "description": (
            "Handsome free open-minded; hasty attractive just courteous strong able exhaustion "
            "from over-activity religious competent unassuming pleasing."
        ),
    },
    ("Jupiter", 8): {
        "nature": _G,
        "description": (
            "Tall somewhat stooping elegant manners serious exacting well built superior airs "
            "selfish imprudent weak constitution subservient to women passionate conventional "
            "proud zealous ceremonious unhappy life."
        ),
    },
    ("Jupiter", 9): {
        "nature": _G,
        "description": (
            "Pretty inheritance wealthy influential handsome noble trustworthy charitable good "
            "executive ability weak constitution artistic qualities poetic open-minded good "
            "conversationalist."
        ),
    },
    ("Jupiter", 10): {
        "nature": _G,
        "description": (
            "Tactless good intention disgraceful behaviour generous unhappy irritable "
            "inconsistent avaricious unmanly jealous."
        ),
    },
    ("Jupiter", 11): {
        "nature": _B,
        "description": (
            "Learned not rich controversial figure philosophical popular compassionate "
            "sympathetic amiable prudent humanitarian melancholic meditative dreamy dental "
            "troubles."
        ),
    },
    ("Jupiter", 12): {
        "nature": _B,
        "description": (
            "Good inheritance; stout medium height two marriages if with malefics enterprising "
            "political diplomacy high position."
        ),
    },

    # ── Venus ────────────────────────────────────────────────────────────────
    ("Venus", 1): {
        "nature": _G,
        "description": (
            "Extravagant active mutable artistic dreamy idealist proficient in fine arts "
            "licentious sorrowful fickle-minded prudent unhappy irreligious easy going loss "
            "of wealth due to loose life."
        ),
    },
    ("Venus", 2): {
        "nature": _G,
        "description": (
            "Well built handsome pleasing countenance independent sensual love of nature fond "
            "of pleasure elegant taste in dancing and music voluptuous."
        ),
    },
    ("Venus", 3): {
        "nature": _G,
        "description": (
            "Rich gentle kind generous eloquent proud respected gullible love of fine arts "
            "learned intelligent good logician just dual marriage; tendencies towards "
            "materialism."
        ),
    },
    ("Venus", 4): {
        "nature": _G,
        "description": (
            "Melancholy emotional timid more than one wife haughty sorrowful light character "
            "inconsistent unhappy many children sensitive learned."
        ),
    },
    ("Venus", 5): {
        "nature": _G,
        "description": (
            "Money through women pretty wife wayward conceited passionate fair complexion "
            "emotional zealous licentious; attracted by the fair sex premature in conclusions "
            "superior airs unvanquished by enemies."
        ),
    },
    ("Venus", 6): {
        "nature": _G,
        "description": (
            "Petty-minded licentious unscrupulous unhappy illicit love agile loquacious rich "
            "learned."
        ),
    },
    ("Venus", 7): {
        "nature": _G,
        "description": (
            "Statesman poet intelligent generous philosophical handsome matrimonial felicity "
            "successful marriage passionate proud respected intuitive sensual wide travels."
        ),
    },
    ("Venus", 8): {
        "nature": _G,
        "description": (
            "Broad features quarrelsome medium statured independent artistic unjust proud "
            "disappointed in love haughty not rich."
        ),
    },
    ("Venus", 9): {
        "nature": _G,
        "description": (
            "Medium height powerful wealthy respected impertinent generous frank happy domestic "
            "life high position philosophical."
        ),
    },
    ("Venus", 10): {
        "nature": _G,
        "description": (
            "Fond of low class women imprudent ambitious unprincipled licentious boastful "
            "subtle learned weak body."
        ),
    },
    ("Venus", 11): {
        "nature": _B,
        "description": (
            "Liked by all middle stature handsome affable; persuasive witty timid chaste calm "
            "helpful and humanitarian."
        ),
    },
    ("Venus", 12): {
        "nature": _B,
        "description": (
            "Witty tactful learned popular just ingenious caricaturist modest refined powerful "
            "exalted respected pleasure-seeking."
        ),
    },

    # ── Saturn ───────────────────────────────────────────────────────────────
    ("Saturn", 1): {
        "nature": _G,
        "description": (
            "Idiotic wanderer insincere peevish resentful cruel fraudulent immoral boastful "
            "quarrelsome gloomy mischievous perverse misunderstanding nature."
        ),
    },
    ("Saturn", 2): {
        "nature": _G,
        "description": (
            "Dark complexion deceitful successful powerful unorthodox clever likes solitude "
            "voracious eater persuasive cool contagious diseases; many wives; self-restraint "
            "worried nature."
        ),
    },
    ("Saturn", 3): {
        "nature": _G,
        "description": (
            "Wandering nature miserable untidy original thin subtle ingenious; strategic few "
            "children taste for chemical and mechanical sciences narrow-minded; speculative "
            "logical desperado."
        ),
    },
    ("Saturn", 4): {
        "nature": _G,
        "description": (
            "Poor weak teeth pleasure-seeking few sons cheeks full slow dull cunning rich "
            "selfish deceitful malicious stubborn devoid of motherly care."
        ),
    },
    ("Saturn", 5): {
        "nature": _G,
        "description": (
            "Middle stature severe obstinate few sons stubborn unfortunate conflicting hard "
            "worker good writer evil-minded."
        ),
    },
    ("Saturn", 6): {
        "nature": _G,
        "description": (
            "Dark complexion malicious poor quarrelsome erratic narrow-minded rude conservative "
            "taste for public life weak health."
        ),
    },
    ("Saturn", 7): {
        "nature": _G,
        "description": (
            "Famous founder of institutions and the like; rich; tall fair self-conceited "
            "handsome tactful powerful respected sound judgment antagonistic independent proud "
            "prominent; charitable subservient to females."
        ),
    },
    ("Saturn", 8): {
        "nature": _G,
        "description": (
            "Rash; indifferent hard-hearted adventurous petty self-conceited reserved "
            "unscrupulous violent unhappy; danger from poisons fire and weapons wasteful "
            "unhealthy."
        ),
    },
    ("Saturn", 9): {
        "nature": _G,
        "description": (
            "Pushful artful cunning famous peaceful faithful pretentious apparently generous "
            "troubles with wife courteous dutiful children generally happy."
        ),
    },
    ("Saturn", 10): {
        "nature": _G,
        "description": (
            "Intelligent harmony and felicity in domestic life selfish covetous peevish "
            "intellectual learned suspicious reflective revengeful prudent melancholy "
            "inheritance from wife's parties."
        ),
    },
    ("Saturn", 11): {
        "nature": _B,
        "description": (
            "Practical able diplomatic ingenious a bit conceited prudent happy reflective "
            "intellectual philosophical vanquished by enemies."
        ),
    },
    ("Saturn", 12): {
        "nature": _B,
        "description": (
            "Clever pushful gifted polite happy good wife trustworthy scheming wealthy "
            "helpful."
        ),
    },
}

# The 7 planets covered by planet-in-sign data (no Rahu/Ketu in source)
_PLANETS = [
    Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
    Planet.Jupiter, Planet.Venus, Planet.Saturn,
]


def get_planet_in_sign_interpretation(birth_time: AstroTime, planet: Planet) -> dict:
    """Return the natal planet-in-sign interpretation for a single planet.

    Returns a dict with:
        - planet (str)
        - sign_num (int, 1-based)
        - sign_name (str)
        - nature (str: 'Good' | 'Bad')
        - description (str)
    """
    sign_num = get_planet_sign_num(planet, birth_time)
    sign_name = SIGN_NAMES[sign_num] if sign_num <= 12 else ""
    entry = _PLANET_IN_SIGN_DATA.get((planet.name, sign_num), {})
    return {
        "planet": planet.name,
        "sign_num": sign_num,
        "sign_name": sign_name,
        "nature": entry.get("nature", "Neutral"),
        "description": entry.get("description", ""),
    }


def get_all_planet_in_sign_interpretations(birth_time: AstroTime) -> List[dict]:
    """Return natal planet-in-sign interpretations for all 7 classical planets."""
    return [get_planet_in_sign_interpretation(birth_time, p) for p in _PLANETS]
