from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *


class dotation_forfaitaire(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total de la dotation forfaitaire (DF)"
    reference = "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070633/LEGISCTA000006192290?etatTexte=VIGUEUR&etatTexte=VIGUEUR_DIFF#LEGISCTA000006192290"

    def formula_2018(commune, period, parameters):
        dotation_forfaitaire_an_dernier = commune('dotation_forfaitaire', period.offset(1, 'year'))
        part_compensations_part_salaires = commune('part_compensations_part_salaires', period)
        return dotation_forfaitaire_an_dernier + part_compensations_part_salaires


class part_compensations_part_salaires(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Retraitement CPS: \
        retraitement des compensations part salaires (CPS) transférées aux communes (dite part CPS)"
    reference = "https://www.collectivites-locales.gouv.fr/files/files/dgcl_v2/FLAE_circulaires_10_fevrier2016/note_dinformation_2019_dfcom_-_vdef2.pdf"


class df_eligible_ecretement(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    label = "Eligibilité à l'écrêtement de la dotation forfaitaire:\
        La commune est éligible à subir un écrêtement de sa dotation forfaitaire"
    reference = "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070633/LEGISCTA000006192290?etatTexte=VIGUEUR&etatTexte=VIGUEUR_DIFF#LEGISCTA000006192290"
    documentation = '''
        A compter de 2012, les communes dont le potentiel fiscal par habitant est inférieur à 0,75 fois \
        le potentiel fiscal moyen par habitant constaté pour l'ensemble des communes bénéficient \
        d'une attribution au titre de la garantie égale à celle perçue l'année précédente. \
        Pour les communes dont le potentiel fiscal par habitant est supérieur ou égal à 0,75 fois \
        le potentiel fiscal moyen par habitant constaté pour l'ensemble des communes, ce montant est diminué
        '''


class df_montant_total_ecretement(Variable):
    value_type = int
    entity = Etat
    definition_period = YEAR
    label = "Montant total d'écrêtement à la dotation forfaitaire"
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033878417"


class df_montant_total_ecretement_hors_dsu_dsr(Variable):
    value_type = int
    entity = Etat
    definition_period = YEAR
    label = "Montant total à écréter à la dotation forfaitaire hors variations de la DSU et de la DSR"
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033878417"


class df_score_attribution_ecretement(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score d'attribution de l'écrêtement de la dotation forfaitaire:\
        Score au prorata duquel l'écrêtement de la dotation forfaitaire est calculé"
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037994287"
    documentation = '''
        Le montant [...] est diminué [...] en proportion de leur population et de l'écart relatif \
        entre le potentiel fiscal par habitant de la commune et 0,75 fois le potentiel fiscal moyen \
        par habitant constaté pour l'ensemble des communes.
        '''


class df_evolution_part_dynamique(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Part dynamique de la dotation forfaitaire:\
        Évolution de la dotation forfaitaire consécutive aux changements de population DGF majorée"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=115"
    documentation = '''
        Il est, selon le cas, ajouté ou soustrait à la dotation forfaitaire ainsi retraitée \
        une part calculée en fonction de l’évolution de la population DGF entre 2019 et 2020 \
        et d’un montant compris entre 64,46 € et 128,93 € calculé en fonction croissante \
        de la population de la commune.
        '''
