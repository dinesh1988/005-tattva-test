"""House-Lord-in-House (Natal) Interpretations.

For each of the 12 house lords placed in each of the 12 natal houses this
module provides the classical Vedic interpretation text sourced from the
VedAstro C# HoroscopeDataListStatic.cs (EventTag.Personal).

Lookup key: (lord_house: int, placement_house: int) -> description str
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .time import AstroTime
from .consts import Planet
from .lordship import get_lord_of_house
from .house_queries import get_planet_house

# ---------------------------------------------------------------------------
# Data table: (lord_house, placement_house) -> description
# ---------------------------------------------------------------------------

_HOUSE_LORD_IN_HOUSE_DATA: Dict[Tuple[int, int], str] = {

    # ── House 1 Lord ─────────────────────────────────────────────────────────
    (1, 1): (
        "The subject lives by his own exertion will have an independent spirit and will have two wives or one "
        "married and another illegal. the person becomes famous in his own community and country. the results "
        "produced will be quite different from those which he would have produced by being aspected by benefics. "
        "The same rules apply to all Bhavas which should be borne in mind by every reader."
    ),
    (1, 2): (
        "There will be more of gains teased or worried by enemies good character respectable and generous "
        "hearted. Well-disposed. He will gladly discharge his duties towards his kith and kin and will be "
        "ambitious. He will possess prominent eyes and be blessed with forethought."
    ),
    (1, 3): (
        "Makes one highly couragious fortunate reepectable two wives intelligent and happy. When Lagnadhipati "
        "is well disposed the natives rise in life will be brought about by his brothers. He may become famous "
        "as a musician or a mathematician depending upon the nature of the sign and the planets involved."
    ),
    (1, 4): (
        "There will be happiness from parents many brothers materialistic well built fair looking and "
        "well-behaved. If the 4th lord is favourably disposed the person will acquire considerable landed "
        "properties specially through maternal sources. He will be rich happy famous and commands a number "
        "of conveyances."
    ),
    (1, 5): (
        "The first child does not survive not much happiness from children short tempered subservient and "
        "serving others. If fortified In the good graces of rulers or powerful political parties and likely "
        "to be absorbed into trade or diplomatic services. He will propitiate deities consistent with the "
        "indications of the fifth lord."
    ),
    (1, 6): (
        "In addition to the results produced by the lord of Lagna being in the third the following may also "
        "be noted. There will be bebts but they will be liquidated when the Dasa of the Lagndhipati comes. "
        "When the lord is fortified the native joins the army becomes a Commander or even a "
        "Commander-in-chief provided the lords Dasa operates at the opportune period. Or he may become head "
        "of medical or health services or an expert physician or surgeon. Here the other influences should "
        "be suitably balanced."
    ),
    (1, 7): (
        "The wife does not live or there will be more than one marriage. Later in life becomes detached from "
        "worldly affairs and tries to lead an ascetic life. Depending upon other factors the subject will "
        "either be rich or poor. There will be much travelling. If well disposed he will spend most of his "
        "time in foriegn countries and lead a licentious life. Or he will be a puppet in the hands of his "
        "parents-in-law."
    ),
    (1, 8): (
        "Learned gambling tendencies interested in occultism and mean character. If the lord is strong the "
        "native takes pride in helping others has a number of friends religiously inclined and will have a "
        "peaceful and sudden end."
    ),
    (1, 9): (
        "Generally fortunate protector of others religious is a Hindu worshipper of Vishnu good orator "
        "happiness on account of wife and children and rich. Provided the lord is well disposed he will "
        "inherit good ancestral and paternal property. The father will be famous philanthropic and "
        "god-fearing."
    ),
    (1, 10): (
        "In addition to the results of the 4th house there will be professional success honoured by eminent "
        "men a research scholar or specialisation in that branch of knowledge or profession which is "
        "represented by lord of Lagna and the 10th."
    ),
    (1, 11): (
        "In addition to the results of the 2nd house there will always be gains in business if a businessman. "
        "The subject will not experience financial straits. He owes his prosperity to his elder brother. He "
        "will earn enormous business profits consistent with the indications of the other planets joining "
        "the combination."
    ),
    (1, 12): (
        "The same results as in the 8th are produced. In addition there will be many losses visiting holy "
        "places and no success in business enterprises. He will spend inherited riches on charities and other "
        "deserving causes. Emotionally balanced he will dedicate himself for public weal."
    ),

    # ── House 2 Lord ─────────────────────────────────────────────────────────
    (2, 1): (
        "The native becomes no doubt wealthy but he hates his own family lacks polite manners becomes "
        "passionate subservient and time-serving. one will earn money by his own effort intelligence and "
        "learning."
    ),
    (2, 2): (
        "Becomes proud. The native may marry twice or thrice depending upon the strength of the seventh "
        "house. He may become childless. The position of the 2nd lord in a constellation which does not "
        "happen to be the 3rd 5th and 7th from Janma Nakshatra is highly desirable especially if he is "
        "otherwise fortified i.e. joined with or aspected by benefics. The exaltation of the 2nd lord of "
        "his disposition in Lagna the 4th 5th 7th 9th or 10th will fortify him to the extent of making him "
        "a yogakaraka. The native will be enabled to earn considerable fortune through business or other "
        "occupations consistent with the nature of the 2nd lord and 2nd house. Depending upon the nature of "
        "the aspects cast on the 2nd lord by malefic planets the native will sustain losses. An affliction "
        "to the 2nd lord may also express itself in the shape of the subject not getting nutritious and "
        "delicious food or his family and children suffering from constant diseases or want of cordial "
        "relations between the native and his life-partner."
    ),
    (2, 3): (
        "Brave intelligent good-natured but depraved character. Atheistic tendencies will be rampant and he "
        "becomes addicted to luxuries. Later in life he turns out to be a miser. When the 2nd lord in the "
        "3rd is well fortified he will be benefited by his sisters. He will benefit by learning fine arts "
        "viz. music and dancing. He will also indulge in propitiating Kshudra Devatas or evil spirits."
    ),
    (2, 4): (
        "He will spend money for his own happiness. He will be highly frugal in dealing with money. When "
        "well fortified one will earn well as an automobile dealer or agent or an agriculturist or landlord "
        "or commission agent. He will also be benefited by his maternal relations. When afflicted one will "
        "have losses as an automobile dealer or agent."
    ),
    (2, 5): (
        "Hating family sensual not spending money even on children he lacks manners and etiquette. When the "
        "2nd lord in the 5th is well fortified there will be unexpected acquisition of wealth through "
        "lotteries crosswords or the favour of rulers."
    ),
    (2, 6): (
        "Income and expenditure from enemies. He will suffer from defects or diseases in the anus and "
        "thighs. Amassing of wealth by black-marketing deceit dissimulation and by creating "
        "misunderstandings and troubles between friends and relatives and through questionable and suspicious "
        "dealings can be anticipated."
    ),
    (2, 7): (
        "Likely to become a healer. Laxity of morals will mark both husband and wife. He will waste much "
        "money on the gratification of the senses. When the second lord who joins the 7th with the 7th lord "
        "is strong there will be influx of wealth through foreign sources. The native will undertake "
        "journeys to foreign countries and do business. When the Rasi Navamsa or the constellation held by "
        "the 2nd lord happens to be a feminine one then he will benefit by contact with women."
    ),
    (2, 8): (
        "Will have very little or no happiness from wife or husband. Misunderstandings with elder brothers. "
        "Gets landed properties. When the 2nd lord is strong there will be influx as well as loss of wealth. "
        "Actual observation reveals that under such a combination there will hardly be any earnings but "
        "inherited or accumulated wealth will disappear."
    ),
    (2, 9): (
        "Skilful ill-health in young age but healthy afterwards will possess lot of wealth and become happy. "
        "When the 2nd lord is well fortified and the 9th lord is in Lagna the native will have good "
        "inheritance. There will also be benefits through different sources according to the nature of the "
        "sign and nakshatra held by the 2nd lord."
    ),
    (2, 10): (
        "Respect from elders and superiors learned wealthy and he earns by his own exertions. The native "
        "will take to a number of useful avocations. He will do business or take to agriculture and also "
        "engage himself in philosophical lectures and dissertations and thereby benefit financially. Here "
        "again the constellation and the sign held by the 2nd lord determine the exact nature and sources "
        "of earnings. Powerful afflictions will cause loss from the very same sources."
    ),
    (2, 11): (
        "Health will be bad during childhood earns considerable wealth but becomes unscrupulous. When well "
        "fortified one earns by lending money or as a banker or by running a boarding house."
    ),
    (2, 12): (
        "The native becomes a respectable man. In all probability he will be a government servant and will "
        "be deprived of the happiness of elder brother. The income will be through ecclesiastical sources."
    ),

    # ── House 3 Lord ─────────────────────────────────────────────────────────
    (3, 1): (
        "Earns livelihood by self-exertion becomes vindictive lean and tall body brave and courageous always "
        "sickly and serving others. When well fortified he will become an expert in dancing music and acting "
        "and the means of livelihood will be primarily fine arts. He will earn a good name as an actor."
    ),
    (3, 2): (
        "This is an unfavourable position as it makes the subject rather unscrupulous unless there are other "
        "favourable combinations. He will make advances on the women and wealth of others. Likes mean deeds "
        "and is generally devoid of happiness. He is likely to lose his younger brothers."
    ),
    (3, 3): (
        "Brave surrounded by friends relatives blessed with good children wealthy happy and contented. The "
        "3rd lord well disposed in the 3rd 6th or 11th indicates a number of younger brothers. When the 3rd "
        "lord happens to be Mars and occupies the 3rd then generally the native will lose all his younger "
        "brothers. Saturn will also give similar effects. The Sun in a similar position will kill elder "
        "brothers."
    ),
    (3, 4): (
        "Life will be happy on the whole. He becomes rich and learned. But the wife will be "
        "cruel-hearted and mean."
    ),
    (3, 5): (
        "Much pleasure will not be derived from children. Financially well off in life. Friction will "
        "prevail in the domestic life. Well disposed the native will be highly benefited by his brothers. "
        "He will carry on agricultural operations on a large scale or he will be adopted by a rich family. "
        "He will also shine well in Government service."
    ),
    (3, 6): (
        "Hates brothers and relatives and difficulty through them. Becomes rich. Maternal relatives will "
        "suffer. Accepts illegal gratifications. When the 3rd lord is in the 6th well disposed younger "
        "brother joins the Army. One of the brothers will become a successful physician."
    ),
    (3, 7): (
        "May incur the displeasure of rulers or authorities. Many vicissitudes in life. Much suffering in "
        "childhood. The union will be unfortunate. Danger while travelling. When the 3rd lord is in the 7th "
        "well fortified there will be cordial feelings between brothers. When the 7th lord is in Lagna one "
        "of the brothers will settle in a foreign country and he will help the native."
    ),
    (3, 8): (
        "Involvement in a criminal case or false accusations. Trouble on account of death or bequests "
        "marriage unfortunate career will not be smooth victim of misfortune. When the 3rd lord is in the "
        "8th he will suffer from a serious and dangerous disease and lose his younger brother."
    ),
    (3, 9): (
        "Fortune will improve after marriage. Father untrustworthy. Long journeys. Sudden and unexpected "
        "changes in life. When the 3rd lord is in the 9th favourably disposed the natives brother will "
        "inherit ancestral property. The native himself will be benefited by his brother. When afflicted "
        "the person will have misunderstandings with his father."
    ),
    (3, 10): (
        "A quarrelsome and faithless wife. The native will become rich. He will be happy and intelligent. "
        "Gain from journeys connected with profession. When the 3rd lord is in the 10th all the brothers "
        "will shine well and they will be helpful to him in all ways."
    ),
    (3, 11): (
        "Not a very good combination. Earnings with effort. He becomes vindictive. The body will be "
        "unattractive and emaciated. Subservient to or dependent upon others and liable to suffer from "
        "frequent attacks of illness."
    ),
    (3, 12): (
        "Sorrow through relatives gets fortune from marriage seclusion. Great ups and downs. Unscrupulous "
        "father. When the 3rd lord is in the 12th the youngest brother will be a tyrant. The native becomes "
        "poor on account of him."
    ),

    # ── House 4 Lord ─────────────────────────────────────────────────────────
    (4, 1): (
        "The person becomes highly learned but will be afraid to speak in public assemblies. He is likely to "
        "lose inherited wealth. According as the fourth lord posited in Lagna is strong middling or weak the "
        "native will have been born in a rich mediocre or poor family."
    ),
    (4, 2): (
        "He will be highly fortunate courageous and happy. He will have a sarcastic nature. He will inherit "
        "property from maternal grandfather."
    ),
    (4, 3): (
        "The person will be sickly generous a man of character and will acquire wealth by self-effort. He "
        "will suffer from the machinations of step-brothers and step-mother."
    ),
    (4, 4): (
        "Religiously inclined will have respect for traditions. He will be rich respected happy and sensual."
    ),
    (4, 5): (
        "Loved and respected by others devotee of Vishnu becomes rich by self-effort. Mother comes from a "
        "respectable family. The native will acquire vehicles."
    ),
    (4, 6): (
        "Short-tempered and mean he will have dissimulating habits evil thoughts and intentions. He will "
        "always be roaming about."
    ),
    (4, 7): (
        "Generally happy will command houses and lands will eke out livelihood in distant places or near his "
        "birthplace according as the seventh happens to be a movable or fixed sign."
    ),
    (4, 8): (
        "The person becomes miserable. Father dies early. He will be either impotent or loose in sex-life. "
        "He is also likely to lose landed properties or face litigation."
    ),
    (4, 9): (
        "Generally a fortunate combination favouring happiness in regard to father and properties."
    ),
    (4, 10): (
        "Will have political success. He will be an expert chemist. He will vanquish his enemies and make "
        "his personality felt by the world."
    ),
    (4, 11): (
        "Self-made generous sickly mother fortunate but may have a step-mother also. Favours success in "
        "selling and buying cattle and lands."
    ),
    (4, 12): (
        "Deprived of happiness and properties. Early death to mother bad finances and generally a miserable "
        "existence."
    ),

    # ── House 5 Lord ─────────────────────────────────────────────────────────
    (5, 1): (
        "The person commands a number of servants becomes a Judge Magistrate or Minister empowered to punish "
        "the evil-minded. He will earn the grace of God. Few children will have foes and gives happiness to "
        "others. If the 5th lord is afflicted there will be no issues will invoke kshudra devatas evil and "
        "destructive forces will be evil-minded and leader of a gang of deceitful persons a tale-bearer with "
        "a sting. If the lord is moderately good mixed results will follow."
    ),
    (5, 2): (
        "If the 5th lord is favourably disposed the person will be blessed with a beautiful wife and "
        "well-behaving children. There will be gains from Government or King. He will become learned and a "
        "good astrologer. Lord weak and afflicted: Poor loss of money through Government displeasure will be "
        "unable to maintain his own family will have family troubles and misunderstandings becomes a priest "
        "in a Siva temple."
    ),
    (5, 3): (
        "Many good children and brothers. When afflicted: loss of children misunderstandings with brothers "
        "and continuous occupational troubles. He will become stingy and a tale bearer."
    ),
    (5, 4): (
        "If favourably disposed the person will have a few sons one of whom will live by agriculture. The "
        "mother will live long. May become an adviser to a ruler or his preceptor. The lord afflicted causes "
        "death of children. The lord moderately strong confers daughters and no sons."
    ),
    (5, 5): (
        "Lord favourably disposed indicates a number of sons becomes great in his own line of activity "
        "otherwise he becomes an expert in Mantrasastra and befriends persons in power. He may also become "
        "an expert in mathematics or head of a religious institution. Lord afflicted contrary results should "
        "be anticipated. Children will die he will not keep to his word wavering mentality and cruel."
    ),
    (5, 6): (
        "If the fifth lord is favourably disposed the maternal uncle will be a famous man. He will have "
        "enmity with his own son. If the lord is afflicted issues will not be born and he may have to adopt "
        "one from maternal uncles line."
    ),
    (5, 7): (
        "When the lord is favourably disposed the natives son lives abroad and attains distinction wealth "
        "and fame. Or he will have a number of issues. He will also become renowned learned prosperous "
        "greatly devoted to his master and possesses a charming personality. When the lord is afflicted "
        "there will be loss of children one of whom will die abroad after attaining name and fame."
    ),
    (5, 8): (
        "Paternal property will be lost due to debts. There will be extinction of the family. He will suffer "
        "from lung troubles. He will be peevish unhappy but not poor."
    ),
    (5, 9): (
        "He will become a teacher or a preceptor. Renovates ancient temples wells choultries and gardens. "
        "One of the sons attains distinction as an orator or author."
    ),
    (5, 10): (
        "If the lord is beneficially disposed a Raja Yoga is formed. Acquires landed property earns the "
        "goodwill of the rulers constructs temples and performs religious sacrifices one of the sons becomes "
        "a gem of the family. If aspected by the Sun the native may join the intelligence department. If the "
        "lord is afflicted faces the wrath of the rulers and contrary results will happen."
    ),
    (5, 11): (
        "Benefits through sons and success in all undertakings becomes rich and learned and helps others "
        "will have a number of sons becomes an author."
    ),
    (5, 12): (
        "Quest for knowing the Ultimate Reality will be pronounced. He will lead a life of non-attachment "
        "becomes spiritual moves from one place to another and ultimately attains Moksha."
    ),

    # ── House 6 Lord ─────────────────────────────────────────────────────────
    (6, 1): (
        "The person may join the army as a soldier or Commander consistent with the strength or otherwise of "
        "the disposition. Or he may become a Minister of War or an official or officer concerned with "
        "prisons. He will live in the house of his maternal uncle. When afflicted he will become a robber or "
        "a thief or leader of a criminal gang."
    ),
    (6, 2): (
        "Conjoined with or aspected by benefics the native will have untold suffering in family life and "
        "deep sorrows loss of money through enemies defective vision uneven teeth and stammering. If the "
        "sixth lord is weak and otherwise ill-disposed in the 2nd there will be loss of wife in the Dasa or "
        "Bhukti of the malefic lord. If Venus is weak the native will be a celibate and poverty-stricken "
        "just able to get a morsel of food when hungry."
    ),
    (6, 3): (
        "The sixth lord fortified confers enmity with brothers. Or his maternal uncle befriending the "
        "natives brother works against the natives interests or the natives brother suffers from frequent "
        "ill-health. The 6th lord weak and afflicted the native will have no younger brothers."
    ),
    (6, 4): (
        "Well fortified lives in a dilapidated building. He will have breaks in education and will discard "
        "his mother. Maternal uncles will generally be land cultivators. Weak and afflicted he will quarrel "
        "with his mother and ancestral property will be involved in debts. He will work as a menial and lead "
        "a miserable life. Troublesome home and domestic affairs and trouble through servants."
    ),
    (6, 5): (
        "Sickly children. The native will be adopted by his maternal uncle and become fortunate."
    ),
    (6, 6): (
        "Increase of cousins. Natives maternal uncle becomes famed. If in conjunction with weak Lagnadhipati "
        "he will suffer from an incurable disease and increase of enmity with kith and kin."
    ),
    (6, 7): (
        "Generally marries mothers brothers or fathers sisters daughter. The maternal uncle lives in a "
        "far-off place or a foreign country. The wifes character will be doubtful. If the sixth lord is "
        "afflicted he will either divorce his wife early in life or she will die. If the Rasi and Navamsa "
        "involved are hermaphrodite ones he will have a sickly or barren wife. When Lagnadhipati joins the "
        "sixth lord in the 7th which happens to be a hermaphrodite sign the native will be a eunuch and "
        "unable to perform the sexual act. There will also be troubles with disrespectable women."
    ),
    (6, 8): (
        "When fortified he will have Madhyayu or middle life. When afflicted he will have plenty of debts "
        "and will suffer from loathsome diseases. He will hunt after women other than his own wife and take "
        "pleasure in inflicting pain on others."
    ),
    (6, 9): (
        "Father becomes a judge if the sixth lord is well fortified. The maternal uncle becomes highly "
        "fortunate. There will be misunderstandings between him and his father. There will be benefits from "
        "Gnatis or cousins. If afflicted poverty sinful acts misfortunes through relatives ungrateful towards "
        "preceptors and engaged in unrighteous deeds. If moderate becomes a mason timber merchant or stone "
        "cutter."
    ),
    (6, 10): (
        "If fortified sinful and destructive nature poses as an orthodox and pious man but really "
        "unscrupulous in regard to religious matters. When the lord is weak dismissal formidable enemies "
        "low life or begging."
    ),
    (6, 11): (
        "If benefic eldest brother will be a judge. If ordinary an elder brother becomes a judge for some "
        "time but loses his job. If malefic poor and wretched life suffering on account of convictions."
    ),
    (6, 12): (
        "Well disposed difficulty and sorrow through destructive nature causes harm to others. If afflicted "
        "miserable hard and wretched existence."
    ),

    # ── House 7 Lord ─────────────────────────────────────────────────────────
    (7, 1): (
        "The native may marry someone he has known since childhood or one who has been brought up in the "
        "same house. The wife or husband of the native will be a stable and mature person. He will be "
        "intelligent and capable of weighing the pros and cons. Afflictions to the 7th lord may entail "
        "constant travelling. If the 7th lord and Venus are afflicted the native may be sensual and seek "
        "clandestine relationship with the opposite sex."
    ),
    (7, 2): (
        "The native will get wealth from women or through marriage. If afflicted one may earn money through "
        "despicable means as trading in flesh women not excluding his wife. He may eat food offered at "
        "death-ceremonies shraddha and wander about seeking such food. If the second house is a dual sign "
        "and afflicted more than one marriage is likely. If a maraka Dasa is on the native may die during "
        "the period of the seventh lord. The person will have a wavering mind and will always be inclined "
        "sensually."
    ),
    (7, 3): (
        "This disposition gives lucky brothers who may live abroad. If afflicted the native may indulge in "
        "adultery with a brothers or sisters married partner. Affliction also gives misfortunes to co-borns. "
        "Female issues survive."
    ),
    (7, 4): (
        "Gives a lucky and happy married partner with many children and comforts. The native may have the "
        "benefit of high academic qualification and own many vehicles. If afflicted domestic harmony may be "
        "spoilt through an immature and mean partner. The native may run into endless problems on account of "
        "his conveyances. If severely afflicted by the nodes and other malefics the natives wifes character "
        "becomes questionable."
    ),
    (7, 5): (
        "An early marriage the partner may hail from an affluent and well-to-do family. The wife or husband "
        "will be mature and an advantage to the native. If the 7th lord is weak there may be no children. "
        "If severely afflicted one may get issues through the adulterous conduct of the wife. If there are "
        "both afflictions and benefic influences on the 7th lord the native may get only female progeny. "
        "Trouble to ones office superiors through foreign sources is likely. The native will possess good "
        "character."
    ),
    (7, 6): (
        "The native may have two marriages with both partners living. One may marry a cousin such as an "
        "uncles daughter. If badly afflicted and the karaka Venus is also ill-disposed one may suffer from "
        "impotency and many other diseases. The natives wife may be sickly and jealous by nature denying "
        "the husband happiness from marriage. If Venus is well placed but the 7th lord is afflicted the "
        "native may suffer from piles. If Venus is weak but not afflicted one may desert or lose ones "
        "married partner through some indiscreet act."
    ),
    (7, 7): (
        "If well placed the native will have a charming and magnetic personality. Women will flock to him "
        "and seek him out for alliance. The wife or husband will be a just and honourable person coming "
        "from a family of reputation and social standing. If weak and afflicted it gives a lonely life "
        "devoid of marriage and friends and loss through marriage negotiations."
    ),
    (7, 8): (
        "When well placed marriage may take place with relatives or the partner may be a rich person. "
        "Affliction causes the early death of partner while the native may die in distant lands. It gives "
        "a sickly and ill-tempered wife or husband leading to estrangement and separation."
    ),
    (7, 9): (
        "If fortified the father may live abroad while the native may make his fortune in foreign lands. He "
        "will get an accomplished wife who will enable him to lead a righteous life. If afflicted the father "
        "may die early. Married partner may drag the native from the right course Dharmic of life and he "
        "may waste away his wealth and suffer penury."
    ),
    (7, 10): (
        "The native may flourish in a profession abroad or his career may involve constant travelling. One "
        "will get a devoted and faithful wife or husband. The wife may also be employed and contribute to "
        "the natives income. Or she may help in the advancement of the natives career. If afflicted wife "
        "will be avaricious and over-ambitious but without sufficient capacity. Consequently natives career "
        "may suffer and deteriorate."
    ),
    (7, 11): (
        "There may be more than one marriage or the native may associate with many women. If beneficially "
        "disposed wife may hail from a rich background or bring in much wealth. If afflicted the native may "
        "marry more than once but one wife may outlive him."
    ),
    (7, 12): (
        "There maybe more than one marriage in the natives life. He may marry a second time clandestinely "
        "while the first wife is still alive. Or if afflicted he may marry a second time after losing the "
        "first wife by death or separation. But if the affliction is severe the wife or husband may die or "
        "separate soon after marriage and there may be no second marriage. Death may occur while travelling "
        "or abroad. If both karaka and the 7th lord are weak the native may only dream of women but never "
        "marry. The natives wife may hail from a servants family. He will be close-fisted and generally "
        "poor."
    ),

    # ── House 8 Lord ─────────────────────────────────────────────────────────
    (8, 1): (
        "Penury and heavy debts will befall the native who has the 8th lord placed in the Ascendant with "
        "the Ascendant lord. Misfortune will follow him at every step. If the 8th lord is weak or placed in "
        "the 6th 8th or 12th from Navamsa Lagna the intensity of misfortune is reduced. If the 8th lord is "
        "severely afflicted the native will suffer bodily complaints such as disease and disfiguration. His "
        "constitution will be weak and he will have no bodily comforts. He will be the target of the "
        "displeasure of his superiors and higher-ups. Trouble from Government will cause him worries."
    ),
    (8, 2): (
        "The lord of the 8th house in conjunction with the 2nd lord in the 2nd house brings in troubles and "
        "problems of all sorts. The native suffers from eye and tooth troubles. He will have to eat unhealthy "
        "and tasteless or putrid foods. His domestic life will be filled with discontent and quarrels. His "
        "wife will not understand him. This may lead to estrangement and even separation. If longevity is "
        "good he may suffer some severe illness. If the 8th lord is in the 6th 8th or 12th from Navamsa "
        "Lagna the intensity of the results will be reduced in degree."
    ),
    (8, 3): (
        "If the lord of the 8th house combines with the lord of the 3rd in the 3rd the third house "
        "significations suffer. The natives ears may cause problems or he may go deaf. Misunderstandings "
        "will crop up with brothers and sisters leading to quarrels. The native will be beset by all sorts "
        "of fears and mental anguish. He may imagine things and suffer from hallucinations. He may involve "
        "himself in debts and get into trouble thereby. If malefics afflict the 8th lord in the 3rd with "
        "the 3rd lord the sufferings of the native will be unbearable. But if the 8th lord combines with "
        "the 6th or 12th lords benefic results may come by. He may get a monetary windfall through writing "
        "or through the agency of a co born."
    ),
    (8, 4): (
        "If the lord of the 8th house joins the 4th lord in the 4th house the natives mental peace will be "
        "shattered. Domestic bickerings financial and other problems will increase. Mothers health may suffer "
        "and cause great concern. The native may be beset with problems regarding his house land and "
        "conveyance. If the affliction is heavy his land and immovable property may slip from his hands due "
        "to circumstances beyond his control. His conveyances may get lost or be destroyed. His pets may "
        "contract diseases and die. Malefics furthering the affliction may force him to seek his fortune "
        "abroad where he will meet with all sorts of troubles and losses. Reverses in profession and the "
        "displeasure of superiors are also likely."
    ),
    (8, 5): (
        "If the lord of the 8th is in the 5th with the 5th lord the children of the native may get into "
        "trouble. They may commit some crime and invite situations that could affect the natives reputation. "
        "Or the native and his father may develop misunderstandings. The natives child may fall sick and "
        "suffer thereby. If the affliction is heavy a child may die as soon as it is born or cause much "
        "grief to the native due to some incurable physical affliction or mental retardation. The native may "
        "also suffer much bodily ill-health. If the 8th lord is in the 6th 12th or 8th from Navamsa Lagna "
        "the evil results are greatly mitigated. But if fortified in a kendra or trikona the evil results "
        "are intensified. Since the 5th house is the buddhisthana the native may also suffer nervous debility "
        "or breakdown or mental aberration."
    ),
    (8, 6): (
        "If the lord of the 8th house joins the 6th lord in the 6th house a Rajayoga results. Material "
        "affluence fame and acquisition of objects desired are the good results. But because the 6th house "
        "is the house of disease the native may suffer ill-health. If afflicted the native suffers loss of "
        "money through theft and trouble through courts and the police. The evil is intensified if the 8th "
        "lord is in a kendra or trikona. The natives maternal uncle may suffer much trouble. If the 6th lord "
        "is fortified he is able to overcome all his troubles and emerge victor. No attempts made by his "
        "ill-wishers and enemies to harm him will succeed."
    ),
    (8, 7): (
        "The lord of the 8th house placed in the 7th house with the 7th lord curtails longevity. The "
        "natives wife may suffer ill-health. If afflicted the native will also suffer from disease. He may "
        "go abroad where he will meet with ill-health and problems. If the 7th and 8th lords are strong the "
        "native will undertake foreign journeys on diplomatic missions and distinguish himself."
    ),
    (8, 8): (
        "If the lord of the 8th house occupies the 8th house in strength the native lives long enjoying "
        "happiness. He will acquire lands conveyance power and position through the merit acquired in former "
        "lives. If the 8th lord is weak he may have no serious troubles but may not also enjoy any luck or "
        "good fortune of significance. The father of the native may die or pass through some crisis. If the "
        "8th lord is afflicted the native will fail in his undertakings. He will be prompted to do the "
        "wrong things and thereby suffer loss."
    ),
    (8, 9): (
        "If the lord of the 8th house joins the 9th lord in the 9th house with malefics the native may lose "
        "his fathers property. Misunderstandings with father may arise. If the Sun the natural significator "
        "of father is afflicted father may die during the period of the 9th lord. If conjoined with benefics "
        "the native acquires his fathers property. Relations with father will be harmonious. If the 9th lord "
        "is weak the native suffers all kinds of hardships misery and unhappiness. His friends and kinsmen "
        "may desert him while his superiors will find fault with him. If the 8th lord is in the 6th 8th or "
        "12th from Navamsa Lagna the evil results will be greatly reduced."
    ),
    (8, 10): (
        "If the lord of the 8th house is in the 10th house with the 10th lord the native has slow "
        "advancement in career. He faces obstacles and impediments in his activities. In the appropriate "
        "period he may be superseded by his subordinates and his merit may go unnoticed. He may resort to "
        "deceit and unrighteous means to gain his ends. His thinking will be clouded and his actions will "
        "invite the wrath of the government or the law. He may suffer poverty. If the 2nd lord is also "
        "afflicted and joins the 8th lord his reputation may suffer due to involvement in huge debts and "
        "inability to repay them. If the 8th lord is placed in the 6th 8th or 12th from Navamsa Lagna the "
        "intensity of the evil is greatly reduced. The 8th lord in the 10th may also confer unexpected gains "
        "due to the death of the superiors or elders."
    ),
    (8, 11): (
        "If the lord of the 8th house combines with the 11th lord in the 11th house there may be trouble to "
        "close friends. Elder brother may pass through a difficult time. Relations with him will be strained "
        "and troubled. Or the elder brother may cause anguish to the native and his family by his "
        "unscrupulous behaviour and conduct. Business may suffer losses and run into debts. If benefic "
        "planets influence the combinations there will be troubles but the native gets help from friends and "
        "elder brother to overcome them. Afflictions will aggravate the malefic results."
    ),
    (8, 12): (
        "The position of the 8th lord in the 12th house with the 12th lord gives rise to a Rajayoga. If "
        "benefics join the 8th lord unfavourable results may be expected. Treachery of friends will result "
        "in many problems and grief. Unexpected expenditure will arise and there may be pecuniary losses. "
        "If the 8th lord is in the 12th house and the 12th lord is favourably placed in a trine or quadrant "
        "the native will gain in religious learning and piety. Some post or seat of authority may be thrust "
        "on him with all its attendant paraphernalia. If afflicted by malefics the native may resort to "
        "vicious acts clandestinely. Such acts would include rape adultery counterfeiting of money. The "
        "8th house signifies sudden gains of money and smuggling activities."
    ),

    # ── House 9 Lord ─────────────────────────────────────────────────────────
    (9, 1): (
        "When the ninth lord is placed in the first house the native becomes a self-made man. He earns much "
        "money through his own efforts. If the 9th lord combines with the Lagna lord in the first house and "
        "associates with or is aspected by a benefic planet the native is fortunate with riches and "
        "happiness."
    ),
    (9, 2): (
        "When the ninth lord is placed in the 2nd house beneficially the natives father is a rich and "
        "influential man. The native acquires wealth from the father. Malefics influencing the ninth lord "
        "in the 2nd house ruin or destroy paternal property."
    ),
    (9, 3): (
        "If the lord of the ninth is placed in the 3rd the native makes his fortune through writing speeches "
        "and oratorial abilities. The natives father will be a man of moderate means while the native "
        "advances his fortune through his co-borns. If malefics afflict the ninth lord in the 3rd house the "
        "native may land in trouble through his writings which may be irrational and even obscene depending "
        "upon the nature of affliction. He may be forced to sell his paternal property because of troubles "
        "occurring through his writings."
    ),
    (9, 4): (
        "The ninth lord in the 4th house gives vast landed properties and beautiful bungalows. Or the native "
        "may earn through estate and land dealings. His mother will be a rich and fortunate woman. He will "
        "inherit his fathers immovable properties. If the ninth lord is afflicted in the 4th house the "
        "native may not have any domestic unhappiness. His early life will be crossed by miseries due to a "
        "hard-hearted father or disharmony between parents. If Rahu afflicts mother may be a divorcee or "
        "living separately from his father."
    ),
    (9, 5): (
        "The ninth lord in the fifth house gives a prosperous and famous father. The natives sons may also "
        "be very fortunate in life and enjoy success and distinction."
    ),
    (9, 6): (
        "The ninth lord in the sixth house gives a sickly father afflicted with chronic diseases. If "
        "benefics flank such a sixth house the native may gain wealth through successful termination of "
        "fathers legal problems and by way of compensation costs etc. If malefics afflict the ninth lord in "
        "the sixth house the natives attempts to make his fortune may be frustrated through litigation "
        "involving his father or debts contracted by him."
    ),
    (9, 7): (
        "The native may go abroad and prosper there. His father may also prosper in foreign lands. He will "
        "get a noble and lucky wife. If ascetic yogas are present in the chart the native may seek spiritual "
        "guidance and fulfilment abroad. If asubhayogas spoil the ninth lord the father may meet with his "
        "death abroad."
    ),
    (9, 8): (
        "The native may lose his father early in life. If malefics afflict the eighth house in such a case "
        "he may suffer severe poverty and heavy responsibility due to fathers death. If benefics influence "
        "the ninth lord the native may inherit substantial paternal property. Afflictions may cause the "
        "native to abandon traditions or damage religious institutions and trusts set up by the family."
    ),
    (9, 9): (
        "The ninth lord in the ninth house gives a long-lived and prosperous father. The native will be "
        "religiously inclined and be charitable. He will travel abroad and earn money and distinction "
        "thereby. If afflicted by malefics or if the 9th lord occupies the 6th 8th or 12th from Navamsa "
        "Lagna the natives father will die early."
    ),
    (9, 10): (
        "If the ninth lord is in the tenth house the native will become very famous and powerful. He will be "
        "generous and occupy posts of authority. He will earn much wealth and acquire every kind of comfort "
        "and luxury. His means of livelihood will be righteous and he will be a law abiding citizen."
    ),
    (9, 11): (
        "The native will be exceedingly rich. He will have powerful and influential friends. His father will "
        "be a well-known and well-placed man. If afflicted unfaithful friends will destroy the natives "
        "wealth through selfish scheming and fraud."
    ),
    (9, 12): (
        "The position of the lord of the ninth house in the twelfth house gives a poor background. The "
        "native will suffer much and will have to work very hard in life. Even then success may not come to "
        "him. He will be religious and noble but always in want. Father may die early leaving the native "
        "penniless."
    ),

    # ── House 10 Lord ────────────────────────────────────────────────────────
    (10, 1): (
        "When the lord of the tenth house occupies the Ascendant the native rises in life by sheer dint of "
        "perseverance. He will be self-employed or pursue a profession of independence. When the Lagna and "
        "10th lord combine in the first house the native becomes very famous and a pioneer in his field of "
        "work. He founds a public institution and engages himself in social projects."
    ),
    (10, 2): (
        "The 10th lord in the second house makes the native fortunate. He rises well in life and makes a lot "
        "of money. He may engage himself in the family trade and develop it. If malefics afflict the 10th "
        "house he will suffer losses and be responsible for winding up the family business. He will prosper "
        "in catering and restaurant businesses."
    ),
    (10, 3): (
        "The native may have to travel constantly on short-journeys. He will be a speaker or writer of "
        "celebrity if the 10th lord is well-placed. His brothers may be instrumental to some extent in "
        "advancing his career. If 10th lord is in the 6th 8th or 12th from Navamsa Lagna or in an "
        "unfriendly constellation in the 3rd house the natives rise in life is slow and beset with "
        "obstacles. If the 3rd lord is also afflicted rivalry between brothers may lead to reversals "
        "obstacles etc in the natives career."
    ),
    (10, 4): (
        "The native will be a lucky man and highly learned in various subjects. He will be famous both for "
        "his learning and generosity. If the 10th lord is strong the native is respected wherever he goes "
        "and he receives royal favour. He may engage in agricultural pursuits or in dealings with immovable "
        "properties. If the 4th lord the 9th lord and the 10th are beneficially disposed and related to one "
        "another the native wields great political authority as a president or head of a government. If the "
        "10th lord is depressed eclipsed in an inimical sign or afflicted by malefic planets the native will "
        "lose his lands and be forced to take to a life of servitude."
    ),
    (10, 5): (
        "The native shines well as a broker and engages in speculation and similar business. If benefics "
        "join the lord of the 10th in the 5th house the native leads a simple and pious life engaging "
        "himself in prayers and pious activities. He may become the head of an orphanage or remand home if "
        "the 10th lord occupies the 6th 8th or 12th Navamsa."
    ),
    (10, 6): (
        "The person will have an occupation bearing on judiciary prisons or hospitals. If Saturn aspects "
        "the 10th lord he may have to work all his life in a low-paying job with not much prospects. If "
        "benefics aspect the 10th lord he holds a post of authority and will be held in high esteem for his "
        "character. If Rahu or afflicted malefics are with the 10th lord he may suffer disgrace in his "
        "career. He may be exposed to criminal action and face imprisonment."
    ),
    (10, 7): (
        "The 10th lord placed in the 7th house gives a mature wife who will assist the native in his work. "
        "He will travel abroad on diplomatic missions. He will be well known for his skill in talking and "
        "achieving objectives. He will make profits through partnerships and co-operative ventures. If "
        "malefics afflict the 10th lord the native will be debased in his sexual habits and indulge in "
        "every kind of vice."
    ),
    (10, 8): (
        "The native has many breaks in career. If the 10th lord is fortified he will occupy a high office "
        "in his field but only for a short time. If a malefic planet afflicts the 10th lord the person has "
        "criminal propensities and commits offences. If Jupiter influences the 10th lord by aspect or "
        "association in the 8th house he will become a mystic or spiritual teacher. Saturn here makes the "
        "person an undertaker or otherwise employed in burning ghats graveyards etc."
    ),
    (10, 9): (
        "The 10th lord in the 9th house makes the native a spiritual stalwart. He will be a beacon light to "
        "spiritual seekers if Jupiter aspects the 10th lord. If both benefics and malefics aspect the 10th "
        "lord the native is generally fortunate and well-to-do. He follows a hereditary profession or that "
        "of a preacher teacher or healer. The father of the native has a great influence on him. He will be "
        "a dutiful son and do many charitable deeds."
    ),
    (10, 10): (
        "If the 10th lord is strongly disposed in the 10th the native can be highly successful in his "
        "profession and command respect and honour. If the lord is weak and afflicted he will have no "
        "self-respect cringing for favours. He will also be a dependent all his life. He will be "
        "fickle-minded. If the 10th lord occupies the 6th 8th or 12th houses from Navamsa the natives "
        "career will be routine and ordinary. If three other planets conjoin the 10th lord in the 10th "
        "house the native becomes an ascetic."
    ),
    (10, 11): (
        "The person earns immense riches. Fortunate in every respect he will engage himself in meritorious "
        "deeds. He will give employment to hundreds of persons and will be endowed with a high sense of "
        "honour. He will have many friends. If the eleventh house comes under affliction his friends will "
        "turn enemies and cause him every sort of hardship and worry."
    ),
    (10, 12): (
        "If the 10th lord occupies the twelfth house the native will have to work in a far-off place. He "
        "will lack comforts and face many difficulties in life. If beneficially disposed the native becomes "
        "a spiritual seeker. He will be separated from his family and wander about without success if "
        "malefics afflict the 10th lord. He will indulge in smuggling and other nefarious activities. Rahu "
        "afflicting the 10th lord makes the native a cheat and a criminal. He causes sorrow to his family "
        "and relatives."
    ),

    # ── House 11 Lord ────────────────────────────────────────────────────────
    (11, 1): (
        "The native will be born in a rich family. He will earn much wealth. According as the 11th lord in "
        "Lagna is strong middling or weak the native will be born in a very rich fairly rich or well-to-do "
        "family. He will lose an elder brother early in life."
    ),
    (11, 2): (
        "The native will live with his elder brothers. Benefics there give harmonious relations. Malefics "
        "cause domestic bickerings but common residence. The native will earn through commercial concerns "
        "and banking business. Business with friends will bring good profits but if malefics join the native "
        "may suffer heavy losses on account of friends."
    ),
    (11, 3): (
        "The person will be a concert-singer or musician and will earn thereby. Gain through brothers is "
        "also indicated. He will have many friends and helpful neighbours. Afflictions give contrary results."
    ),
    (11, 4): (
        "One acquires profits through landed estates rentals and products of the earth. His mother will be "
        "a cultured and distinguished lady. He will be renowned for his learning and scholarship of various "
        "subjects. He will live in comfort and enjoy all joys in life. He will have a devoted and charming "
        "wife."
    ),
    (11, 5): (
        "The native will have many children who will come up well in life. He will indulge in speculation "
        "and gain much money. If the 11th lord is afflicted he will be a gambler and indulge in foolish "
        "ventures. If 11th lord is beneficially disposed the native will be pious and observe many resolves "
        "and vows which will enhance his prosperity."
    ),
    (11, 6): (
        "The person gains money through maternal relatives litigation and running nursing-homes. If the 11th "
        "lord is afflicted in the 6th the native thrives on setting person against person involving himself "
        "in other peoples quarrels and anti-social activity. If malefics afflict the 11th lord the native "
        "may lose through similar sources."
    ),
    (11, 7): (
        "The person marries more than once. He prospers in foreign countries. If there are afflictions to "
        "the 11th lord the native carries on liaisons with women of ill-repute. He will indulge in trading "
        "in flesh and similar immoral activities. If the 11th lord is fortified the native marries only once "
        "but a rich and influential woman."
    ),
    (11, 8): (
        "The native though rich at birth suffers many calamities and loses much of his money. He will suffer "
        "from the depredations of thieves cheats and swindlers. If the 11th lord occupies a malefic "
        "constellation the native will be forced to eke out his living by begging."
    ),
    (11, 9): (
        "He inherits a large paternal fortune and will be very lucky in life. He will possess many houses "
        "conveyances and every other kind of luxury. He will be religious-minded and disseminate religious "
        "literature. He will be charitable and set up charitable institutions."
    ),
    (11, 10): (
        "The native prospers very well in his business and makes good profits. His elder brother will also "
        "help him in his business. He will earn some prize-money for original contributions to the subject "
        "of his study or profession. Depending upon the benefic or malefic nature of the planet he will "
        "earn through fair or foul means."
    ),
    (11, 11): (
        "The native will have many friends and elder brothers who may help him throughout life. He will have "
        "a happy life with the blessings of wife home children and comforts."
    ),
    (11, 12): (
        "He will suffer losses in business. His elder brother will be ailing and much expenditure will be "
        "incurred on account of his illness. The native may also lose an elder brother by death. He will "
        "have to pay fines and penalties frequently and will be burdened with many domestic "
        "responsibilities."
    ),

    # ── House 12 Lord ────────────────────────────────────────────────────────
    (12, 1): (
        "The native will have a weak constitution and will be feeble-minded. He will however be handsome "
        "and sweet-tongued. If the sign is common the native will generally be travelling about. If the 6th "
        "lord joins the 12th lord in Lagna the native will live long. But if the 8th house is afflicted he "
        "will be short-lived. This also indicates imprisonment and living abroad. If the Lagna and 12th "
        "lords exchange signs the native will be a miser hated by all and devoid of intelligence."
    ),
    (12, 2): (
        "The person will suffer financial losses. He may contact debts and get involved in nefarious "
        "activity. He will not eat timely meals. His eye-sight will be poor and his family life marked by "
        "lack of harmony. If the twelfth lord is a benefic and in dignity these evil indications will be "
        "greatly reduced and the native will have financial stability. He will be a tactful speaker. If the "
        "twelfth lord is ill-disposed the native indulges in gossip and quarrelling."
    ),
    (12, 3): (
        "He will be timid and quiet. Loss of a brother is shown. He will be shabbily dressed. If malefics "
        "afflict he may develop ear-ailments. He may have to spend much money on younger brothers. As a "
        "writer he may be unsuccessful. He may work in some commonplace job and earn very little. If the "
        "12th lord joins the 2nd lord in the 3rd and is aspected by Jupiter or the 9th lord one may have "
        "more than one wife."
    ),
    (12, 4): (
        "Early death to mother mental restlessness unnecessary worry enmity of relatives and living abroad "
        "are some of the results. Suffering constant harrassment from the landlord his residence will be in "
        "an ordinary house. But if the twelfth lord is well placed these adverse indications get mitigated "
        "to a large extent. If Venus is strong the native may own his own conveyance but it will always "
        "give trouble."
    ),
    (12, 5): (
        "Either difficulty to beget progeny or unhappiness from children will be experienced. He will be "
        "religious-minded and may undertake pilgrimages. Weak-minded and suffering mental aberrations he "
        "feels he is miserable. He will not succeed in agriculture as his crops will suffer from pests and "
        "disease."
    ),
    (12, 6): (
        "The native will be happy and prosperous live long enjoy many comforts possess a healthy and "
        "handsome physique and vanquish his enemies. But he may become involved in litigation which may "
        "come to an end to his advantage. But if malefics afflict the 12th lord the person will be "
        "unscrupulous sinful and ill-tempered hating his mother suffering from unhappiness on account of "
        "his own children. Womanising will land him in distress."
    ),
    (12, 7): (
        "The wife may come from a poor family. Married life will be unhappy and may end in separation. "
        "Later on he will take to asceticism. Weak in health and suffering from phlegmatic troubles he will "
        "be without learning or property."
    ),
    (12, 8): (
        "The native will be rich and celebrated will enjoy a luxurious life with many servants waiting on "
        "him. Gain through deaths and legacy is indicated. Interested in occult subjects and devoted to "
        "Lord Vishnu he will be righteous famous and a gentle speaker being endowed with many good qualities "
        "of head and heart."
    ),
    (12, 9): (
        "Residence abroad and prosperity are shown. He may acquire much property in foreign lands. Honest "
        "generous and large-hearted he may not have any spiritual leanings. Not liking his wife friends and "
        "preceptor and interested in physical culture he loses his father early in life."
    ),
    (12, 10): (
        "Hard-working and having to undertake tedious journeys for his occupation he will be a jailor doctor "
        "or work in the cemetery and such places. He spends money on agricultural pursuits in which he makes "
        "profits. The native will derive no happiness or physical comforts from his sons."
    ),
    (12, 11): (
        "He will engage himself in business but does not make much profit. He has few friends but many "
        "enemies. Troubled by extravagant brothers some of whom may be invalids the natives funds may "
        "dwindle on this account. He will earn well by trading in pearls rubies and other precious stones."
    ),
    (12, 12): (
        "The native spends much on religious and righteous purposes. He will have good eye-sight and enjoy "
        "pleasures of the couch. He will be engaged in agriculture. If malefics afflict the twelfth lord "
        "the native will be restless and always roaming about."
    ),
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_house_lord_in_house_interpretation(birth_time: AstroTime, lord_house: int) -> dict:
    """Return the interpretation for a single house lord's placement.

    Args:
        birth_time: Birth AstroTime.
        lord_house: The house whose lord we are examining (1–12).

    Returns:
        dict with keys: lord_house, lord_planet, placement_house, description.
    """
    lord_planet: Planet = get_lord_of_house(lord_house, birth_time)
    placement_house: int = get_planet_house(lord_planet, birth_time)
    description = _HOUSE_LORD_IN_HOUSE_DATA.get((lord_house, placement_house), "")
    return {
        "lord_house": lord_house,
        "lord_planet": lord_planet.name,
        "placement_house": placement_house,
        "description": description,
    }


def get_all_house_lord_in_house_interpretations(birth_time: AstroTime) -> List[dict]:
    """Return interpretations for all 12 house lords.

    Args:
        birth_time: Birth AstroTime.

    Returns:
        List of 12 dicts, one per house lord (houses 1–12).
    """
    return [get_house_lord_in_house_interpretation(birth_time, h) for h in range(1, 13)]
