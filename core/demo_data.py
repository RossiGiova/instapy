"""Invented personas for the demo data. Any resemblance to real people is accidental."""

# username, first name, last name, bio, verified, avatar colours (top, bottom, figure)
PERSONAS = [
    {
        "username": "giulia.trek", "first_name": "Giulia", "last_name": "Ferrante",
        "bio": "Guida escursionistica 🥾 Alba in vetta, pranzo al rifugio.", "verified": True,
        "avatar": ((255, 170, 100), (200, 80, 90), (60, 40, 60)),
        "posts": [
            ("sunset", {"palette": 0}, "Tramonto dal rifugio, 2.300 metri di silenzio."),
            ("sunset", {"reflection": True, "palette": 2}, "Lago alpino all'ora blu. Acqua gelida, vista perfetta."),
            ("forest", {"mood": "mist"}, "Foresta nella nebbia: il sentiero più bello della valle."),
            ("sunset", {"palette": 1}, "Cresta al tramonto, ultimo tratto prima della discesa."),
        ],
        "reactions": ["Che vista pazzesca!", "Quando si va insieme?", "Mi hai fatto venire voglia di partire 🥾", "Colori incredibili 😍", "Da mettere in lista per la prossima estate"],
    },
    {
        "username": "marco.skyline", "first_name": "Marco", "last_name": "Bellini",
        "bio": "Fotografo urbano 🌃 Città di notte, luci e geometrie.", "verified": False,
        "avatar": ((30, 40, 90), (90, 60, 140), (230, 210, 190)),
        "posts": [
            ("city", {"mode": "night"}, "Skyline di notte: mille finestre accese."),
            ("city", {"mode": "dusk"}, "Ora d'oro sopra i tetti."),
            ("city", {"mode": "dawn"}, "Prime luci sulla città che si sveglia."),
        ],
        "reactions": ["Composizione perfetta!", "Le luci sono bellissime", "Che atmosfera 🌃", "Sembra un film", "Quale obiettivo hai usato?"],
    },
    {
        "username": "sofia.incucina", "first_name": "Sofia", "last_name": "Marchetti",
        "bio": "Cuoca per passione 🍝 Ricette semplici, ingredienti veri.", "verified": False,
        "avatar": ((255, 225, 150), (230, 120, 80), (90, 50, 40)),
        "posts": [
            ("flatlay", {"dish": "pasta"}, "Spaghetti al pomodoro e basilico: la domenica comincia così."),
            ("flatlay", {"dish": "pizza"}, "Pizza fatta in casa, impasto 48 ore."),
            ("flatlay", {"dish": "salad"}, "Insalata d'estate con pomodorini e uova."),
            ("coffee", {}, "Pausa caffè, il momento migliore della giornata ☕"),
        ],
        "reactions": ["Ho una fame improvvisa 😋", "Mi passi la ricetta?", "Sembra buonissimo!", "Invitami a cena!", "Impiattamento da chef 👏"],
    },
    {
        "username": "luca.surf", "first_name": "Luca", "last_name": "Rinaldi",
        "bio": "Onde, sale e tavole 🏄 Sempre in cerca del prossimo swell.", "verified": False,
        "avatar": ((110, 200, 230), (20, 90, 150), (250, 230, 200)),
        "posts": [
            ("waves", {"time": "day"}, "Mare perfetto stamattina."),
            ("waves", {"time": "sunset"}, "Sessione al tramonto, acqua come l'olio."),
            ("waves", {"time": "day"}, "Domani ci riprovo, previsioni ottime."),
        ],
        "reactions": ["Invidia pura 🌊", "Che mare!", "Portami con te la prossima volta", "Onde da sogno", "Quanta pace in questa foto"],
    },
    {
        "username": "elena.astro", "first_name": "Elena", "last_name": "Conti",
        "bio": "Astrofila 🔭 Cieli bui, telescopio e termos di tè.", "verified": True,
        "avatar": ((10, 10, 40), (70, 30, 110), (200, 190, 240)),
        "posts": [
            ("space", {"ring": True}, "Il pianeta con gli anelli visto dal mio telescopio (e un po' di fantasia)."),
            ("space", {"ring": False}, "Notte limpida, la Via Lattea si vedeva a occhio nudo."),
            ("space", {"ring": True}, "Opposizione di Saturno: una serata da ricordare."),
        ],
        "reactions": ["Spettacolo del cosmo ✨", "Quanto vorrei un telescopio così", "Foto stupenda", "Mi hai fatto alzare gli occhi al cielo", "Bellissimo, davvero"],
    },
    {
        "username": "tommaso.design", "first_name": "Tommaso", "last_name": "Greco",
        "bio": "Graphic designer ✏️ Forme, colori e un po' di Bauhaus.", "verified": False,
        "avatar": ((245, 197, 48), (222, 52, 38), (24, 24, 24)),
        "posts": [
            ("bauhaus", {}, "Esercizio di composizione n.1: cerchi e triangoli."),
            ("bauhaus", {}, "Esercizio n.2: solo colori primari."),
            ("bauhaus", {}, "Esercizio n.3: la griglia è tutto."),
            ("bauhaus", {}, "Esercizio n.4: rompere le regole, ma con metodo."),
        ],
        "reactions": ["Ottimo uso del colore!", "Questa finirebbe benissimo su un poster", "Mi piace la griglia", "Pulito ed efficace 👌", "Complimenti, che occhio"],
    },
    {
        "username": "nora.garden", "first_name": "Nora", "last_name": "Villa",
        "bio": "Giardino, orto e tanta pazienza 🌸 Condivido quello che cresce.", "verified": False,
        "avatar": ((150, 210, 140), (40, 120, 80), (250, 235, 230)),
        "posts": [
            ("garden", {"palette": "spring"}, "La primavera nel mio giardino."),
            ("garden", {"palette": "summer"}, "Fioritura d'estate, i girasoli stanno arrivando."),
            ("forest", {"mood": "dusk"}, "Passeggiata nel bosco dietro casa, a fine giornata."),
        ],
        "reactions": ["Che colori! 🌼", "Hai il pollice verde", "Bellissimo giardino", "Mi dai qualche consiglio per le rose?", "Pace assoluta"],
    },
]

LEGACY_USERNAMES = ["alice", "bruno", "chiara", "dario"]  # removed by --reset (old demo data)
