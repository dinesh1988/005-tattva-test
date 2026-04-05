"""Gochara (Transit) Predictions.

Gochara = planet transit counted from the natal Moon sign.
House = ((transit_sign - birth_moon_sign) % 12) + 1
Rules sourced from VedAstro C# EventDataListStatic.cs.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .time import AstroTime
from .consts import Planet
from .house_queries import get_planet_sign_num

# ---------------------------------------------------------------------------
# Data table: (planet_name, house_num) -> {nature, life_areas, description}
# nature: "Good" | "Bad" | "Neutral"
# life_areas: dict of Mind/Studies/Family/Money/Love/Body -> nature string
# ---------------------------------------------------------------------------

_G = "Good"
_B = "Bad"
_N = "Neutral"


def _la(mind=_N, studies=_N, family=_N, money=_N, love=_N, body=_N):
    return {"Mind": mind, "Studies": studies, "Family": family,
            "Money": money, "Love": love, "Body": body}


_GOCHARA_DATA: Dict[Tuple[str, int], dict] = {
    # ── Sun ─────────────────────────────────────────────────────────────────
    ("Sun", 1): {
        "nature": _B,
        "life_areas": _la(money=_B, body=_B),
        "description": (
            "When the Sun traverses through the Rasi occupied by the Moon, "
            "the person suffers from loss of wealth, loss of prestige, sickness "
            "and will have many obstacles and aimless travels. Financial loss, "
            "discomfort, chest pain and aimless journey."
        ),
    },
    ("Sun", 2): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_B),
        "description": (
            "When he transits in the 2nd house, there will be loss of wealth, "
            "he will suffer deceit, he will have full of financial worries. "
            "Increase of expenditure, eye trouble, deceit and unhappiness."
        ),
    },
    ("Sun", 3): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G, body=_G),
        "description": (
            "In the 3rd house there will be advent of money, happiness, relief "
            "from diseases, recognition from superiors, honours and courage. "
            "Increase of emoluments, freedom from sickness and destruction of enemies."
        ),
    },
    ("Sun", 4): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, money=_B, love=_B, body=_B),
        "description": (
            "In the 4th house, there will be diseases, constant attacks from "
            "opponents, no peace of mind, pressure from creditors, and sorrow "
            "and misery. Quarrels with wife, unhappiness in conjugal life and "
            "the general ailments."
        ),
    },
    ("Sun", 5): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, love=_B, body=_B),
        "description": (
            "The Sun transiting the 5th will cause mental agitation, ill-health, "
            "embarrassment and accidents. Increase of enemies and physical indisposition."
        ),
    },
    ("Sun", 6): {
        "nature": _G,
        "life_areas": _la(mind=_G, family=_G, body=_G),
        "description": (
            "The Sun in the 6th gives rise to release from sorrows, worries and "
            "troubles, destruction of enemies and peace of mind. Success over "
            "enemies, joy and good health."
        ),
    },
    ("Sun", 7): {
        "nature": _B,
        "life_areas": _la(body=_B),
        "description": (
            "The Sun transiting the 7th produces wearisome travelling, colic and "
            "anal troubles, humiliation and sickness. Wearisome travelling, chest "
            "pain and stomach troubles."
        ),
    },
    ("Sun", 8): {
        "nature": _B,
        "life_areas": _la(family=_B, love=_B, body=_B),
        "description": (
            "In the 8th, Sun's progress gives rise to quarrels with friends, "
            "diseases, high blood pressure, royal and official displeasure. "
            "Misunderstandings with or separation from wife."
        ),
    },
    ("Sun", 9): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, love=_B, body=_B),
        "description": (
            "The Sun's transit in the 9th house will cause to the native danger, "
            "humiliation, dependency, disappointment and separation. Accidents, "
            "stomach trouble, mental worry and opposition."
        ),
    },
    ("Sun", 10): {
        "nature": _G,
        "life_areas": _la(),
        "description": (
            "One will accomplish his desire and plans, and success will attend on "
            "all kinds of undertakings when the Sun is in the 10th. Success in "
            "endeavors, honour and realisation of ambition."
        ),
    },
    ("Sun", 11): {
        "nature": _G,
        "life_areas": _la(money=_G, body=_G),
        "description": (
            "In the 11th, the passage of the Sun will confer on a person honour, "
            "health, wealth and success. Great success, respect, freedom from "
            "disease and prosperity."
        ),
    },
    ("Sun", 12): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, money=_B, love=_B, body=_B),
        "description": (
            "When the Sun passes through the 12th house, there will be sorrow, "
            "creation of a situation which causes loss to everything, quarrels "
            "and ill-health."
        ),
    },
    # ── Moon ────────────────────────────────────────────────────────────────
    ("Moon", 1): {
        "nature": _G,
        "life_areas": _la(family=_G, body=_G),
        "description": (
            "When the Moon transits the sign occupied by her at the time of birth "
            "of a person, the native will get excellent food, bed and clothes. "
            "Good food, comforts and clothes."
        ),
    },
    ("Moon", 2): {
        "nature": _B,
        "life_areas": _la(money=_B),
        "description": (
            "When the Moon passes through the 2nd house, loss of respect and of "
            "money and obstacles in the way of success are to be predicted. Loss "
            "of respect, money and increase of obstacles."
        ),
    },
    ("Moon", 3): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G, love=_G),
        "description": (
            "In the 3rd house, the native gets clothes, pleasure from wife and "
            "finance. Domestic happiness and access to money."
        ),
    },
    ("Moon", 4): {
        "nature": _B,
        "life_areas": _la(mind=_B),
        "description": (
            "In the 4th, he becomes mentally uneasy. Loss of trust in others and "
            "lack of peace of mind."
        ),
    },
    ("Moon", 5): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, love=_B, body=_B),
        "description": (
            "In the 5th, suffers from humility, ill-health, pain of mind and "
            "other obstacles. Indisposition, grief and disappointment."
        ),
    },
    ("Moon", 6): {
        "nature": _G,
        "life_areas": _la(money=_G, love=_G, body=_G),
        "description": (
            "In the 6th, enjoys wealth, health, comfort, redemption from enemies. "
            "Happiness, success over enemies and good health."
        ),
    },
    ("Moon", 7): {
        "nature": _G,
        "life_areas": _la(money=_G),
        "description": (
            "7th house, conveyances, good food and financial equilibrium. Respect "
            "from others and sudden influx of unexpected resources."
        ),
    },
    ("Moon", 8): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, love=_B, body=_B),
        "description": (
            "The Moon transiting the 8th produces misery, ill-health and fear "
            "from unexpected sources. Apprehension, uneasiness and worry."
        ),
    },
    ("Moon", 9): {
        "nature": _B,
        "life_areas": _la(mind=_B, body=_B),
        "description": (
            "In the 9th from herself, pain of mind, chest pain, fatigue of body "
            "and the like are caused. Mental pain, stomach trouble and incarceration."
        ),
    },
    ("Moon", 10): {
        "nature": _G,
        "life_areas": _la(),
        "description": (
            "When the Moon passes through the 10th house, success will attend in "
            "every sphere of activity. Success, authority and position, realisation "
            "of ambition."
        ),
    },
    ("Moon", 11): {
        "nature": _G,
        "life_areas": _la(money=_G),
        "description": (
            "In the 11th house, the person will enjoy prosperity, will get wealth "
            "and new friends. Prosperity, new friends and good income."
        ),
    },
    ("Moon", 12): {
        "nature": _B,
        "life_areas": _la(money=_B, body=_B),
        "description": (
            "When the Moon transits through the 12th sign. He suffers from "
            "accidents and injuries. Injuries due to fall from vehicles and "
            "increased expenditure."
        ),
    },
    # ── Mars ────────────────────────────────────────────────────────────────
    ("Mars", 1): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, love=_B, body=_B),
        "description": (
            "When Mars passes through the sign occupied by the Moon at the time "
            "of birth of a person, he will suffer from troubles. Troubles from "
            "various sources and bodily affliction."
        ),
    },
    ("Mars", 2): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_B, body=_B),
        "description": (
            "In the 2nd house from the Moon displeasure of king, and suffering "
            "from quarrels, from enemies and disgrace is indicated. There will be "
            "fear from thieves and the body will be afflicted with bilious and "
            "windy complaints. Trouble from the Government, frequent quarrels with "
            "enemies, disease, accidents, bilious and windy complaints and loss "
            "by theft."
        ),
    },
    ("Mars", 3): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G, body=_G),
        "description": (
            "Mars transiting the 3rd gives rise to gain of objects, pleasure from "
            "children, good health, access to riches and new clothes. Benefits "
            "through auspicious characters, financial improvement and acquisition "
            "of woolen articles and also authority."
        ),
    },
    ("Mars", 4): {
        "nature": _B,
        "life_areas": _la(body=_B),
        "description": (
            "In the 4th sign, Mars produces evil results such as fever, digestive "
            "troubles, blood discharges and depravity of character. Fever, "
            "stomachache, piles and blood discharges and frequent trouble from ailments."
        ),
    },
    ("Mars", 5): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, body=_B),
        "description": (
            "Enemies will increase, fresh diseases will make their appearance and "
            "mental peace will be completely absent when Mars passes through the "
            "5th house. Trouble from enemies, illness, misunderstandings with "
            "children and loss of physical energy."
        ),
    },
    ("Mars", 6): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G),
        "description": (
            "In the 6th house, relief from troubles, worries and ill-health should "
            "be predicted; he leads an independent life, obtains riches and becomes "
            "pretty cheerful. Success over enemies, termination of strife in the "
            "family, and acquisition of self-confidence."
        ),
    },
    ("Mars", 7): {
        "nature": _B,
        "life_areas": _la(family=_B, love=_B, body=_B),
        "description": (
            "When transiting the 7th, the native quarrels with wife or husband, "
            "eye troubles, stomach-ache, indigestion, etc., are also likely to be "
            "felt. Frequent quarrels with wife, eye trouble and stomachache."
        ),
    },
    ("Mars", 8): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, money=_B, love=_B, body=_B),
        "description": (
            "Mars transiting in the 8th produces quite unfavorable effects, such "
            "as discharging of blood, loss of wealth, disgrace and mental worry. "
            "Loss of blood from piles and anemia and loss of wealth and name."
        ),
    },
    ("Mars", 9): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, money=_B, body=_B),
        "description": (
            "Mars transiting in the 9th produces quite unfavorable effects, such "
            "as discharging of blood, loss of wealth, disgrace and mental worry. "
            "In addition, the subject becomes extremely weak. Suffering from insults, "
            "heavy expenditure and weakness due to ill-health."
        ),
    },
    ("Mars", 10): {
        "nature": _G,
        "life_areas": _la(money=_G),
        "description": (
            "His transiting the 10th produces quite favourable results. Amounts "
            "due will be realised. Success will attend on his ventures. Business "
            "will improve. Acquisition of money from unexpected source."
        ),
    },
    ("Mars", 11): {
        "nature": _G,
        "life_areas": _la(money=_G),
        "description": (
            "His transiting the 11th produces quite favourable results. Amounts "
            "due will be realised. Business will improve. Fame, reputation and authority."
        ),
    },
    ("Mars", 12): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_B, love=_B, body=_B),
        "description": (
            "In the 12th house, however, he will suffer from various expenses, "
            "troubles, diseases of the eye, pinpricks from an angry wife, from "
            "bilious complaints and various other worries. Unforeseen expenses, "
            "quarrels with wife, eye disease and bilious affections."
        ),
    },
    # ── Mercury ─────────────────────────────────────────────────────────────
    ("Mercury", 1): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_B),
        "description": (
            "When Mercury passes through the sign occupied by the Moon at time of "
            "birth of a person, such person will suffer loss of wealth caused by "
            "the advice of wicked men, by talebearers, by imprisonment and quarrels. "
            "He will, besides, receive disagreeable intelligence when in his journey. "
            "Loss of money due to advice by wicked men, worry due to association "
            "with tale-bearers, quarrels, imprisonment and disagreeable news while "
            "travelling."
        ),
    },
    ("Mercury", 2): {
        "nature": _G,
        "life_areas": _la(family=_B, money=_G),
        "description": (
            "When Mercury passes through the 2nd house, the person will suffer "
            "disgrace but gains success and wealth. Disgrace, ill-treatment from "
            "relatives but acquisition of success and wealth."
        ),
    },
    ("Mercury", 3): {
        "nature": _B,
        "life_areas": _la(),
        "description": (
            "When he passes through the 3rd house, the subject will get friends, "
            "will be afraid of troubles from the king and from his enemies, he "
            "will quit his place due to his wicked deeds. New friends, but "
            "anticipation of trouble from government and enemies, aimless roaming "
            "about due to misdeeds."
        ),
    },
    ("Mercury", 4): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G),
        "description": (
            "When Mercury passes through the 4th house, the person's kinsmen and "
            "family will increase and there will be much gain. Prosperity for "
            "relatives and family members, addition to family and gain of money."
        ),
    },
    ("Mercury", 5): {
        "nature": _B,
        "life_areas": _la(family=_B, love=_B),
        "description": (
            "In the 5th house, the person will quarrel with his wife and sons and "
            "will not enjoy the company of an excellent wife. Quarrels with wife "
            "and children."
        ),
    },
    ("Mercury", 6): {
        "nature": _G,
        "life_areas": _la(),
        "description": (
            "In the 6th house, the person will be liked by all and will gain "
            "renown. Gain of renown, success and popularity."
        ),
    },
    ("Mercury", 7): {
        "nature": _B,
        "life_areas": _la(family=_B, body=_B),
        "description": (
            "In the 7th house, the person's appearance becomes less bright and "
            "there will be quarrels. Bloodlessness, quarrels and mental uneasiness."
        ),
    },
    ("Mercury", 8): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G),
        "description": (
            "When Mercury passes through the 8th house, the person will get sons, "
            "success, clothes and wealth and will become happy and powerful. Birth "
            "of an issue, success, happiness and acquisition of new articles."
        ),
    },
    ("Mercury", 9): {
        "nature": _B,
        "life_areas": _la(mind=_B),
        "description": (
            "When he passes through the 9th house from the Moon, the person will "
            "meet with obstacles in his work. Obstacles and mental worry."
        ),
    },
    ("Mercury", 10): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G, love=_G),
        "description": (
            "In the 10th house, the person's enemies will meet with ruin and the "
            "person will get wealth, will enjoy the company of his wife and will "
            "be dressed in the flannel. Defeat of enemies, acquisition of money, "
            "happiness with wife and agreeable company."
        ),
    },
    ("Mercury", 11): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G),
        "description": (
            "When Mercury passes through the 11th house from the Moon, the person "
            "will get wealth, comfort, sons, women, friends and conveyance and will "
            "be happy and will receive good intelligence. Acquisition of wealth; "
            "birth of a son and happiness."
        ),
    },
    ("Mercury", 12): {
        "nature": _B,
        "life_areas": _la(family=_B, love=_B, body=_B),
        "description": (
            "In the 12th, the person will suffer disgrace from his enemies, will "
            "suffer from diseases and will not enjoy the company of a good wife. "
            "Disgrace from enemies, disease and domestic disharmony."
        ),
    },
    # ── Jupiter ─────────────────────────────────────────────────────────────
    ("Jupiter", 1): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, money=_B),
        "description": (
            "When Jupiter passes through the sign occupied by the Moon at the time "
            "of birth of a person, such person will lose his wealth and intelligence, "
            "will quit his place and will suffer from many quarrels. Loss of money "
            "and intelligence, aimless roaming about and frequent quarrels."
        ),
    },
    ("Jupiter", 2): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G, love=_G),
        "description": (
            "When Jupiter passes through the 2nd house from the Moon, the person "
            "will have no enemies and will enjoy wealth and women. Happiness, "
            "domestic harmony and success over enemies."
        ),
    },
    ("Jupiter", 3): {
        "nature": _B,
        "life_areas": _la(money=_B),
        "description": (
            "When Jupiter passes through the 3rd house from the Moon, the person "
            "will quit his place and will meet with obstacles in his work. Moving "
            "about from place to place, obstacles to own work and loss of position."
        ),
    },
    ("Jupiter", 4): {
        "nature": _B,
        "life_areas": _la(family=_B),
        "description": (
            "When Jupiter passes through the 4th house from the Moon, the person "
            "will suffer from troubles caused by his kinsmen, will become patient "
            "and resigned and will delight in nothing. Troubles from relatives, "
            "development of a sense of resignation to the inevitable."
        ),
    },
    ("Jupiter", 5): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G),
        "description": (
            "When Jupiter passes through the 5th house from the Moon, the person "
            "will get servants, prosperity, sons, elephants, houses, bullocks, "
            "gold, women, clothes, gems and good qualities. Acquisition of servants, "
            "birth of a son, general prosperity, addition of property and "
            "development of good qualities."
        ),
    },
    ("Jupiter", 6): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, love=_B),
        "description": (
            "When Jupiter passes through the 6th house from the Moon, the person "
            "will be so much afflicted at heart that he will take no delight in "
            "agreeable things. Affliction of mind, friends turning enemies and "
            "indifferent to good things."
        ),
    },
    ("Jupiter", 7): {
        "nature": _G,
        "life_areas": _la(money=_G, love=_G),
        "description": (
            "When Jupiter passes through the 7th house from the Moon, the person "
            "will enjoy good bed, the company of an excellent woman, wealth, good "
            "meals, flowers, conveyance and the like. Happiness, erotic pleasure, "
            "good income, purchase of a conveyance and graceful speech."
        ),
    },
    ("Jupiter", 8): {
        "nature": _B,
        "life_areas": _la(family=_B, body=_B),
        "description": (
            "When Jupiter passes through the 8th house from the Moon, the person "
            "will suffer from imprisonment, diseases, heavy grief, the fatigue of "
            "journey and serious illness. Imprisonment, disease, heavy grief and "
            "serious illness."
        ),
    },
    ("Jupiter", 9): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G),
        "description": (
            "When Jupiter passes through the 9th house from the Moon, the person "
            "will become efficient at work and influential and he will get sons, "
            "success in work, wealth and gain. Influential, birth of an issue, "
            "success in work and acquisition of wealth from an unexpected source."
        ),
    },
    ("Jupiter", 10): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_B, body=_B),
        "description": (
            "When Jupiter passes through the 10th house from the Moon, the person "
            "will quit his place and suffer loss of health and wealth. Destruction "
            "of position, loss of money and health and aimless roaming about."
        ),
    },
    ("Jupiter", 11): {
        "nature": _G,
        "life_areas": _la(money=_G, body=_G),
        "description": (
            "When Jupiter passes through the 11th house, the person will return to "
            "his country and will recover his health and wealth. Reinstatement in "
            "former position, and recovery of health."
        ),
    },
    ("Jupiter", 12): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, love=_B),
        "description": (
            "When Jupiter passes through the 12th house, the person will suffer "
            "grief in his return journey. Fall from ideals and right conduct and "
            "increase of grief."
        ),
    },
    # ── Venus ───────────────────────────────────────────────────────────────
    ("Venus", 1): {
        "nature": _G,
        "life_areas": _la(love=_G, body=_G),
        "description": (
            "When Venus passes through the sign occupied by the Moon at the time "
            "of birth of a person, such a person will enjoy excellent perfumes, "
            "flowers, clothes, houses, bed, meals and women. Acquisition of "
            "comforts for pleasure, and a happy life."
        ),
    },
    ("Venus", 2): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G, love=_G),
        "description": (
            "When Venus passes through the 2nd house from the Moon, the person "
            "will get sons, wealth, grain and presents from the king; will have a "
            "prosperous family, will enjoy flowers and gems and will be of bright "
            "appearance. Acquisition of money and gifts, birth of an issue and "
            "erotic pleasure."
        ),
    },
    ("Venus", 3): {
        "nature": _G,
        "life_areas": _la(money=_G),
        "description": (
            "When Venus passes through the 3rd house from the Moon, the person "
            "will become influential, wealthy and respectable and will get clothes. "
            "His enemies will meet with ruin. Influence, wealth and respect."
        ),
    },
    ("Venus", 4): {
        "nature": _G,
        "life_areas": _la(),
        "description": (
            "When Venus passes through the 4th house, the person will get friends "
            "and will become greatly powerful. Disgrace to enemies and general "
            "prosperity."
        ),
    },
    ("Venus", 5): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G),
        "description": (
            "When Venus passes through the 5th house, the person will be happy, "
            "will get kinsmen, sons, wealth and friends and will not suffer defeat "
            "by the enemy. Renewal of contact with friends, increase of reputation, "
            "influence and power."
        ),
    },
    ("Venus", 6): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_G, body=_B),
        "description": (
            "When Venus passes through the 6th house from the Moon, the person "
            "will suffer disgrace, will be afflicted with diseases and will be "
            "exposed to danger. General happiness, extension of business, birth "
            "of an issue and good income."
        ),
    },
    ("Venus", 7): {
        "nature": _B,
        "life_areas": _la(family=_B, love=_B, body=_B),
        "description": (
            "When Venus passes through the 7th house, the person will suffer "
            "injuries through women. Humiliation, disease and danger."
        ),
    },
    ("Venus", 8): {
        "nature": _G,
        "life_areas": _la(mind=_B, love=_B),
        "description": (
            "When Venus passes through the 8th house from the Moon, the person "
            "will get houses, articles of lacquer and beautiful women. Injuries "
            "and trouble from women and mental worry."
        ),
    },
    ("Venus", 9): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G, love=_G),
        "description": (
            "When Venus passes through the 9th house from the Moon, the person "
            "will become virtuous, happy and wealthy and he will get plenty of "
            "clothes. Acquisition of a new house, articles of luxury and wife "
            "if not married."
        ),
    },
    ("Venus", 10): {
        "nature": _B,
        "life_areas": _la(),
        "description": (
            "When Venus passes through the 10th house from the Moon, the person "
            "will suffer disgrace and will also suffer quarrels. Increase of virtue, "
            "happiness, wealth and performance of religious acts."
        ),
    },
    ("Venus", 11): {
        "nature": _G,
        "life_areas": _la(money=_G),
        "description": (
            "When Venus passes through the 11th house from the Moon, the person "
            "will get wealth of his friends and will also get perfumes and clothes."
        ),
    },
    ("Venus", 12): {
        "nature": _B,
        "life_areas": _la(money=_B, body=_B),
        "description": (
            "When Venus passes through the 12th house, the person will get very "
            "few clothes. Acquisition of new friends, money, perfumes and clothes."
        ),
    },
    # ── Saturn ──────────────────────────────────────────────────────────────
    ("Saturn", 1): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_B),
        "description": (
            "When Saturn passes through the sign occupied by the Moon at the time "
            "of his birth, such person will suffer from poison and from fire, will "
            "quit his kinsmen, will suffer from imprisonment and torture, will "
            "travel to foreign lands and live with his friend there, will suffer "
            "miseries, loss of wealth and of sons, will suffer also from the fatigues "
            "of foot journey and from humiliation. Fear from poison or fire, of "
            "friends and family members, fear of incarceration, travel to foreign "
            "lands, loss of money and near relatives, separation from kith and kin "
            "and suffering from insults."
        ),
    },
    ("Saturn", 2): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_B, body=_B),
        "description": (
            "When Saturn passes through the 2nd house from the Moon, the person "
            "will suffer from loss of beauty and comfort, will become weak and will "
            "get wealth from other men but will not enjoy this wealth long. "
            "Emaciated physical appearance, loss of comfort, acquisition but not "
            "enjoyment of wealth."
        ),
    },
    ("Saturn", 3): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G, body=_G),
        "description": (
            "When Saturn passes through the 3rd house from the Moon, the person "
            "will get wealth, servants, articles of enjoyment, camels, buffaloes, "
            "elephants, asses and horses. He will become influential, happy, free "
            "from disease and will become greatly powerful and will defeat his "
            "enemies in fight. Increase of wealth and other comforts, good health, "
            "general happiness and disappearance of enemies."
        ),
    },
    ("Saturn", 4): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, money=_B, love=_B),
        "description": (
            "When Saturn passes through the 4th house from the Moon, the person "
            "will be separated from his friends, wealth, and wife and ever "
            "suspecting evil in everything, will never feel happy. Separation from "
            "friends and family members, suspicious nature, crooked behaviour and "
            "wicked acts."
        ),
    },
    ("Saturn", 5): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_B),
        "description": (
            "When Saturn passes through the 5th house from the Moon, the person "
            "will be separated from his sons and wealth and will suffer from "
            "quarrels. Separation from sons, loss of money and frequent quarrels."
        ),
    },
    ("Saturn", 6): {
        "nature": _G,
        "life_areas": _la(love=_G, body=_G),
        "description": (
            "When Saturn passes through the 6th house from the Moon, the person "
            "will be freed from his enemies and diseases and will enjoy the company "
            "of women. Freedom from enemies and diseases, association with fair sex."
        ),
    },
    ("Saturn", 7): {
        "nature": _B,
        "life_areas": _la(family=_B, love=_B),
        "description": (
            "When Saturn passes through the 7th house from the Moon, the person "
            "will be separated from his wife and sons, will travel on foot in a "
            "pitiable condition. Separation from wife and children and aimless "
            "roaming about."
        ),
    },
    ("Saturn", 8): {
        "nature": _B,
        "life_areas": _la(family=_B, love=_B),
        "description": (
            "When Saturn passes through the 8th house from the Moon, the person "
            "will be separated from his wife and sons, will travel on foot in a "
            "pitiable condition. Indulgence in mean activities and bereft of "
            "happiness."
        ),
    },
    ("Saturn", 9): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, love=_B, body=_B),
        "description": (
            "When he passes through the 9th house, the person will be separated "
            "from his wife and sons, will travel on foot in a pitiable condition. "
            "Suffers from hatred, heart trouble and even imprisonment."
        ),
    },
    ("Saturn", 10): {
        "nature": _B,
        "life_areas": _la(money=_B),
        "description": (
            "When Saturn passes through the 10th house, the person will get work "
            "and will suffer loss of wealth, learning and fame. Gets new avocation, "
            "but loses money and fame."
        ),
    },
    ("Saturn", 11): {
        "nature": _G,
        "life_areas": _la(money=_B, love=_B),
        "description": (
            "When Saturn passes through the 11th house from the Moon, the person "
            "will become cruel and will get women and wealth. Frequent loss of "
            "temper but acquisition of wealth through wrong means."
        ),
    },
    ("Saturn", 12): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, body=_B),
        "description": (
            "When Saturn passes through the 12th house from the Moon, the person "
            "will suffer from much grief. Grief, series of miseries, ill-health "
            "and general affliction."
        ),
    },
    # ── Rahu ────────────────────────────────────────────────────────────────
    ("Rahu", 1): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, money=_B, body=_B),
        "description": (
            "When Rahu passes through the sign occupied by the Moon at the time "
            "of his birth, such person will suffer from poison and from fire, "
            "will quit his kinsmen, will suffer from imprisonment and torture, "
            "will travel to foreign lands and live with his friend there, will "
            "suffer miseries, loss of wealth and of sons, will suffer also from "
            "the fatigues of foot journey and from humiliation."
        ),
    },
    ("Rahu", 2): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_B, body=_B),
        "description": (
            "When Rahu passes through the 2nd house from the Moon, the person "
            "will suffer from loss of beauty and comfort, will become weak and "
            "will get wealth from other men but will not enjoy this wealth long."
        ),
    },
    ("Rahu", 3): {
        "nature": _G,
        "life_areas": _la(money=_G),
        "description": (
            "When Rahu passes through the 3rd house from the Moon, the person "
            "will get wealth, servants, articles of enjoyment, camels, buffaloes, "
            "elephants, asses and horses. He will become influential, happy, free "
            "from disease and will become greatly powerful and will defeat his "
            "enemies in fight."
        ),
    },
    ("Rahu", 4): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, money=_B, love=_B),
        "description": (
            "When Rahu passes through the 4th house from the Moon, the person "
            "will be separated from his friends, wealth, and wife and ever "
            "suspecting evil in everything, will never feel happy."
        ),
    },
    ("Rahu", 5): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_B),
        "description": (
            "When Rahu passes through the 5th house from the Moon, the person "
            "will be separated from his sons and wealth and will suffer from "
            "quarrels."
        ),
    },
    ("Rahu", 6): {
        "nature": _G,
        "life_areas": _la(love=_G),
        "description": (
            "When Rahu passes through the 6th house from the Moon, the person "
            "will be freed from his enemies and diseases and will enjoy the "
            "company of women."
        ),
    },
    ("Rahu", 7): {
        "nature": _B,
        "life_areas": _la(family=_B, love=_B),
        "description": (
            "When Rahu passes through the 7th or 8th house from the Moon, the "
            "person will be separated from his wife and sons, will travel on foot "
            "in a pitiable condition."
        ),
    },
    ("Rahu", 8): {
        "nature": _B,
        "life_areas": _la(family=_B, love=_B),
        "description": (
            "When Rahu passes through the 7th or 8th house from the Moon, the "
            "person will be separated from his wife and sons, will travel on foot "
            "in a pitiable condition."
        ),
    },
    ("Rahu", 9): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, love=_B, body=_B),
        "description": (
            "When he passes through the 9th house, the person will be separated "
            "from his wife and sons, will travel on foot in a pitiable condition. "
            "Besides that, suffer from hatred, chest pain, imprisonment and in "
            "consequence will not properly observe the daily duties."
        ),
    },
    ("Rahu", 10): {
        "nature": _B,
        "life_areas": _la(studies=_B, money=_B),
        "description": (
            "When Rahu passes through the 10th house, the person will get work "
            "and will suffer loss of wealth, learning and fame."
        ),
    },
    ("Rahu", 11): {
        "nature": _G,
        "life_areas": _la(money=_B, love=_B),
        "description": (
            "When Rahu passes through the 11th house from the Moon, the person "
            "will become cruel and will get women and wealth."
        ),
    },
    ("Rahu", 12): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B),
        "description": (
            "When Rahu passes through the 12th house from the Moon, the person "
            "will suffer from much grief."
        ),
    },
    # ── Ketu ────────────────────────────────────────────────────────────────
    ("Ketu", 1): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, love=_B, body=_B),
        "description": (
            "When Ketu passes through the sign occupied by the Moon at the time "
            "of birth of a person, he will suffer from troubles."
        ),
    },
    ("Ketu", 2): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, body=_B),
        "description": (
            "In the 2nd house from the Moon displeasure of king, and suffering "
            "from quarrels, from enemies and disgrace is indicated. There will be "
            "fear from thieves and the body will be afflicted with bilious and "
            "windy complaints."
        ),
    },
    ("Ketu", 3): {
        "nature": _G,
        "life_areas": _la(family=_G, money=_G, body=_G),
        "description": (
            "Ketu transiting the 3rd gives rise to gain of objects, pleasure from "
            "children, good health, access to riches and new clothes."
        ),
    },
    ("Ketu", 4): {
        "nature": _B,
        "life_areas": _la(body=_B),
        "description": (
            "In the 4th sign, Ketu produces evil results such as fever, digestive "
            "troubles, blood discharges and depravity of character."
        ),
    },
    ("Ketu", 5): {
        "nature": _B,
        "life_areas": _la(mind=_B, body=_B),
        "description": (
            "Enemies will increase, fresh diseases will make their appearance and "
            "mental peace will be completely absent when Ketu passes through the "
            "5th house."
        ),
    },
    ("Ketu", 6): {
        "nature": _G,
        "life_areas": _la(money=_G),
        "description": (
            "In the 6th house, relief from troubles, worries and ill-health should "
            "be predicted; he leads an independent life, obtains riches and becomes "
            "pretty cheerful."
        ),
    },
    ("Ketu", 7): {
        "nature": _B,
        "life_areas": _la(family=_B, love=_B, body=_B),
        "description": (
            "When transiting the 7th, the native quarrels with wife or husband, "
            "eye troubles, stomach-ache, indigestion, etc., are also likely to be "
            "felt."
        ),
    },
    ("Ketu", 8): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, money=_B, body=_B),
        "description": (
            "Ketu transiting in the 8th produces quite unfavorable effects, such "
            "as discharging of blood, loss of wealth, disgrace and mental worry."
        ),
    },
    ("Ketu", 9): {
        "nature": _B,
        "life_areas": _la(mind=_B, family=_B, money=_B, body=_B),
        "description": (
            "Ketu transiting in the 9th produces quite unfavorable effects, such "
            "as discharging of blood, loss of wealth, disgrace and mental worry. "
            "In addition, the subject becomes extremely weak."
        ),
    },
    ("Ketu", 10): {
        "nature": _G,
        "life_areas": _la(money=_G),
        "description": (
            "His transiting the 10th produces quite favourable results. Amounts "
            "due will be realised. Success will attend on his ventures. Business "
            "will improve."
        ),
    },
    ("Ketu", 11): {
        "nature": _G,
        "life_areas": _la(money=_G),
        "description": (
            "His transiting the 11th produces quite favourable results. Amounts "
            "due will be realised. Business will improve."
        ),
    },
    ("Ketu", 12): {
        "nature": _B,
        "life_areas": _la(family=_B, money=_B, love=_B, body=_B),
        "description": (
            "In the 12th house, however, he will suffer from various expenses, "
            "troubles, diseases of the eye, pinpricks from an angry wife, from "
            "bilious complaints and various other worries."
        ),
    },
}

# Planets for which we compute gochara (all 9 grahas)
_GOCHARA_PLANETS: List[Planet] = [
    Planet.Sun,
    Planet.Moon,
    Planet.Mars,
    Planet.Mercury,
    Planet.Jupiter,
    Planet.Venus,
    Planet.Saturn,
    Planet.Rahu,
    Planet.Ketu,
]


# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------

def get_gochara_house(birth_time: AstroTime, transit_time: AstroTime, planet: Planet) -> int:
    """Return the gochara house number (1–12) for *planet* at *transit_time*.

    The house is counted from the natal Moon sign:
        house = ((transit_sign - birth_moon_sign) % 12) + 1
    """
    birth_moon_sign = get_planet_sign_num(Planet.Moon, birth_time)   # 1-based
    transit_sign = get_planet_sign_num(planet, transit_time)          # 1-based
    return ((transit_sign - birth_moon_sign) % 12) + 1


def get_gochara_prediction(birth_time: AstroTime, transit_time: AstroTime, planet: Planet) -> dict:
    """Return the gochara prediction dict for a single planet."""
    house = get_gochara_house(birth_time, transit_time, planet)
    key = (planet.name, house)
    data = _GOCHARA_DATA.get(key)
    if data is None:
        return {
            "planet": planet.name,
            "gochara_house": house,
            "nature": _N,
            "life_areas": _la(),
            "description": f"No data for {planet.name} in house {house}.",
        }
    return {
        "planet": planet.name,
        "gochara_house": house,
        "nature": data["nature"],
        "life_areas": data["life_areas"],
        "description": data["description"].strip(),
    }


def get_gochara_predictions(birth_time: AstroTime, transit_time: AstroTime) -> List[dict]:
    """Return gochara predictions for all 9 planets at *transit_time*.

    Each entry contains:
        planet, gochara_house, nature, life_areas, description
    """
    return [
        get_gochara_prediction(birth_time, transit_time, planet)
        for planet in _GOCHARA_PLANETS
    ]


def get_gochara_summary(birth_time: AstroTime, transit_time: AstroTime) -> dict:
    """High-level summary: good/bad/neutral counts and overall score."""
    predictions = get_gochara_predictions(birth_time, transit_time)
    counts = {_G: 0, _B: 0, _N: 0}
    for p in predictions:
        counts[p["nature"]] = counts.get(p["nature"], 0) + 1
    score = counts[_G] - counts[_B]
    if score > 2:
        overall = _G
    elif score < -2:
        overall = _B
    else:
        overall = _N
    return {
        "good_count": counts[_G],
        "bad_count": counts[_B],
        "neutral_count": counts[_N],
        "net_score": score,
        "overall": overall,
    }
