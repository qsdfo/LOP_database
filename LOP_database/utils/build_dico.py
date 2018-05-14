#!/usr/bin/env python
# -*- coding: utf8 -*-

from collections import OrderedDict
import pickle as pickle


# Dico with the regexp for intru_mapping
def build_dico():

    hand_expr = ur"(linke|left|rechte|right|prawa|lewa)\s*(hand|reka)"

    dico = {
        u"accordion": [
            ur"a[kc]{1,2}ord[ei]on",
            ur"^[^h-z]*(akk|acc)[^h-z]*$",
        ],
        u"bandoneon": [
            ur"bandoneone?",
        ],
        u"bandurr?ia": [    # Espèce de luth espagnol
            ur"bandurria",
        ],
        u"basso continuo": [
            ur"fonda(mento)?",
            ur"b\.c\.",
            ur"(basso[\s\-])?continuo",
            ur"co(nt)?\.",
            ur"bs?\.?\s+c\.?[^a-z]*$",
            ur"spinetta e violone",
            ur"bassus continuus"
        ],
        u"basset horn": [  # Kind of clarinet
            ur"corni di bassetto",
        ],
        u"bassoon": [
            ur"fagott?[oei]?s?",
            ur"bass?oo?ns?"
        ],
        u"bell": [
            ur"(orchestra|tubular\s*)?bells?",
            ur"cloche",
            ur"campane",
            ur"chimes"
        ],
        u"bombo": [
            ur"bombo",
        ],
        u"castanets": [
            ur"castanuelas",
            ur"castagnetti"
        ],
        u"celesta": [
            ur"celesta( (lh|rh))?",
        ],
        u"clarinet bass": [
            ur"[ck]lar(inett?[ieo]?n?s?)?",
            ur"^[^h-z]*bs[\s\-]*klt?[^h-z]*$",
        ],
        u"clarinet": [
            ur"[ck]lar(inett?[ieo]?n?s?)?",
            ur"^[^h-z]*klt?[^j-z]*$",
        ],
        u"clarini": [
            ur"clarini",
        ],
        u"clave": [
            ur"claves?",
            ur"klangstabe",
        ],
        u"clavinet": [
            ur"clavinet",
        ],
        u"cornet": [
            ur"cornet[^t]?( a piston)?",  # cornet a piston
            ur"pistons?",
        ],
        u"cornett": [
            "cornett[io]?",  # cornet a bouquin
        ],
        u"cymbal": [
            ur"platillos",
            ur"c[yi]mb[ea]ls?",
            ur"becken",
            ur"piatti",
        ],
        u"double bass": [
            ur"^[^a-z]*bassi[^a-z]*$",
            ur"double\s*bass?e?s?",
            ur"contrab",
            ur"[ck]ontr[ae]\s*bb?ass[eo]?s?",
            ur"k\.?\s*b(ass)?$",
            ur"^[^a-z]*cb[^a-z]*$",
            ur"contrabajos?",
            ur"bass( (tremolo|pizz))",
            ur"generalbass",
        ],
        u"drum": [
            ur"tambo?uro?( militai?re)?",
            ur"drums?",
            ur"standard kit",
            ur"schlagzeug",
        ],
        u"dulcian": [
            ur"dulcian",
        ],
        u"english horn": [
            ur"englisc?h[\s\-]*horn",
            ur"eng[\s\-]*horn",
            ur"engl\.[\s\-]*hor?n",
            ur"eng\.[\s-]*h\.",
            ur"cor\s*anglais",
            ur"corno inglese"
        ],
        u"euphonium": [
            ur"euphonium",
        ],
        u"fortepiano": [
            ur"fortepiano",
            ur"pianoforte?",
        ],
        u"flaghorn": [
            ur"flaghorn",
        ],
        u"flugelhorn": [
            ur"flug(elhorn)?",
            ur"bugle",
        ],
        u"flauto d'amore": [
            ur"fl\.?\s*d'am",
        ],
        u"flute": [
            ur"[^pi]*fl(au|u|o)t[oei]n?(\s*tran?s?vers[oe])?",
            ur"transverse flute",
            ur"traversa",
            ur"querfl",
            ur"qfl",
            ur"^[^h-z]*flt?[^j-z]*$",
        ],
        u"guitar": [
            ur"((nylon|jazz|acoustic) )?(gu?itarr?e?|git)( \(steel\))?",
        ],
        "glockenspiel": [
            ur"glockenspiel",
            ur"glock",
            ur"campanelli",
            ur"carillon",
        ],
        "hammond organ": [
            ur"(hammond?|drawbar)\s*organ",
        ],
        u"harmonica": [
            ur"harmonica",
        ],
        u"harmonium": [
            ur"harmonium( main (droite|gauche))?",
        ],
        u"harpsichord": [
            ur"harpsichord",
            ur"(clavi[\s-]?)?cembalo",
            ur"^(.*\s)?cemb(\s.*)?$",
            ur"clavecin",
            ur"hpschd",
            ur"recit",
            ur"cembalo" + hand_expr,
        ],
        u"harp": [
            ur"(orchestral\s*)?harps?( (lh|rh))?",
            ur"harfe",
            ur"arpa",
        ],
        u"horn": [
            ur"(fr(\.|ench)\s*)?horns?",
            ur"trompas?",
            ur"cors?",
            ur"french\s*horns?",
            ur"corn[oi]?",
            ur"horner",
            ur"^[^h-z]*hr?n",
        ],
        u"lute": [
            ur"luth",
            ur"lute",
        ],
        u"lyre": [
            ur"lyr[ea]",
            ur"orfeo",
        ],
        u"mandola": [
            ur"mandol[ai](ne)?",
        ],
        u"maracas": [
            ur"maracas",
        ],
        u"marimba": [
            ur"marimba",
        ],
        u"metallophone ": [
            ur"metallophon",
        ],
        u"oboe": [
            ur"obo[eia]s?",
            ur"^[^h-z]*ob[^h-z]*$",
            ur"hobo",
            ur"hautbois",
            ur"h?oboen",
        ],
        u"oboe amore": [
            ur"ob.*d'am(ore)?",
        ],
        u"oboe da caccia": [
            ur"ob d c?",
            ur"oboe da caccia",
        ],
        u"ocarina": [
            ur"o[ck]arina",
        ],
        u"ondes martenot": [
            ur"ondes? martenot",
        ],
        u"organ": [
            ur'(orguel|orgue|orgel|organ)(\s*(LH|RH))?',
            ur'^[^a-z]*org[^a-z]*$',
            ur"great organ",
            ur"stops combinations?",
            ur"swell organ",
            ur"pedal",
        ],
        u"other": [
            ur"unnamed",
            ur"^\\new$",
            ur"^onbekend$",
            ur"unbekannt",
            # ur"^instru",
            ur"^\s*midi(file)?\s*[0-9_]*?$",
            ur"unbenannt",
            ur"musicxml",
            ur"^\s*$",
            ur"^\s*[IV]+\s*$",
            ur"bezeichnung",
            ur"^[\s0-9\.\-_]+$",
            ur"ARIA Player",
            ur"^solo$",
            # Specific to Musicalion
            ur"\(ohne Bezeichnung\)",
            ur"pos[\s\.0-9]*$",
            ur"unknown",
            ur"^bottom$",
            ur"^top$",
            ur"^dessus[0-9]$",
            ur"^lower$",
            ur"^upper$",
            ur"^up$",
            ur"^down$",
            ur"^one$",
            ur"^two$",
            ur"^three$",
            ur"^four$",
            ur"^five$",
            ur"^six$",
            ur"^seven$",
            ur"^eight$",
            ur"^nine$",
            ur"^ten$",
            ur"^staff[0-9\-\.]*(one|two)?$",
            ur"\[system [0-9]\]",
            ur"^\s*insieme archi 1\s*$",
            ur"^\s*scala tuned pitch bend track\s*$",
            "strumento[0-9]",
            ur"SmartMusic SoftSynth",
            ur"Standard-MIDI-Ausgabegerat",
            ur"ornaments",
            # Kunstderfuge
            # ur"\[\.\.\.\]",
            # ur"B(ob |\.)Fisher",
            # ur"schola",
            # ur"Russian piano Music for children",
            # ur"Miaskowskij: 3 fugues",
            # ur"^pan[0-9]+$",
            # ur"^p_[0-9]+$",
            # ur"^ch_[0-9]+$",
        ],
        u"pan flute": [
            ur"pan\s*fl[ou]te",
        ],
        u"percussion": [
            ur"schlagwerk",
            ur"perc",
            ur"percussion",
            ur"trommel",
        ],
        u"piano": [
            ur"piano",
            ur"klavier",
            ur"konzertflugel",
            ur"^[^a-z]*(manual|primo|secondo)?[^a-z]*" + hand_expr,
            ur"^[^a-z]*(LH|RH)[^a-z]*$",
            ur"kboard",
            # ur"Instrument(17|18|19)",
            ur"Track (1|2|3|4)"
        ],
        u"piccolo": [
            ur"pic?coll?o(flote)?",
            ur"picc",
            ur"ottavino",
            ur"flautin",
            ur"petite flute",
        ],
        u"ratchet": [
            ur"raganella",
        ],
        u"recorder": [
            ur"flute a bec",
            ur"recorder",
            ur"block[\-\.\s]*(fl(o|au)te|fl\.?)",
            ur"bl[\-\s]*fl",
        ],
        u"rohrenglocken": [
            ur"rohrenglocken",
        ],
        u"tambourine": [
            ur"tambo?urin[eo]?",
        ],
        u"tam tam": [
            ur"t[ao]m[\s\-]*t[ao]m",
            ur"gong",
        ],
        u"timpani": [
            ur"timpani",
            ur"timbale?s?",
            ur"pauken?",
            ur"^[^h-z]*pk[^h-z]*$",
        ],
        u"triangle": [
            ur'triangle',
            ur'triangel',
            ur'triang[uo]lo',
        ],
        u"trombone": [
            ur"trombone?s?",
            ur"p(o|au)s(aunen?)?"
        ],
        u"trumpet": [
            ur"tr[uo]mpett?([ea]n?)?s?",
            ur"tr[uo]mp",
            ur"trpt?",
            ur"tromb[ae]",
            ur"tp",
        ],
        u"tuba": [
            ur"tuba",
            ur"bombardino",
        ],
        u"saxophone": [
            ur"(saxo?(phone?)?|sassofono)",
        ],
        u"spinet": [  # épinette
            "spinet( (left|right))?",
        ],
        u"voice": [
            ur"^(a|b|t|s)\.?[\s0-9]*$",
            ur'sopra?ano?',
            ur'sop',
            ur'^[^a-z]*alto?[^h-z]*$',
            ur'sopra?ano?\s*solo',
            ur"mezzo",
            ur'solo\s*sopra?ano?',
            ur"\\mtxinstrname\{altus\}",
            ur"\{\\twelvebf\{altus\}\}",
            ur'contratenor',
            ur'contralt[io]',
            ur'tenore?\s*(solo|primo|secondo)?',
            ur'ten\. ',
            ur"\\mtxinstrname\{tenor\}",
            ur"\{\\twelvebf\{tenor\}\}",
            ur'bar[yi]tone?',
            ur'bar[yi]tone?\s*solo',
            ur"\\mtxinstrname\{bassus\}",
            ur"bassus",
            ur"bass I\. II\.",
            ur"frauen",
            ur"\{\\twelvebf\{bassus\}\}",
            ur'treble',
            ur'(dis|des)?cant(us)?',
            ur"canto\s*(primo|secondo)?",
            ur"(basse|haute)-contre",
            # mix
            ur"s/?a",
            ur"t/?b",
            ur"a/?t",
            ur"ten[-/\s]*bass",
            ur"sopr[-/\s]*alt",
            ur"sopran\s?/\s?alto?",
            ur"tenor\s?/\s?bass",
            # misc
            ur'voice',
            ur'voz',
            ur"voix",
            ur"choi?r",
            ur"stimme",
            ur'gb$',
            ur"medius",
            ur"superius",
            ur"cant[ou]s?( (primus|secundus))?",
            ur'quint[oua]s?',
            ur'quinta vox?',
            ur'sest[ou]s?',
            ur"gesang",
            ur"[ABST]-Blfl",
            ur"\{\\twelvebf\{cantus\}\}",
            ur"\{\\twelvebf\{quintus\}\}",
            ur"\\mtxinstrname\{cantus\}",
            ur"\\mtxinstrname\{quintus\}",
            ur"manner"
            # ###### R E M O V E /// C H E C K ##########
            # ##############################################
            # ##############################################
            # ##############################################
        ],
        u"vibraphone": [
            ur"vibraphone?",
        ],
        u"viola": [
            ur"(viol[ea]|vla|va|bratsche)[^gambro]*$",
        ],
        u"viola d'amore": [
            ur"va\.? d'am",
            ur"viola d'amore"
        ],
        u"viola da gamba": [
            ur"viol[ea][\sI\(\)]+d[ea] gamb[ea]",
        ],
        u"viola da braccio": [
            ur"viola[\sI]+da braccio",
        ],
        u"violin": [
            ur"viol[io]n[oe]?( (principale|secondo))?[^c]*?$",  # Avoid violoncello and viola
            ur"viol?\.?[^ach-z]*$",
            ur"vl[^a-hj-z]*$",
            ur"geige",
            ur"skrzypce",
        ],
        u"violoncello": [
            ur"cell[oei]",
            ur"vl?\.?cl?\.?",
            ur"vcelli",
            ur"violl?onc\.?",
        ],
        u"woodblock": [
            ur"wood\s*block",
        ],
        u"xylophone": [
            ur"xylophone?s?",
            ur"silofono",
        ],
        u"zither": [
            ur"(zither|cithare)",
        ],
        ur"violin and viola and violoncello and double bass": [
            ur"string ensemble",
        ]
    }
    dico_ordered = OrderedDict()
    for key, value in sorted(dico.items()):
        new_value = []
        for elem in value:
            new_value.append(elem)
        dico_ordered[key] = new_value
    return dico_ordered

if __name__ == '__main__':
    dico = build_dico()
    pickle.dump(dico, open("instru_regex.p", "wb"))


# ####### To check
# Remove "primo" and "secondo" from other and find what it refers to in Brahms music
# wtf is Rechts ??
