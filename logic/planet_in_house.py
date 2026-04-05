"""Planet-in-House (Natal) Interpretations.

For each of the 9 planets in each of the 12 natal houses this module
provides the classical Vedic interpretation text sourced from
VedAstro C# HoroscopeDataListStatic.cs (EventTag.Personal).

Lookup key: (planet_name: str, house_num: int) -> str description
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from .time import AstroTime
from .consts import Planet
from .house_queries import get_planet_house

# ---------------------------------------------------------------------------
# Data table: (planet_name, house_num) -> description
# ---------------------------------------------------------------------------

_PLANET_IN_HOUSE_DATA: Dict[Tuple[str, int], str] = {

    # ── House 1 ─────────────────────────────────────────────────────────────
    ("Sun", 1): (
        "Strong moral nature righteous-minded ambition and love of power tends to be well supported by good "
        "health and vitality. Cheerfulness and an optimistic temperament help to ensure popularity. It adds "
        "respect to the personality and gives lofty motives. If with Saturn or Mars it indicates scars and a "
        "hot constitution. The blood becomes impure and there will be itches all over the body. Fevers "
        "inflammations and eye affections may also be anticipated."
    ),
    ("Moon", 1): (
        "The native becomes fanciful and romantic a moderate eater. Considerable restlessness is usually "
        "tempered by an easy-going disposition. The fortune is generally changing. It makes one an idealist "
        "a great traveller and explorer. If with Saturn the mind will always be worried. If Mars is with the "
        "Moon it indicates menstrual disorders in the case of women. Sociability tends to be a strong feature. "
        "He will be successful in professions that bring him into contact with the masses. The Moon in Lagna "
        "with Rahu indicates hysterical tendencies and with Jupiter the mind is elevated."
    ),
    ("Mars", 1): (
        "This gives a hot constitution courage self-confidence and enterprise. The native will possess "
        "practical ability and love of liberty and independence. He becomes reckless of danger scorning defeat. "
        "This gives somewhat of a rash nature. The body will have scars and the appearance will be handsome. "
        "The domestic life will be unhappy unless there are other favourable combinations. Abuse of physical "
        "resources may lead to ill-health. There is a proneness to accidents. The aspects should be carefully "
        "examined. Danger of cuts burns etc. are likely."
    ),
    ("Mercury", 1): (
        "This position makes the subject humorous. Quickness of wit and mental ingenuity tend to be strongly "
        "marked. The native becomes well-read particularly in occult studies. In good aspect to Venus it makes "
        "one musical and talented. Adaptability is a striking feature. Mercury makes the man intellectual. If "
        "there is a Rahu or Ketu in Lagna the native suffers a lot of nervous troubles."
    ),
    ("Jupiter", 1): (
        "A magnetic personality is bestowed on the native. An optimistic spirit jovial disposition and pleasant "
        "manners are indicated. The native will have more sons if the 5th house is not affected. "
        "Self-indulgence especially in regard to gluttony will affect health. If with Rahu sins will be "
        "committed. Body will be inclined towards corpulence. Lawyers professors writers theologians etc. come "
        "under this planet. The man becomes an influential leader. Diseases may result from impure blood."
    ),
    ("Venus", 1): (
        "This is a fortunate combination more so if the ascendant happens to be Capricorn or Aquarius. The "
        "native will possess amiability and a cheerful temperament responsive to the emotional side of nature. "
        "It gives an appreciation of art. There will be craving for pleasure. Passions will be pronounced. The "
        "native will take interest in music drama and singing. There will be a fondness for scents flowers etc. "
        "Those born in this sign will be admired by the opposite sex. Generally a good fortune is denoted. Fond "
        "of wife or husband the native will have a magnetic and attractive personality. Marriage may take place "
        "early. If afflicted it indicates discord in married life."
    ),
    ("Saturn", 1): (
        "Foreign customs will be easily copied and imitated. But if Saturn is not afflicted there will be much "
        "consideration for the welfare of others. Self-confidence is normally justified. Moral stability will "
        "also be marked. The disposition is calm grave and serious. The body will be weak and emaciated. "
        "Progress in any venture will be slow but certain. There may be some aversion for responsibility. This "
        "position of Saturn makes habits inactive. Loss through negligence and lack of opportunity are possible. "
        "The same results will be noticed if the ascendant is aspected by Saturn. Misfortunes are likely in the "
        "early part of life."
    ),
    ("Rahu", 1): (
        "The health will be generally unsatisfactory calling for treatment other than by medical methods. It "
        "inclines one to the occult and the serious wilfulness of nature is well marked. A hypocritical "
        "super-consciousness towards others is likely. It makes one appear rather odd and eccentric. This "
        "combination is usually bad for marriage. Rahu will generally partake of the characteristics of Saturn."
    ),
    ("Ketu", 1): (
        "Psychic powers are likely. It denotes a weak constitution and an emaciated figure. Instability and "
        "deceitfulness may influence the character. Morbid imagination strange appetites tendency to "
        "excitability and wandering disposition become pronouncedly marked. Married life will be unhappy unless "
        "there are other favourable configurations."
    ),

    # ── House 2 ─────────────────────────────────────────────────────────────
    ("Sun", 2): (
        "This is not quite a favourable situation. Losses will occur by offending the authorities. He will "
        "have a diseased face. He will obtain money by industrious effort. The nature of the income depends on "
        "the nature of the sign. He will be stubborn and peevish."
    ),
    ("Moon", 2): (
        "He will have a large family and will enjoy much happiness. Money will also be obtained through females. "
        "The financial position will be somewhat variable; will have a fair complexion. Dhundiraja a noted "
        "astrological writer of yore says that when the Moon is in the 2nd house the native will be reserved "
        "and not much sociable, squint eyed and much admired."
    ),
    ("Mars", 2): (
        "Becomes quarrelsome. Good earning powers but usually miserly. Much money is accumulated. A good "
        "conversationalist. He will befriend evil-minded persons be unsympathetic and pick up quarrels with all."
    ),
    ("Mercury", 2): (
        "Learned in religious and philosophical lore. Denotes gain by lecturing business and commercial "
        "affairs. Becomes rich. Highly intelligent. He spends money on charities and moral purposes. Clever "
        "in earning money and careful and thrifty."
    ),
    ("Jupiter", 2): (
        "Becomes a poet a great writer astrologer or even a scientist. Increases the chances for success. He "
        "accumulates fortune good wife and family surroundings. He will not quarrel with others. Money will be "
        "acquired through things indicated by the signs ruled by Jupiter."
    ),
    ("Venus", 2): (
        "Large family. Money usually comes readily by favours from others. Eats good food possesses "
        "conveyances. Handsome appearance skilful and pleasant will marry a good wife or husband. Health and "
        "wealth are indicated in a large measure."
    ),
    ("Saturn", 2): (
        "Saturn unless the second is Libra Capricorn or Aquarius tends to make earning an uphill struggle. "
        "Much work with little gain. Harsh speech unsocial sorrowful and roaming about aimlessly the person "
        "comes across many opportunities but seldom takes advantage of them. In family life he will be unhappy. "
        "He will gain by dealing with metals storage mines labour etc. He will be unpopular."
    ),
    ("Rahu", 2): (
        "Peevish diseased face friction in family life danger to eye-sight. Financial affairs uncertain unless "
        "other favourable combinations occur. If Jupiter aspects the second house then earnings will be good. "
        "Money is gained through friends and business."
    ),
    ("Ketu", 2): (
        "Bad speaker. Loss through fraud and deception. There will be liability in financial affairs. Success "
        "in spiritualism navigation mystical arts hospital etc. may be expected."
    ),

    # ── House 3 ─────────────────────────────────────────────────────────────
    ("Sun", 3): (
        "Makes the person courageous. The mind becomes resourceful and restive successful. Bad for brothers "
        "if afflicted. Discredit through letters. Position of the Sun in the 3rd is one of the strong points "
        "in a horoscope."
    ),
    ("Moon", 3): (
        "Generally changes in occupation are indicated fond of travelling and active minded. Wife will be fair. "
        "The subject possesses good knowledge. Rather indifferent to spiritual values of life. Subordinate to "
        "wife. Attached to children. If however the Moon is waning cruel miserable impious and unscrupulous. "
        "An unfavourable position for peace of mind if afflicted."
    ),
    ("Mars", 3): (
        "This position is bad for brothers and sisters. Liability to danger and accidents by journeys. Brave. "
        "Worried on account of family misunderstandings. Reckless pioneering and unprincipled. May be troubled "
        "with ear defects or even deafness. If the house is further afflicted it shows thoughts of suicide or "
        "violent tendencies. If the third is Capricorn Aries or Scorpio the evil effects will be largely "
        "modified."
    ),
    ("Mercury", 3): (
        "Will do good deeds for the benefit of others but he will not himself be happy. The mind is sharp. "
        "Fond of reading and study; when once he undertakes a work he does it to the finish and will never get "
        "discouraged. Tactful and diplomatic. He will befriend businessmen and merchants. He will generally be "
        "successful in trade and speculation. A number of brothers and sisters. Independent views. Liked by "
        "friends and relatives. When Mercury is afflicted the native is inclined to nervous break-down. Gain "
        "through third house affairs."
    ),
    ("Jupiter", 3): (
        "This is also a good position. The mind is optimistic and philosophical. Will have many good brothers. "
        "Becomes a miser. Does not love family and children. The body gets heated and he suffers from "
        "ill-health. He may be devoid of gratitude if Jupiter is afflicted. He does not have many friends. "
        "Does not take advantage of opportunities. Adapts himself to conventionalities."
    ),
    ("Venus", 3): (
        "The mental quality is good but health will be poor lacking in vitality. He will take delight in "
        "singing music dancing and fine arts. Financially he will not be very successful. If Venus is "
        "afflicted miserly mean poor and highly sensual. He becomes funky and interested in scandals. Brothers "
        "will be good. Not much happiness from children."
    ),
    ("Saturn", 3): (
        "Brave and courageous wealthy loss of brothers eccentric and cruel. Sorrow through brothers; honoured "
        "by rulers; may become head or president of local boards municipalities etc. He will protect many "
        "people. One peculiarity of this combination is that success attends him only after he has suffered "
        "disappointments and reverses. The tendency of the mind is towards gloom anxiety and misgivings. The "
        "mental condition improves with age. If Saturn is afflicted the despondency is likely to run into "
        "mental affliction."
    ),
    ("Rahu", 3): (
        "Brave for outward appearances. Sudden and unexpected news. The combination is generally bad for "
        "brothers. He may incur severe criticism on account of his views and ideas."
    ),
    ("Ketu", 3): (
        "Strong and adventurous but funky. Disturbs the mind with hallucinations."
    ),

    # ── House 4 ─────────────────────────────────────────────────────────────
    ("Sun", 4): (
        "This combination is said to make one generally unhappy and mentally worried. He will be roaming "
        "about. The position promises some inheritance. He will have interest in occult and philosophical "
        "studies. In the political field success is difficult. Obstacles in life are shown if Saturn or Mars "
        "aspects the Sun."
    ),
    ("Moon", 4): (
        "Possesses house; derives happiness from relatives; will be cheerful and contented; becomes important "
        "as a leader or ruler; proud and somewhat quarrelsome. The position indicates early separation from "
        "the mother if the Moon is afflicted; will be fond of sensual pleasures unless aspected by Jupiter."
    ),
    ("Mars", 4): (
        "This is generally a bad combination. The person will be deprived of happiness from mother relations "
        "and friends but will have success in the political line. There will be quarrels with mother and "
        "domestic affairs go awry. If Mars joins Rahu or Ketu the man will have a tendency for suicide. The "
        "person will own houses but will not be happy on that account."
    ),
    ("Mercury", 4): (
        "Shines well as an educationist or diplomat. He will boldly criticise the Government. He will be held "
        "in great esteem. Father will be a self-made man. He will command a good conveyance. He will have "
        "taste for music and other fine arts and will frequently travel to far off countries. He will be witty "
        "in speech."
    ),
    ("Jupiter", 4): (
        "Philosophically inclined learned happy possesses the favour of the ruling class a terror to his "
        "enemies religiously inclined respected and fortunate peaceful domestic environments great spiritual "
        "advancement."
    ),
    ("Venus", 4): (
        "Well versed in music polished manners deep attachment to mother many friends conveyances and houses "
        "religious by inclination successful achievement of desires. This is a favourable yoga for affairs of "
        "a domestic nature concord and happiness."
    ),
    ("Saturn", 4): (
        "Sickly during early years deprived of mother and unhappy suffers from windy and phlegmatic complaints "
        "lethargic temperament will not inherit any property will have troubles from houses and vehicles "
        "disliked by relatives desire to live a very secluded life unfavourable for domestic or family affairs "
        "unless beneficially aspected or associated."
    ),
    ("Rahu", 4): (
        "Foolish in behaviour few friends will be subjected to fraud or guilty of fraudulent action."
    ),
    ("Ketu", 4): (
        "Will be deprived of mother properties and happiness; lives in a foreign place. There will be "
        "exceptional experiences at the end of life. There will be reversals and sudden changes."
    ),

    # ── House 5 ─────────────────────────────────────────────────────────────
    ("Sun", 5): (
        "This combination deprives the person of children riches and happiness. His life will be short. He "
        "will suffer from heart disease; will roam about in forest regions; a mountaineer. This position also "
        "denotes difficult child-birth."
    ),
    ("Moon", 5): (
        "Clarity of mind happiness from children acquisition of lands gems and precious stones opportunity to "
        "serve the State are indicated when the Moon is in the 5th. The person will be straightforward "
        "truthful learned gentlemanly god-fearing and devoid of enemies. Strong tendency towards speculation "
        "is also denoted. One of the children becomes famous."
    ),
    ("Mars", 5): (
        "Miserable for his wife friends and children; always disturbed in thoughts; impressive rash "
        "weak-minded back-biter and unhappy. He will suffer from colic and suffers misfortunes through "
        "children. Too much attached to sex pleasures and consequently loss of health. Dangerous child-birth "
        "may be predicted in a woman's chart."
    ),
    ("Mercury", 5): (
        "Learned and happy will have a number of children. The person may become an adviser or a minister; "
        "highly intelligent and learned in Mantrasastras; inclined to too much of sex pleasure and "
        "consequently lacking in vitality."
    ),
    ("Jupiter", 5): (
        "Learned in logic and law mantrasastra highly intelligent preceptor or adviser to a king and great "
        "discriminating power. He will have good friends and vehicles and decorous manners. A number of "
        "children; god-fearing; happy with children and friends."
    ),
    ("Venus", 5): (
        "Poetic possesses a number of friends and beautiful children; happiness through offspring; wise and "
        "discriminating acquires wealth; respected by the State. This position also indicates more of female "
        "children and success in speculation."
    ),
    ("Saturn", 5): (
        "Evil-minded and stupid; sickly and weak poor and hated by others. This combination denotes sorrows "
        "through children. Fortune will be variable and not steady and he will have a hypocritical nature. "
        "Quarrels with friends and relatives and sorrow in domestic life."
    ),
    ("Rahu", 5): (
        "Suffers from colic mistaken by others and unfriended will lose a number of children hard-hearted and "
        "unconventional heart trouble."
    ),
    ("Ketu", 5): (
        "Loss of children trouble in the stomach strange and peculiar experiences in connection with emotions "
        "and feelings. Later on in life inclination towards spirituality."
    ),

    # ── House 6 ─────────────────────────────────────────────────────────────
    ("Sun", 6): (
        "The person becomes a good politician famous and successful. Not very good for health. Sun afflicted: "
        "long and troublesome illness. Sun fortified: good administrative ability few enemies wealthy and "
        "generally successful in all endeavours. Affliction by Saturn is not desirable as it indicates "
        "heart-trouble or frequent chest pain unless the affliction is relieved by Jupiter's aspect."
    ),
    ("Moon", 6): (
        "Indicates Balarishta or much ill-health during early childhood. Affliction by Mars and Saturn: "
        "curious and incurable diseases and revengeful enemies. Moon strongly denotes ability and success in "
        "subordinate positions. If the sixth is a fixed sign the person will suffer from stone in the bladder; "
        "he will be submissive to women; weak sexual connection and stomach troubles. Afflicted in common "
        "signs danger from lung troubles. He will have success as a caterer."
    ),
    ("Mars", 6): (
        "Highly passionate victorious and successful as a ruler or politician. He will have worries from near "
        "relatives. Mars afflicted: accidents losses and troubles through employees. If Saturn is the "
        "afflicting planet death may be due to operation or injury by animals. If Rahu afflicts Mars death "
        "may be due to suicide. If Ketu he will die by poisoning."
    ),
    ("Mercury", 6): (
        "Quarrelsome and showy but yet respected; interrupted education. If afflicted mental troubles and "
        "danger of nervous breakdown. If afflicted by Mars and Rahu or Saturn and Rahu there is danger of "
        "insanity through excitement troubles with servants and a tendency to poor health. The person will be "
        "lazy harsh in speech but nevertheless a terror to his enemies."
    ),
    ("Jupiter", 6): (
        "Inactive suffers disrespect indulges in black magic feared by enemies unlucky dyspeptic; health "
        "generally good. If afflicted health suffers through overindulgence."
    ),
    ("Venus", 6): (
        "No enemies; corrupted by young women; favourable for getting favours from women. If afflicted: health "
        "affected by too much sexual indulgence fond of other women and licentious."
    ),
    ("Saturn", 6): (
        "Quarrelsome obstinate voracious eater foeless courageous. If afflicted sickness through privation or "
        "neglect troubles through subordinates. If Mars is the afflicting planet dangerous illness and "
        "operations. If Rahu afflicts the person suffers from hysteria. Saturn well-aspected denotes gains "
        "through contract work mining masonry etc."
    ),
    ("Rahu", 6): (
        "Long-lived and wealthy troubled by enemies ghosts and diseases in private parts. He will also suffer "
        "from sickness of a puzzling nature. There is also liability to mental derangement if the Moon and "
        "Saturn join Rahu. The person will have many cousins and his private life will be scandalous."
    ),
    ("Ketu", 6): (
        "The best position for Ketu to occupy in a horoscope. The person will have fame and authority. He will "
        "be foeless. Nevertheless his moral character will be loose. The position also confers intuitive and "
        "occult powers."
    ),

    # ── House 7 ─────────────────────────────────────────────────────────────
    ("Sun", 7): (
        "The native will be fair and have thinning hair. He will have few friends and finds difficulty in "
        "getting along with people. Marriage is delayed and troubled. Fond of travelling he will have loose "
        "morals. He likes foreign things. His wife's character will be questionable and the native will run "
        "the risk of loss and disgrace through women. He will incur the displeasure of the Government and "
        "suffer humiliation. He will be deformed."
    ),
    ("Moon", 7): (
        "The native will be passionate and easily roused to jealousy. Mother may die while the native is "
        "young. Wife will be good-looking but the native will seek other women. Narrowminded but sociable he "
        "will be energetic and successful in life. He hails from a good family if the Moon is waxing and "
        "otherwise strong. He will suffer pain in the groins. He will be stingy. If the Moon is waning he "
        "will always be quarrelling with his enemies."
    ),
    ("Mars", 7): (
        "The native will be hen-pecked by his wife and submissive to women. Married life will have clashes "
        "and tensions or there may be two wives. The native will be rash and indulge in speculation. He will "
        "be intelligent tactless stubborn peevish and unsuccessful."
    ),
    ("Mercury", 7): (
        "A man of virtue and geniality he will dress well and tastefully. He will have profound knowledge of "
        "law. He will be skilled in business and trade tactics. He will have writing ability and success "
        "through it early in life. Early marriage to a rich woman. Learned in mathematics astrology and "
        "astronomy he will be religious and of a devout temperament. Diplomatic but if afflicted the native "
        "will be cunning and deceitful. He will have a good physique and looks."
    ),
    ("Jupiter", 7): (
        "Diplomatic and kind-hearted the native gets a virtuous good-looking and chaste wife. He will get "
        "good education and gains through marriage. He will be sensitive to others' feelings. He has a "
        "speculative mind and is a good agriculturist. He undertakes pilgrimages to distant places and is "
        "superior to father in his qualities. The native will possess good sons."
    ),
    ("Venus", 7): (
        "Fond of quarrelling sensuous and passionate the native has unhealthy habits and a happy marriage and "
        "devoted wife. He is fond of pleasure and drink is suave and charming with winning manners. He has a "
        "magnetic personality. He has danger of loss of virility due to disease or excesses. He is successful "
        "in partnership with those of the opposite sex."
    ),
    ("Saturn", 7): (
        "The native will be under the wife's control. The wife will be ugly or hunch-backed. He will have "
        "more than one marriage or marriage with a widow divorcee or one advanced in age. He will be "
        "diplomatic and enterprising. He has residence abroad a stable marriage and political success. He "
        "will get honour and distinction in foreign lands; suffers from colic pains and deafness."
    ),
    ("Rahu", 7): (
        "The native brings ill-repute to family if a female. He will be unconventional and heterodox. He "
        "will have affairs with outcaste women or foreigners. His wife suffers from womb disorders. He eats "
        "good and rich food has luxurious habits and suffers from diabetes ghosts and the supernatural."
    ),
    ("Ketu", 7): (
        "The native has an unhappy marriage with a shrewish wife. He is passionate sinful lusts after widows. "
        "His wife is sickly. The native suffers from cancer in the abdomen or uterus if a female. He will "
        "suffer humiliation and loss of virility."
    ),

    # ── House 8 ─────────────────────────────────────────────────────────────
    ("Sun", 8): (
        "If the Sun occupies the 8th house in exaltation the native lives long. He will be charming and an "
        "eloquent speaker. If the Sun is afflicted he will be troubled with sores in the face and head and be "
        "disgruntled in life. His eyes will be weak. He will suffer penury and an uneventful life. If "
        "associated with the 8th or 11th lord he may gain monetary benefits all of a sudden through "
        "speculation. He will have limited progeny mostly male. If the Sun is in the 8th the Moon or Rahu is "
        "in the 12th and Saturn is in a trine the native suffers from dental problems."
    ),
    ("Moon", 8): (
        "The native with the Moon in the 8th is subject to mental aberration. He is apprehensive and suffers "
        "from psychological complexes. He will be capricious and unhealthy. The native may lose his mother in "
        "infancy or boyhood. His built will be slender and eyesight will be weak. He acquires possessions "
        "easily through legacies or inheritance. He will be fond of fighting and amusement and be "
        "large-hearted. The native suffers from excessive perspiration; if Mars and Saturn conjoin and the "
        "Moon is in the 8th house the native's eyesight will be afflicted."
    ),
    ("Mars", 8): (
        "The native will be short-lived unless there are other alleviating factors and he may suffer the loss "
        "of wife or husband. He will have very few children. He may seek to gratify his passions by resorting "
        "to extra-marital life. He will hate his relatives. His domestic life will be marred by quarrels and "
        "he suffers from bloody complaints like piles. He will rule over many people. If Mars is in the 8th "
        "the Lagna is a fixed sign Venus is in the 9th the Moon is in the 7th and Jupiter is the 2nd lord "
        "the native will be condemned to lead a life of servitude."
    ),
    ("Mercury", 8): (
        "When Mercury is in the 8th the native will possess many good qualities. He will be known for his "
        "breeding and courteous disposition. He will inherit as well as earn much wealth. He will be learned "
        "and famous for his scholarship in many subjects. He will live long but have a weak constitution."
    ),
    ("Jupiter", 8): (
        "The native will be unhappy but generous hearted. He will live long. He will have difficulty in "
        "speech. He may do ignoble deeds but pretend to be noble. He may have liaisons with widows. He will "
        "have dirty habits and suffer from colitis. He will have a painless death. If Jupiter is debilitated "
        "and the Moon is in the 4th house from Lagna the native will be a menial being always ordered about."
    ),
    ("Venus", 8): (
        "The position of Venus in the 8th gives many blessings. The native will come by much wealth. He will "
        "live a life of comfort and possess all the conveniences for such life. The native's mother may suffer "
        "danger. The native himself may meet with emotional disappointments early in life. As a consequence he "
        "may resort to a life of piety in later life. If exalted in the 8th the native gains much wealth. If "
        "Venus in the 8th is debilitated in Rasi or occupies a saturnine Navamsa and is aspected by Saturn "
        "the native suffers subordination and leads a life of drudgery along with his mother."
    ),
    ("Saturn", 8): (
        "Saturn in the 8th house gives good longevity but many responsibilities in life. The native will "
        "discharge his duties through sheer perseverance against odds which will be many. He will have "
        "defective eyes. He will have very few children. He will have a paunch and be inclined to seek the "
        "company of women outside his caste. He may be predisposed to suffer from asthma consumption and "
        "lung disorders. If afflicted by malefic planets his children will cause him pain and grief. The "
        "native will be dishonest and cruel. When Saturn is in the 8th with Mars Rahu is in Lagna and Gulika "
        "occupies a trine the native suffers disease in his generative organs. If the Moon joins Saturn in "
        "the 8th the result is flatulence and spleen troubles."
    ),
    ("Rahu", 8): (
        "The native will suffer from public censure and humiliation. He will be troubled by many ailments. He "
        "will be vicious quarrelsome and unscrupulous. If the Moon conjoins with a malefic planet and Rahu "
        "is in the 8th 12th or 5th house the native will suffer from mental disorders."
    ),
    ("Ketu", 8): (
        "If Ketu in the 8th is aspected by a benefic the native will enjoy much wealth and live long. If Ketu "
        "is afflicted the native covets others' wealth and women. He will suffer from diseases due to "
        "disorders in the excretory system and also those due to a life of profligacy and excesses."
    ),

    # ── House 9 ─────────────────────────────────────────────────────────────
    ("Sun", 9): (
        "The native may change his faith if the Sun is afflicted. He displays hostile feelings towards his "
        "father lacking respect for elders and spiritual preceptors. But if the Sun is not afflicted the "
        "person will be a dutiful son having regard for spiritual pursuits. The Moon combining with the Sun "
        "here causes eye troubles; Venus with the Sun gives sickness and ailments. The health will be "
        "ordinary and the native gets little patrimony. He will be ambitious and enterprising."
    ),
    ("Moon", 9): (
        "The native will be fortunate and prosperous. He will have many sons friends and kinsmen. He will be "
        "principled and generous-minded. If Saturn Mars and Mercury aspect the Moon the native will become a "
        "ruler. If the Moon combines with Mars he may cause a fatal injury to his mother. If Venus conjoins "
        "the Moon in the 9th the person may lead an immoral life. He will act in league with his step-mother. "
        "Saturn here causes one to suffer much. The native may build charitable institutions. He will acquire "
        "good immovable property and also visit foreign countries."
    ),
    ("Mars", 9): (
        "The native will wield authority and be affluent. He will have children and be happy. He will not be "
        "a dutiful son but otherwise generous and famous for his good qualities; if either Jupiter or Mercury "
        "conjoin Mars the native will be learned in religion and spiritual lore. Venus here gives two wives "
        "and foreign residence; it also gives the native proficiency in law. Saturn with Mars in the 9th "
        "indicates addiction to other women and a wicked nature. He will be self-seeking stubborn and "
        "impetuous."
    ),
    ("Mercury", 9): (
        "The native will acquire much education and wealth. He will be a great scholar. He will be interested "
        "in theosophy and metaphysics. He will have a scientific mind and fond of music and pleasure if Venus "
        "joins Mercury. Jupiter with Mercury in the 9th confers wit and wisdom. He may travel abroad on "
        "invitations and be invited to lecture in educational institutions. Relations with father will be "
        "friendly and happy."
    ),
    ("Jupiter", 9): (
        "The native may become an exponent of law philosophy etc. If Jupiter is aspected by benefic planets "
        "he acquires much immovable property. He will be fond of his brothers; if the Moon and Mars influence "
        "Jupiter he will become a great military leader or commander; if the Sun and Venus join Jupiter the "
        "native becomes characterless. Jupiter beneficially aspected by Saturn makes the native live a life "
        "of austerity and strive for divine communion. He may visit foreign lands as a lecturer preacher etc. "
        "He will be conservative and principled."
    ),
    ("Venus", 9): (
        "The native is born fortunate and endowed with fame learning children wife and generally every kind "
        "of happiness. The Sun with Venus makes one suave and polished in speech but one may suffer from many "
        "physical complaints. Venus with Saturn makes the person a diplomat or otherwise engaged in similar "
        "work under a king or government. He will be well known for his balanced views on men and matters. "
        "Venus with the Sun and Moon may involve the person in quarrels with women resulting in loss of money. "
        "The Sun and Saturn with Venus give criminal tendencies and the person may face conviction. He can "
        "also be notorious as a libertine."
    ),
    ("Saturn", 9): (
        "The native will lead a lonely life and may not marry. He will be well known for his valour on the "
        "battle field. The Sun with Saturn causes serious conflicts with the father and also with his own "
        "children. He may suffer from growths or lumps in the stomach. Mercury with Saturn makes the native "
        "untruthful and deceitful although he may be wealthy. Thrifty in domestic life somewhat irreligious "
        "he may become a founder of charitable institutions."
    ),
    ("Rahu", 9): (
        "The native will have a nagging and domineering wife. He will be impolite and miserly suffering from "
        "emaciation and generally inclined to be of loose morals. He will hate his father and revile God and "
        "religion. But he may become famous and acquire much wealth."
    ),
    ("Ketu", 9): (
        "The native will be short-tempered and may get upset over trifles. He will be eloquent but employ "
        "this ability to scandalize others. Fond of pomp and show haughty and arrogant he will however be "
        "valorous. Often treating his parents badly and generally hostile towards them he will be "
        "short-sighted but save much money through frugal living. He will have a good wife and children."
    ),

    # ── House 10 ────────────────────────────────────────────────────────────
    ("Sun", 10): (
        "The native is successful in all that he undertakes. He will be strong and happy. He will have sons "
        "vehicles fame intelligence money and power. He will be employed in government service. He will "
        "acquire ancestral wealth. He will be fond of music and have personal magnetism. If Mars associates "
        "with the Sun the native becomes addicted to vices like drinking etc. If Mercury joins the Sun he "
        "acquires profound knowledge of the sciences. He will be fond of women and ornaments. If Venus joins "
        "the Sun in the 10th house the native gets a rich wife. Saturn with the Sun generally causes sorrow "
        "and dejection."
    ),
    ("Moon", 10): (
        "The native will be religious wealthy intelligent and bold. He will succeed in all his endeavors. He "
        "will obtain corn ornaments women and will be skilled in the arts. He will be of a helpful nature and "
        "virtuous. Jupiter with the Moon makes the native learned in ancient subjects and skilled in "
        "astrology. If Saturn aspects the Moon the native will be a dispassionate thinker but earning through "
        "printing and selling books. He will have many friends and lead a comfortable and long life. He will "
        "be the trustee of religious institutions."
    ),
    ("Mars", 10): (
        "Other combinations favouring the native may become a cruel ruler. He will be fond of praise and may "
        "take bold steps in governing. He will be rash. He will earn much money. If Mercury joins Mars the "
        "person will be a skilled scientist or technician patronised by the rulers. If Jupiter is with Mars "
        "the native becomes the head of low-class people. If with Venus he becomes a trader in foreign lands. "
        "If Saturn and Mars combine in the 10th house he will be daring but will have no progeny."
    ),
    ("Mercury", 10): (
        "He will be a happy and straightforward person. He will be a scholar in many subjects and engaged in "
        "acquiring more knowledge and fame. He will be successful in all his endeavours. He will have "
        "defective eyesight but profound knowledge in astronomy and mathematics. If Venus joins him the "
        "native will have a charming wife and wealth. If Jupiter he will be unhappy and childless but move in "
        "prominent circles of the government. Saturn and Mercury make the native toil in jobs like that of a "
        "copyist or proofreader and suffer penury."
    ),
    ("Jupiter", 10): (
        "The native will be a high official in the government. Rich virtuous steadfast in his spiritual or "
        "religious life wise and happy he will be guided by high principles. If Jupiter and Venus combine in "
        "the 10th house the person is held in esteem by the government and entrusted with the protection of "
        "the Brahmins and learned people. If he is with Rahu he becomes a mischief-maker and will create "
        "trouble for others at every step. If Jupiter is aspected by Mars the native heads research "
        "institutes academies and educational institutions."
    ),
    ("Venus", 10): (
        "The native earns through houses and buildings. He will be highly influential and has many women "
        "working for him. He will be social friendly and renowned. If Venus combines with Saturn the native "
        "will profit from cosmetics and articles used by women. He will have healing powers and will be a "
        "skilled trader. His education will be disrupted. He will have respect for divine people."
    ),
    ("Saturn", 10): (
        "The native becomes a ruler or minister. He will be an agriculturist brave rich and famous. He will "
        "be dispassionate in nature and will work for the downtrodden masses. He will be judicious and work "
        "in the capacity of a judge. The native visits sacred rivers and shrines and in later life becomes an "
        "ascetic. His career will be marked by sudden elevations and depressions. If Saturn is associated "
        "with the 8th lord in a malefic Navamsa the native suffers under a tyrannical superior officer. If "
        "the 10th lord joins Saturn together with the lord of the Navamsa occupied by the 10th lord and is "
        "influenced by aspect or conjunction with the 6th lord the native will have more than one wife."
    ),
    ("Rahu", 10): (
        "There is a tendency to lust after widows. He will be a skilled artist with a flair for poetry and "
        "literature. He travels widely and is learned. He will be famous and will engage himself in business. "
        "He will have limited issues. Bold and somewhat adventurous he commits many sins."
    ),
    ("Ketu", 10): (
        "The native will be strong bold and well-known. He will commit vile deeds and be impure in his "
        "resolves. He will face many obstacles in all his undertakings. He will be very clever. If "
        "beneficially disposed the native will be happy religious well read in the scriptures and visit many "
        "pilgrim centers and sacred rivers."
    ),

    # ── House 11 ────────────────────────────────────────────────────────────
    ("Sun", 11): (
        "The person lives for a long time and becomes wealthy. He will have wife children and many servants. "
        "He gets royal and governmental favours and achieves success without much effort. He will be sagacious "
        "and principled."
    ),
    ("Moon", 11): (
        "One will be noble generous and blessed with riches wife and children. Introspective by nature and "
        "quiet-going he will become famous making good profits in business. He will acquire vast lands and be "
        "helped in his endeavours by the fair sex."
    ),
    ("Mars", 11): (
        "The native will be an eloquent and forceful speaker clever and rich but lustful; will acquire landed "
        "properties and wield considerable influence in top circles."
    ),
    ("Mercury", 11): (
        "One becomes learned in many sciences. He will possess a keen and sharp intellect; will be wealthy "
        "truthful and happy; will have many faithful servants and will prosper in engineering ventures."
    ),
    ("Jupiter", 11): (
        "The native will be long-lived. He will have a limited number of issues; will be bold and wealthy "
        "with a piercing intellect and will become renowned. He will be fond of music; will accumulate riches "
        "and will have many friends."
    ),
    ("Venus", 11): (
        "He will be of a wandering nature; will make immense profits; possessing all kinds of comforts and "
        "luxuries. He will have a weakness for women and long for their company. He will be popular having "
        "many friends."
    ),
    ("Saturn", 11): (
        "The native earns through employing many men and women. He will have few friends; will be fond of "
        "enjoyment and will earn through Government sources. He will have a long and healthy life and will be "
        "involved in politics commanding great respect."
    ),
    ("Rahu", 11): (
        "The native distinguishes himself in the army or navy; will become famous wealthy and learned; will "
        "have few children; will suffer from ear afflictions and will earn much wealth in foreign countries."
    ),
    ("Ketu", 11): (
        "The native will have the habit of hoarding. He may get monetary windfall through speculation such as "
        "lottery horse-racing and the stock exchange. Noble and possessed of many good qualities of head and "
        "heart he will succeed in all his ventures and will participate in charitable and similar works of "
        "beneficence."
    ),

    # ── House 12 ────────────────────────────────────────────────────────────
    ("Sun", 12): (
        "The native may take to an immoral life and engage himself in vile occupations. He will not be quite "
        "successful in his life and may feel neglected by all. He will suffer the loss of some limb and have "
        "weak eye-sight. He will however be energetic and have sons."
    ),
    ("Moon", 12): (
        "The native may suffer from some deformity. He will be narrow-minded hard-hearted and mischievous. "
        "He prefers to lead an obscure life in solitude. Eye-sight will be weak. If the Moon is waning and "
        "combines with Saturn sloth and lethargy will be the result."
    ),
    ("Mars", 12): (
        "The person may lose his wife. He will be selfish hateful and suffer diseases due to excess of heat "
        "in the body. He is liable to deception and may lose his money. If Mars and Saturn occupy the 12th "
        "and the 2nd houses respectively the Moon be in Lagna and the Sun in the 7th house he may suffer "
        "from leucoderma. If Mars in the 12th house is aspected by the Sun danger from fire and wicked "
        "people is indicated. Malefics in the 7th and the 8th and Mars in the 12th denote that one will have "
        "another wife even when the first is alive."
    ),
    ("Mercury", 12): (
        "Capricious and wayward the person will indulge in extra-marital relations and suffer penury; "
        "perverted thinking will make him unhappy. He will also have a few children."
    ),
    ("Jupiter", 12): (
        "The native may deride religion and be evil-minded. He will commit fearful deeds and lead a "
        "lascivious life. Later on he repents and reforms himself. The native will always be anxious about "
        "his vehicles ornaments and clothes."
    ),
    ("Venus", 12): (
        "Desertion by relatives; hankering after comforts without success and penury will make the native's "
        "life miserable. He will indulge in lying and associates with low women. His eye-sight will be poor. "
        "If Venus is exalted contrary results will happen."
    ),
    ("Saturn", 12): (
        "The native will be dull-headed and lose all his money. He will have squint eyes and a deformed limb; "
        "make many enemies; suffer losses in trade; be a pessimist and commit sins in secret."
    ),
    ("Rahu", 12): (
        "The native will be prosperous immoral but of a helpful nature. He will have eye troubles. If the Sun "
        "is in the 7th Mars is in the 10th and Rahu is in the 12th Bhava the native's father will die early."
    ),
    ("Ketu", 12): (
        "The native will have a restless and wandering mind and leave his country of birth. The lower classes "
        "will befriend him. All his inherited property may be lost."
    ),
}

# Ordered list of planets (same order as C# source)
_PLANETS = [
    Planet.Sun, Planet.Moon, Planet.Mars, Planet.Mercury,
    Planet.Jupiter, Planet.Venus, Planet.Saturn, Planet.Rahu, Planet.Ketu,
]


def get_planet_in_house_interpretation(birth_time: AstroTime, planet: Planet) -> dict:
    """Return the natal planet-in-house interpretation for a single planet.

    Returns a dict with:
        - planet (str)
        - house (int, 1-based)
        - description (str)
    """
    house = get_planet_house(planet, birth_time)
    description = _PLANET_IN_HOUSE_DATA.get((planet.name, house), "")
    return {
        "planet": planet.name,
        "house": house,
        "description": description,
    }


def get_all_planet_in_house_interpretations(birth_time: AstroTime) -> List[dict]:
    """Return natal planet-in-house interpretations for all 9 planets."""
    return [get_planet_in_house_interpretation(birth_time, p) for p in _PLANETS]
