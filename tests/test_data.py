
import pandas


def test_csv_communes_criteres_repartition():
    csv_communes_criteres_repartition = './data/2019-communes-criteres-repartition.csv'

    communes_criteres_repartition_2019 = pandas.read_csv(
        csv_communes_criteres_repartition,
        decimal=",")

    assert len(communes_criteres_repartition_2019["Informations générales - Nom de la commune"]) == 35056

    # nombre_habitants = communes_criteres_repartition_2019[
    #     "Informations générales - Population DGF Année N'"
    #     ]
    # pfi_habitant = communes_criteres_repartition_2019[
    #     "Potentiel fiscal et financier des communes - Potentiel financier par habitant"
    #     ]
    # codes_insee = communes_criteres_repartition_2019[
    #     "Informations générales - Code INSEE de la commune"
    # ]
