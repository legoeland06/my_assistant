import sys, os, operator, subprocess, random
import pretty_midi as pMidi
from pychord import Chord

listeAccords = []
laBelleListeTotale = []

sortie = {
    "normal": 0,
    "demiton": 0,
    "descente": 0,
    "descenteL": 0,
    "decale": 0,
    "basse2Avant": 0,
    "basse2Apres": 0,
    "alea": 0,
    "aleaMontee": 0,
    "guitare": 0,
    "ride": 0,
    "rideDessus": 0,
    "rideSync": 0,
    "charley": 0,
    "charleySync": 0,
    "snare1": 0,
    "snare2": 0,
    "kick": 0,
    "moins": 0,
    "plus": 0,
    "sautD": 0,
    "sautG": 0,
    "pedale": 0,
    "diminuee": 0,
    "NORMAL": 0,
    "m7-seconde": 0,
    "m7-normal": 0,
    "m7-tierce": 0,
    "m7-septieme": 0,
    "m7-quinte": 0,
    "m7-neuf": 0,
}

def cree_midi():

    r1 = random
    r1.Random()

    r2 = random
    r2.Random()

    r3 = random
    r3.Random()

    r4 = random
    r4.Random()
    r5 = random
    r5.Random()

    zchords = []
    listeTransposee = []
    instru = 1

    midi_data = pMidi.PrettyMIDI()

    sosie = Chord

    transpo = 0

    transfertchords = sys.argv[1]
    print("*********\ntransfertchords BRUT:\n", sys.argv[1], "\n*************")
    # nbGrille =int(input("Veuillez indiquer le nombre de répétitions de la grille: "))
    nbGrille = int(sys.argv[
        2
    ])  # int(input("Veuillez indiquer le nombre de répétitions de la grille: "))
    # tempo = int(input("Tempo: "))
    tempo = float(sys.argv[3])  # int(input("Tempo: "))
    # transp = input("Transpositions: (0) ? ")

    # if transp: transpo=int(transp)

    # for i in sys.argv[1]:
    #     zchords.append(i)

    print("transfertchords splitée:\n",
        transfertchords.split(),
        "\n*************",
    )
    zchords = transfertchords.split()
    mchords = [sosie(c) for c in zchords * nbGrille]
    for ch in mchords:
        print (ch)

    chords = mchords

    piano = pMidi.Instrument(program=int("001"), is_drum=False, name="Piano")
    batt = pMidi.Instrument(program=int("041"), is_drum=True, name="Brush")
    guitare = pMidi.Instrument(program=int("025"), is_drum=False, name="Nylon Guitar")
    nappes = pMidi.Instrument(
        program=int("025"), is_drum=False, name="Nylon Guitar"
    )  # String Slow
    basse = pMidi.Instrument(program=int("032"))
    chordBefore = chords[-1]

    # doublon = False
    oldlen = 60.000 / tempo
    n = 0
    nDiffChord = 0
    position = 0
    deuxiemeFois = 0
    montee = 0

    for nChord, chord in enumerate(chords):
        print("ROOT::"+chord.root)
        print("INT::"+chord.chordu)
        print("QUALITY::"+chord.quality.quality)
        print("COMPONENTS_PITCH::"+str(chord.components_with_pitch(2)))
        print("COM%PONENTS::"+str(chord.components()))
        numeroBasse = pMidi.key_name_to_key_number(chord.root)
        syncopes = True

        rand1 = r1.randint(1, 17)
        rand3 = r3.randint(1, 7)
        rand2 = r2.randint(8, 32)
        rand5 = r5.randint(8, 32)
        compt = 0
        chordNext = next(chords.__iter__())
        chordNext = chords[(nChord+1)%len(chords)]
        doublon = True if chordBefore.chordu == chord.chordu else False
        print(
            "*************\nprécédent: {} \nactuel: {} \nsuivant: {}".format(
                chordBefore.chordu, chord.chordu, chordNext.chordu
            )
        )
        nextblond = True if chordNext.chordu == chord.chordu else False
        silentChord = True if str(chord.quality) == "ot" else False
        chordInTextMode = chord.chordu
        if not silentChord and chordInTextMode not in listeAccords:
            listeAccords.append(chordInTextMode)
        if transpo != 0:
            # ******************************************************************
            # ***** TRANSPOSITION DE TOUS LES ACCORDS AVANT LA LECTURE ICI *****
            # ******************************************************************
            chord.transpose(transpo, scale="C")  # on transpose tout
            # mais on n'affiche pas le doublons d'accord
            if not silentChord and chord.chord not in listeTransposee:
                listeTransposee.append(chord.chord)
        # ******************************************************************

        veloSurplus = 0
        _VOLUME_GENERAL = 100
        veloBasse = int(_VOLUME_GENERAL * 9 / 100)
        pourquoipas = False
        # myrandom=rand2

        walkingBassOk = (
            int(chord.chordu) == 4
            or int(chord.chordu) == 3
            or int(chord.chordu) == 6
            or int(chord.chordu) == 2
            and (doublon or nextblond)
        )
        ridingBass = int(chord.chordu) == 2 or doublon or nextblond

        # ATTENTION ICI GESTION DES ACCELERATIONS ET DECELLERATIONS
        newTempo = tempo * int(chord.chordu) / 4
        newLen = 60.000 / newTempo
        # FIN DE GESTION DES TEMPI

        print(chord.root+str(chord.quality))

        if silentChord:
            veloBasse = 0
            _VOLUME_GENERAL = 0
            veloSurplus = 0
            compt += 1
            ridingBass = True
            syncopes = False
            walkingBassOk = False
        else:
            myrandom = random.randint(0, 2)

            veloSurplus = 10
            _VOLUME_GENERAL = 80
            veloBasse = 90
            for note_name in chord.components_with_pitch(root_pitch=3):
                note_number = pMidi.key_name_to_key_number(note_name)
                if note_number < 42:
                    note_number += 12
                elif note_number > 72:
                    note_number -= 12
                pads = pMidi.Note(
                    velocity=int(_VOLUME_GENERAL * 40 / 100),
                    pitch=note_number,
                    start=position + oldlen * myrandom,
                    end=(position)
                    + (4 * oldlen)
                    / float(
                        chord.chordu
                    ),  # on utilise repeti car la fin du placage de l'accord dépend de repeti
                )
                if n % 2 == 0:
                    nappes.notes.append(pads)

            if not doublon:
                n = 0
                nDiffChord += 1
                compt += 1

                deuxiemeFois = 0

                for note_name in chord.components_with_pitch(root_pitch=3):
                    print(note_name)
                    note_number = pMidi.key_name_to_key_number(note_name)
                    if note_number < 52:
                        note_number += 12
                    elif note_number > 72:
                        note_number -= 12

                    p = pMidi.Note(
                        velocity=int(_VOLUME_GENERAL * 1 / 3),
                        pitch=note_number,
                        start=position,
                        end=position
                        + 4
                        * oldlen
                        / float(
                            chord.chordu
                        ),  # on utilise repeti car la fin du placage de l'accord dépend de repeti
                    )
                    piano.notes.append(p)

            elif (nChord * 2) % 10 == r3.randint(0, 60) or pourquoipas == True:
                if montee < 4:
                    note_basse = chord.components_with_pitch(root_pitch=1)[
                        -(n % len(chord.components_with_pitch(root_pitch=1)))
                    ]
                    numeroBasse = pMidi.key_name_to_key_number(note_basse)
                    montee += 1
                    pourquoipas = True
                    sortie["aleaMontee"] += 1
                else:
                    print("********** ", position)
                    pourquoipas = False
                    montee = 0

            # FIN GESTION DES AUTRES NOTES HORS TESSITURE DE LA CONTREBASSE

            elif walkingBassOk and doublon:
                r1.Random()
                rand1 = r1.randint(1, 10)
                print(
                    "n:",
                    n,
                    "\n",
                    "nChord:",
                    nChord,
                    "\n",
                    "nDiffChord:",
                    nDiffChord,
                    "\n",
                    "rand1:",
                    rand1,
                )

                note_basse = chord.components_with_pitch(root_pitch=1)[
                    -(
                        (random.randint(1, 40))
                        % len(chord.components_with_pitch(root_pitch=1))
                    )
                    + 2
                ]
                numeroBasse = pMidi.key_name_to_key_number(note_basse)
                sortie["decale"] += 1

                if (n * 10) % rand3 == random.randint(0, 7) and compt == 0:
                    note_basse = chord.components_with_pitch(root_pitch=1)[
                        -(
                            (n % myrandom)
                            % len(chord.components_with_pitch(root_pitch=1))
                        )
                    ]
                    numeroBasse = pMidi.key_name_to_key_number(note_basse)
                    sortie["descenteL"] += 1

                elif (
                    "m7" in str(chord.quality)
                    or "M" in str(chord.quality)
                    and rand3 == 4
                ):
                    if n % 4 == 0:
                        note_basse = chord.components_with_pitch(root_pitch=1)[0]
                        numeroBasse = pMidi.key_name_to_key_number(note_basse)
                        sortie["m7-normal"] += 1

                    if n * 7 % rand1 == 9:
                        note_basse = chord.components_with_pitch(root_pitch=1)[0]
                        numeroBasse = pMidi.key_name_to_key_number(note_basse) + 2
                        sortie["m7-seconde"] += 1

                    elif n * 7 % rand1 == 3:
                        note_basse = chord.components_with_pitch(root_pitch=1)[
                            random.randint(1, 6)
                            % len(chord.components_with_pitch(root_pitch=1))
                        ]
                        numeroBasse = pMidi.key_name_to_key_number(note_basse)
                        sortie["m7-tierce"] += 1

                    elif n * 7 % rand1 == 4:
                        note_basse = chord.components_with_pitch(root_pitch=1)[
                            random.randint(1, 6)
                            % len(chord.components_with_pitch(root_pitch=1))
                        ]
                        numeroBasse = pMidi.key_name_to_key_number(note_basse)
                        sortie["m7-quinte"] += 1

                    elif n * 7 % rand1 == 5:
                        note_basse = chord.components_with_pitch(root_pitch=1)[
                            random.randint(1, 6)
                            % len(chord.components_with_pitch(root_pitch=1))
                        ]
                        numeroBasse = pMidi.key_name_to_key_number(note_basse)
                        sortie["m7-septieme"] += 1

                elif "m9" in str(chord.quality) and n % rand1 == 6:
                    note_basse = chord.components_with_pitch(root_pitch=1)[3]
                    numeroBasse = pMidi.key_name_to_key_number(note_basse)
                    sortie["m7-neuf"] += 1

                elif n % rand1 == 7 and compt == 0:
                    note_basse = chord.components_with_pitch(root_pitch=1)[
                        myrandom % len(chord.components_with_pitch(root_pitch=1))
                        - (nChord % len(chord.components_with_pitch(root_pitch=1)))
                        - 1
                    ]
                    numeroBasse = pMidi.key_name_to_key_number(note_basse)
                    sortie["descente"] += 1
                    #  GESTION DES AUTRES NOTES HORS TESSITURE DE LA CONTREBASSE

            # GESTION DES DERNIERS TEMPS EN CHROMATISME PLUS OU MOINS

            if (n * 17) % rand3 == rand1:
                note_basse = chord.components_with_pitch(root_pitch=1)[
                    -(
                        random.randint(8, 32)
                        % len(chord.components_with_pitch(root_pitch=1))
                    )
                ]
                numeroBasse = pMidi.key_name_to_key_number(note_basse)
                sortie["descente"] += 1

            if (n * 11) % rand3 == rand1 and nChord + 1 < len(chords):
                if n % 4 == 3:
                    chord2 = chords[nChord + 1]
                    note_basse = chord2.components_with_pitch(root_pitch=1)[0]  # tierce
                    numeroBasse = pMidi.key_name_to_key_number(note_basse) - 1
                    # print(chord.chord,chord2.chord)
                    sortie["demiton"] += 1
                    # print('demiton')
                # FIN DE GESTION DES DERNIERS TEMPS EN CHROMATISME PLUS OU MOINS
                elif rand5 > 98:
                    if deuxiemeFois == 0:
                        noteBasse2 = pMidi.Note(
                            velocity=veloBasse - 2 * veloSurplus,
                            pitch=numeroBasse,
                            start=position - (1 / int(chord.chordu)) * oldlen,
                            end=position
                            + oldlen
                            / float(chord.chordu),  # -(1/(2*int(chord.chordu)))*oldlen,
                        )
                        basse.notes.append(noteBasse2)
                        deuxiemeFois += 1
                        sortie["basse2Avant"] += 1
                    else:
                        noteBasse2 = pMidi.Note(
                            velocity=veloBasse - 2 * veloSurplus,
                            pitch=numeroBasse,
                            start=position + (1 / int(chord.chordu)) * newLen,
                            end=position
                            + oldlen
                            / float(chord.chordu),  # (1/(2*int(chord.chordu)))*oldlen,
                        )
                        basse.notes.append(noteBasse2)
                        sortie["basse2Apres"] += 1
                        deuxiemeFois += 1

            if n % 4 == 0 or chord.on.__str__() in md.N_VAL[1:]:
                note_basse = chord.components_with_pitch(root_pitch=1)[0]
                numeroBasse = pMidi.key_name_to_key_number(note_basse)
                sortie["NORMAL"] += 1

            if numeroBasse > 40:
                numeroBasse -= 12
                sortie["moins"] += 1
            elif numeroBasse < 28:
                numeroBasse += 12
                sortie["plus"] += 1

            noteBasse = pMidi.Note(
                velocity=veloBasse + veloSurplus,
                pitch=numeroBasse,
                start=position,
                end=position
                + 4 * oldlen / float(chord.chordu),  # 4*oldlen/float(chord.chordu),
            )
            basse.notes.append(noteBasse)
            ridingBass = walkingBassOk and nextblond

            if ridingBass:
                ride = pMidi.Note(
                    velocity=int(veloBasse * 3 / 5),
                    pitch=51,  # ride
                    start=position,
                    end=0,
                )
                batt.notes.append(ride)
                sortie["ride"] += 1
                if n % 4 == 2 or n % 4 == 0:
                    charley = pMidi.Note(
                        velocity=veloBasse,
                        pitch=44,  #
                        start=position + newLen * 3,
                        end=0,
                    )
                    batt.notes.append(charley)
                    sortie["charley"] += 1

            sue = r3.randint(1, 1 + int(32 / float(chord.chordu)))
            if sue % 8 == 3 or sue % 8 == 5 or sue % 8 == 7:
                ride = pMidi.Note(
                    velocity=int(veloBasse * 3 / 4),
                    pitch=51,  # ride
                    start=position,
                    end=0,
                )
                batt.notes.append(ride)
                sortie["rideDessus"] += 1

            if sue % 4 == 2:
                charley = pMidi.Note(
                    velocity=veloBasse,
                    pitch=44,  # ride
                    start=position + r3.randint(1, 1 + int(32 / float(chord.chordu))),
                    end=0,
                )
                batt.notes.append(charley)
                sortie["charley"] += 1

            if sue % 5 == 3 and syncopes:
                deuxiemeFois += 1
                ride = pMidi.Note(
                    velocity=int(veloBasse * 3 / 4),
                    pitch=51,  # ride
                    start=position - newLen / 3,
                    end=0,  # position+((n + 1) * newLen),
                )
                batt.notes.append(ride)
                sortie["rideSync"] += 1

                if deuxiemeFois > 2:
                    kick = pMidi.Note(
                        velocity=int(veloBasse / 3),
                        pitch=36,  # ride
                        start=position - newLen / 3,
                        end=0,  # position+((n + 1) * newLen),
                    )
                    batt.notes.append(kick)
                    sortie["kick"] += 1
                    deuxiemeFois -= 2

            if sue % 1 == 0:
                snare1 = pMidi.Note(
                    velocity=int(veloBasse / 3),
                    pitch=40,  # ou 40 snare
                    start=position + ((n % 3) + 2 / 3) * newLen,
                    end=0,
                )
                sortie["snare1"] += 1

            if sue % 3 == 2:
                snare1 = pMidi.Note(
                    velocity=int(veloBasse / 3),
                    pitch=40,  # ou 40 snare
                    start=position + newLen,
                    end=0,
                )

                batt.notes.append(snare1)
                sortie["snare2"] += 1
                sortie["charleySync"] += 1
            # FIN DE GESTION DES 1ER TEMPS

        n += 1
        position += 4 * oldlen / float(chord.chordu)
        chordBefore = chord

    print("********* LES ACCORDS DE LA GRILLES ***********")
    print(listeTransposee)
    print(listeAccords)
    print("********* ************* ***********")
    for item in chords:
        # print("'"+item.chord+"',")
        laBelleListeTotale.append(item.chord)

    print(laBelleListeTotale)

    midi_data.instruments.append(piano)
    midi_data.instruments.append(basse)
    # midi_data.instruments.append(nappes)
    midi_data.instruments.append(guitare)
    # midi_data.instruments.append(batt)
    midi_data.write("zicDjango/static/sounds/midi/chord.mid")

    # os.system('fluidsynth -i -va alsa -g 1 /usr/share/sounds/sf2/default-GM.sf2 --audio-file-type wav -F zicDjango/static/sounds/chord.wav zicDjango/static/sounds/midi/chord.mid')
    os.system('fluidsynth -i -va alsa -g 1 /usr/share/sounds/sf2/default-GM.sf2 zicDjango/static/sounds/midi/chord.mid')
    print()
    # largeur=int(os.system("echo $COLUMNS"))
    sortie["alea"] /= 3
    largeur = 158  # int(os.system('/usr/bin/echo "$COLUMNS" '))
    rapport = 100 / maxDesSorties(sortie)
    print(largeur, rapport)
    for target_list in sortie:
        print(
            target_list,
            " ",
            "-" * int(sortie[target_list] * rapport) + " >",
            int(sortie[target_list]),
        )

    print()
    return midi_data  # render(request,'chords/chords.html',{"liste":md.liste,"suzie":suzie,"chordMid":"./chord.mid"})


def affichage(chords):
    for accord in chords:
        print(accord.components_with_pitch(2))


def maxDesSorties(obj):
    max_val = max(sortie.items(), key=operator.itemgetter(1))[1]
    resultat = max_val
    return resultat


def main():
    cree_midi()


if __name__ == "__main__":
    main()
