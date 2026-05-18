"""
Genererer realistisk testdata i JSON-stat2-format.
Brukes når SSB API ikke er tilgjengelig.
"""


def generate_befolkning_response() -> dict:
    """Simuler SSB tabell 07459 respons med et lite utvalg."""
    kommuner = {
        "0301": "Oslo",
        "1103": "Stavanger",
        "4601": "Bergen",
        "5001": "Trondheim",
        "1902": "Tromsø",
        "3801": "Horten",
        "4202": "Grimstad",
        "1557": "Gjemnes",
        "1151": "Utsira",
        "3411": "Ringsaker",
    }

    aldre = {}
    for a in range(0, 106):
        key = str(a)
        if a == 105:
            aldre[key] = "105 år eller eldre"
        else:
            aldre[key] = f"{a} år"

    years = {"2020": "2020", "2021": "2021", "2022": "2022", "2023": "2023", "2024": "2024"}

    import random
    random.seed(42)

    # Befolkningstall per kommune (realistiske størrelsesordener)
    kommune_pop = {
        "0301": 700000, "1103": 145000, "4601": 290000,
        "5001": 210000, "1902": 78000, "3801": 28000,
        "4202": 24000, "1557": 1200, "1151": 200, "3411": 35000,
    }

    values = []
    for k_code in kommuner:
        base = kommune_pop[k_code]
        for age in range(106):
            # Enkel aldersfordeling: topp rundt 30-40, avtar etter 70
            if age < 20:
                weight = 0.011
            elif age < 35:
                weight = 0.015
            elif age < 50:
                weight = 0.014
            elif age < 55:
                weight = 0.012
            elif age < 62:
                weight = 0.010
            elif age < 67:
                weight = 0.008
            elif age < 75:
                weight = 0.006
            elif age < 85:
                weight = 0.003
            elif age < 95:
                weight = 0.001
            else:
                weight = 0.0002

            for yr_idx, yr in enumerate(years):
                # Liten årlig vekst
                pop = int(base * weight * (1 + 0.005 * yr_idx))
                pop += random.randint(-max(1, pop // 20), max(1, pop // 20))
                values.append(max(0, pop))

    dim_ids = ["Region", "Alder", "Tid"]
    dim_sizes = [len(kommuner), len(aldre), len(years)]

    return {
        "class": "dataset",
        "id": dim_ids,
        "size": dim_sizes,
        "dimension": {
            "Region": {
                "category": {
                    "index": {code: i for i, code in enumerate(kommuner)},
                    "label": kommuner,
                }
            },
            "Alder": {
                "category": {
                    "index": {code: i for i, code in enumerate(aldre)},
                    "label": aldre,
                }
            },
            "Tid": {
                "category": {
                    "index": {code: i for i, code in enumerate(years)},
                    "label": years,
                }
            },
        },
        "value": values,
    }


def generate_lonn_response() -> dict:
    """Simuler SSB tabell 11654 respons."""
    naeringer = {
        "00-99": "Alle næringer",
        "01-03": "Jordbruk, skogbruk og fiske",
        "05-09": "Bergverksdrift og utvinning",
        "10-33": "Industri",
        "41-43": "Bygge- og anleggsvirksomhet",
        "45-47": "Varehandel",
        "49-53": "Transport og lagring",
        "55-56": "Overnattings- og serveringsvirksomhet",
        "58-63": "Informasjon og kommunikasjon",
        "64-66": "Finansierings- og forsikringsvirksomhet",
        "68-75": "Faglig, vitenskapelig og teknisk tjenesteyting",
        "77-82": "Forretningsmessig tjenesteyting",
        "84": "Offentlig administrasjon og forsvar",
        "85": "Undervisning",
        "86-88": "Helse- og sosialtjenester",
    }

    contents = {"Lonsstakere": "Lønnstakere", "GjMdTotal": "Gjennomsnittlig månedslønn"}
    quarters = {"2024K1": "2024K1", "2024K2": "2024K2", "2024K3": "2024K3", "2024K4": "2024K4"}

    # Realistiske tall
    naering_data = {
        "00-99": (2800000, 54000), "01-03": (45000, 38000),
        "05-09": (65000, 78000), "10-33": (220000, 48000),
        "41-43": (250000, 46000), "45-47": (380000, 42000),
        "49-53": (145000, 44000), "55-56": (95000, 32000),
        "58-63": (115000, 65000), "64-66": (55000, 72000),
        "68-75": (170000, 58000), "77-82": (135000, 40000),
        "84": (195000, 52000), "85": (210000, 48000),
        "86-88": (420000, 46000),
    }

    import random
    random.seed(123)

    values = []
    for n_code in naeringer:
        base_count, base_lonn = naering_data[n_code]
        for c_code in contents:
            for q_idx, q in enumerate(quarters):
                if c_code == "Lonsstakere":
                    val = base_count + random.randint(-base_count // 50, base_count // 50)
                else:
                    val = base_lonn + random.randint(-1000, 1000)
                values.append(val)

    return {
        "class": "dataset",
        "id": ["NACE2007", "ContentsCode", "Tid"],
        "size": [len(naeringer), len(contents), len(quarters)],
        "dimension": {
            "NACE2007": {
                "category": {
                    "index": {code: i for i, code in enumerate(naeringer)},
                    "label": naeringer,
                }
            },
            "ContentsCode": {
                "category": {
                    "index": {code: i for i, code in enumerate(contents)},
                    "label": contents,
                }
            },
            "Tid": {
                "category": {
                    "index": {code: i for i, code in enumerate(quarters)},
                    "label": quarters,
                }
            },
        },
        "value": values,
    }
