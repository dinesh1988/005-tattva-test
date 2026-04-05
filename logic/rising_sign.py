"""Rising Sign (Lagna / Ascendant) Predictions.

For each of the 12 rising signs this module provides the classical Vedic
interpretation covering mental tendencies, physical tendencies, and general
life tendencies.  Sourced from VedAstro C# HoroscopeDataListStatic.cs
(EventTag.RisingSign, EventTag.Personal).

Lookup key: sign_num (int, 1-based, Aries=1 … Pisces=12) -> dict
"""

from __future__ import annotations

from typing import Dict, List

from .time import AstroTime
from .calculate import get_lagnam

# ---------------------------------------------------------------------------
# Sign name helpers
# ---------------------------------------------------------------------------

SIGN_NAMES: List[str] = [
    "", "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# ---------------------------------------------------------------------------
# Data table: sign_num (1-12) -> description
# ---------------------------------------------------------------------------

_RISING_SIGN_DATA: Dict[int, str] = {
    1: (
        "Mental Tendencies: Independent thinking courageous and sensitive. "
        "Physical Tendencies: Middle stature ruddy complexion sharp sight long face and neck head broad "
        "at the temples and narrow at chin brown or light and curly mark or scar on the head or temples "
        "teeth well-set and round eyes. "
        "General Tendencies: Those born in Mesha are lovers of scientific thought. They are enterprising "
        "and ambitious. They have the ability to plan. They dislike being guided by others are intense "
        "when interested vehement when excited. They are rather stubborn but often frank. Quick tempered "
        "they resent imposition and are liable to go to extremes. Their constitution will be hot. They "
        "love beauty art and elegance. They have practical ideas. If Aries is afflicted they suffer from "
        "diseases pertaining to the head. Mental affliction and derangement are also likely if Saturn and "
        "the Moon are in Aries."
    ),
    2: (
        "Mental Tendencies: Obstinate proud and ambitious easily accessible to adulation but affectionate "
        "and loving sometimes unreasonable prejudiced and stubborn. "
        "Physical Tendencies: The stature of the person born in this sign will be short and often tending "
        "towards corpulence lips thick and complexion swarthy square build of the body. Face beautiful "
        "eyes and ears large full forehead hands plump and broad. "
        "General Tendencies: If they are not listened to attentively people born in this sign will act "
        "like a bull. They are self-reliant. They have their own principles and ways and a piercing "
        "intellect. They have a great deal of endurance latent power and energy. They always put their "
        "ideas into practice. Their physical powers and mental endurance are indeed noteworthy. They are "
        "fond of pleasure they love beauty and music. They possess a magnetic personality. They think they "
        "are born for exercising authority. They generally suffer from nervous complaints after the "
        "fiftieth year. With regard to children much happiness is not indicated."
    ),
    3: (
        "Mental Tendencies: They will have a wavering mind. Fond of writing and reading they are ingenious "
        "and quickwitted vivacious and inconsistent nervous and restless. "
        "Physical Tendencies: They are tall and straight in stature and active in motion. Face well "
        "developed there is a depression near the chin a thin face sanguine complexion unusual height "
        "if malefics are there the eyes are clear and the nose snub. They are weak but active. "
        "General Tendencies: They are very active and tend to become experts in mechanical sciences. They "
        "may suffer sudden nervous breakdowns. They must be cautious in moving with the opposite sex. "
        "Their mind will be often conscious of their own depravity. They are very clever and possess "
        "inherent conversational and literary ability. They are liable to fraud and deception. If evil "
        "planets are in Gemini trickery and deceit will characterize their nature. They are best in "
        "occupations where there is much activity."
    ),
    4: (
        "Mental Tendencies: People born in this sign will be extremely sensitive inquisitive nervous and "
        "restless interested in music and dexterous. "
        "Physical Tendencies: They have a middle sized body face full slightly snub nose fair complexion "
        "long arms long face and wide chest. "
        "General Tendencies: They are very intelligent bright and extremely frugal and equally "
        "industrious. Their frugality often takes the form of miserliness. The mind is intuitional "
        "perceptive. They like pleasure. They are deeply attached to their family and children. They "
        "often meet with disappointment in love affairs. They are very talkative self-reliant honest and "
        "unbending. They will have a reputation for love of justice and fairplay. Their emotions are "
        "strong. They have psychic tendencies are receptive to new ideas and adapt themselves to "
        "environment. They are desirous of possessions and cautious. They can best take up occupations "
        "of a fluctuating nature."
    ),
    5: (
        "Mental Tendencies: People born in Leo are ambitious as well as avaricious warm-hearted and have "
        "a liking for art literature and music. They are cheerful and unimpulsive. "
        "Physical Tendencies: Persons born in this sign will be magnetic in appearance with broad "
        "shoulders bilious constitution of average height oval faced thoughtful countenance and the upper "
        "part of the body is generally better formed. "
        "General Tendencies: They can adapt themselves to any condition in life. They have faith. In "
        "affection they are sincere. They stick to orthodox principles in religion but are perfectly "
        "tolerant. Generally good tempered they are sensitive. They are lovers of music literature and "
        "possess a certain amount of philosophical knowledge. They are voracious readers. In life they "
        "do not succeed as much as they would like to and often throughout they struggle very much. Their "
        "ambitions remain unfulfilled to a great extent. They lack a natural policy and hence get into "
        "many difficulties. They are forgiving and do not hold a grudge long. They are likely to suffer "
        "from nervous troubles and are generally misunderstood by their superiors and bosses."
    ),
    6: (
        "Mental Tendencies: Those born in Virgo are impulsive emotional and fond of learning. They love "
        "music and fine arts. They lack self-confidence. Methodical and ingenious they have active minds. "
        "Physical Tendencies: Persons born in this sign will be middle-sized. Their chest will be "
        "prominent and when afflicted weak also. They have a straight nose cheeks massive and the "
        "forehead good. "
        "General Tendencies: They exhibit their intelligence when quite young. They are discriminating "
        "and emotional and get easily carried away by impulse. They are cautious regarding their own "
        "interests prudent economical diplomatic and shrewd. As authors they make progress in physical "
        "and chemical sciences. They acquire much power and influence over others. They are liable to "
        "suffer from nervous breakdowns and paralysis when the sign is afflicted. They are of a "
        "speculative nature."
    ),
    7: (
        "Mental Tendencies: Persons born in Libra are idealistic quick-witted vindictive forceful and "
        "positive. "
        "Physical Tendencies: They generally possess fair complexion a middle-sized stature phlegmatic "
        "constitution handsome appearance broad face fine eyes broad chest and regular features. Their "
        "appearance will be generally youthful. "
        "General Tendencies: People born in this sign are generally of a sensual disposition. They are "
        "keen observers of human nature. They have keen foresight and reason out things from the "
        "standpoint of their own views. They love justice peace order and are agreeable persons. They are "
        "ambitious. They are more idealists than realists or practical men and often contemplate on "
        "schemes that are like building castles in the air. They are not sensitive to what others say of "
        "them. As political leaders and religious reformers they exert tremendous influence over the "
        "masses and sometimes their zeal and enthusiasm can go to such a pitch that they can force their "
        "views upon unwilling minds. They are not easily amenable to reason. They are great lovers of "
        "music. Truth and honesty have a special appeal for them."
    ),
    8: (
        "Mental Tendencies: Sarcastic and impulsive a female born in this sign will be masculine in "
        "nature. Interested in occult forms of study they possess a subtle mind hard to influence. "
        "Physical Tendencies: Persons born in this sign are handsome in appearance. The bones are well "
        "developed. They have broad eyes tall figure curly hair and broad forehead. The personality is "
        "forceful with prominent brows and perceptive faculties. "
        "General Tendencies: They will have a generous disposition. They are exceedingly fickle-minded "
        "and love much excitement. Though inclined to sensual things in reality they will not hesitate "
        "to philosophise upon the virtues of controlling sensual pleasures. They are good "
        "correspondents. They are often brutal brusque and keenly fond of contest. They possess "
        "enterprise. They appreciate luxury but are frugal. They may become expert musicians if they "
        "learn that art. They can also become proficient in fine arts dancing and the like. They uphold "
        "their own views. Their constitution will be hot and they are liable to suffer from piles. They "
        "are good conversationalists as well as writers and often rely too much on their own "
        "intelligence."
    ),
    9: (
        "Mental Tendencies: Those born in Sagittarius have an inclination for philosophy and occult "
        "studies. They can acquire great mastery in these subjects. Humane and somewhat impulsive they "
        "are generally active and enterprising. "
        "Physical Tendencies: Persons born in this sign are generally inclined towards corpulence. They "
        "possess almond eyes and their hair is brown. They are usually good looking. Evenly set teeth a "
        "happy smile and fullness of the figure characterise the natives of Dhanus. "
        "General Tendencies: They are of a phlegmatic temperament. They are too conventional and also "
        "business-like. They are prompt and uphold conservative views. They are sympathetic and loving "
        "and possess good foresight. At times they are restless and overanxious. They are too callous "
        "and enthusiastic. They hate all external show. They are God-fearing honest humble and free from "
        "hypocrisy. They exercise strict control over their food and drinks and in regard to their "
        "relations with the opposite sex. They are prone to be misunderstood unintentionally by others. "
        "In late years they must be careful about their lungs as they are liable to suffer from "
        "rheumatic pains and the like."
    ),
    10: (
        "Mental Tendencies: They are stoical to the miseries of life. Possessed of sympathy generosity "
        "and philanthropy self-willed strong in purpose secretive and vindictive Capricorn natives are "
        "cunning and determined. "
        "Physical Tendencies: Persons born in this sign are tall lean reddish-brown in colour with "
        "prominent stiff hair on the eye-brows and the chest. The head is big and the face fairly broad. "
        "They have large teeth a big mouth prominent nose and are inclined to stoop. The body is thin "
        "and fleshy. "
        "General Tendencies: They have a knack to adapt themselves to circumstances. They have great "
        "aspirations in life and cannot economise funds. They like a lot of show. Noted for their "
        "perseverance. They become vindictive when Saturn is afflicted and may become somewhat bigoted. "
        "They are capable of much endeavour. In the home life they are perfectionists and often cannot "
        "get on well with husbands or wives. They should check this harmful tendency on their part. "
        "They are industrious. If Mars occupies any sign other than his own they lack confidence become "
        "funky nervous and weak-minded. They can be described as chatter-boxes and have little or no "
        "control over their tongues."
    ),
    11: (
        "Mental Tendencies: Aquarius being a philosophical sign people born in it become great teachers "
        "writers and lecturers provided the sign is free from afflictions. Natives of Aquarius are "
        "reserved they are peevish when provoked generous hearted highly sympathetic and are always bent "
        "upon helping others. They are intelligent good memory and capable of dealing with facts. "
        "Physical Tendencies: They are generally tall and lean with countenance handsome appearance "
        "attractive and disposition elegant. Their lips are flushy cheeks are broad and they have "
        "prominent temples and buttocks. If Saturn is in the 4th the chest will be weak with a tendency "
        "towards stooping. "
        "General Tendencies: They make friends of others very soon. They are peevish and when provoked "
        "rise like a bulldog but their anger is easily subsided. They shine very well as authors and "
        "writers. Their conversation is always interesting. They are sometimes timid and funky. They "
        "feel shy to exhibit their talents before new audiences. They specialise in subjects like "
        "astrology and become great upholders of some such cause. Their literary greatness comes before "
        "the world when they are quite young. Unless the planetary positions are otherwise favourably "
        "situated people born in this sign will suffer certain critical setbacks which will jeopardise "
        "their reputation. Owing to their humanitarian doctrines they are prone to be misunderstood. In "
        "family life they will not have sufficient happiness. They will be much devoted to their "
        "husbands or wives. They are liable to suffer from colic troubles chest pain and the like. "
        "They should always be kept happy in life by their husbands or wives. Otherwise their health "
        "will suffer."
    ),
    12: (
        "Mental Tendencies: Persons born in Pisces are stubborn psychically receptive highly religious "
        "stoical bigotted and God-fearing. "
        "Physical Tendencies: They are fair stout of middle-sized height swarthy in complexion eyes "
        "piscean and inclined towards corpulence. "
        "General Tendencies: They are respectors of orthodoxical principles and can forego anything but "
        "orthodoxy. They are extremely superstitious. They are very reserved and are liable to draw "
        "premature conclusions on any matter. They are God-fearing and very rigid in the observance of "
        "religious customs and practices. They are stubborn rather timid and ambitious to exercise "
        "authority over others. They rarely realise their ambitions. They are restless and fond of "
        "history antiquarian talks and mythological masterpieces. They are frugal in spending money and "
        "though generally dependent upon others throughout their life still bear a mark of independence. "
        "They are just in their dealings and fear to transgress the laws of truth. With all this they "
        "lack self-confidence."
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_lagna_sign_num(birth_time: AstroTime) -> int:
    """Return the rising sign number (1-based, Aries=1 … Pisces=12)."""
    lagna_longitude = get_lagnam(birth_time)
    return int(lagna_longitude / 30) % 12 + 1


def get_rising_sign_interpretation(birth_time: AstroTime) -> dict:
    """Return the rising sign interpretation for the given birth time.

    Returns:
        dict with keys: sign_num, sign_name, description.
    """
    sign_num = get_lagna_sign_num(birth_time)
    sign_name = SIGN_NAMES[sign_num]
    description = _RISING_SIGN_DATA.get(sign_num, "")
    return {
        "sign_num": sign_num,
        "sign_name": sign_name,
        "description": description,
    }
