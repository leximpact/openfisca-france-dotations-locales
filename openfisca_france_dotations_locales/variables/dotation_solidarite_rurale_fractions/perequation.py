from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *
from numpy import sum as sum_, where
from openfisca_france_dotations_locales.variables.base import safe_divide


class dsr_eligible_fraction_perequation(Variable):
    value_type = bool
    entity = Commune
    definition_period = YEAR
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
    documentation = '''
        La deuxième fraction de la dotation de solidarité rurale est attribuée
        aux communes de moins de 10 000 habitants dont le potentiel financier par habitant
        est inférieur au double du potentiel financier moyen par habitant
        des communes appartenant à la même strate démographique.
        La population à prendre en compte est également la population DGF 2019.
    '''

    def formula(commune, period, parameters):
        seuil_nombre_habitants = parameters(period).dotation_solidarite_rurale.seuil_nombre_habitants
        population_dgf = commune('population_dgf', period)

        potentiel_financier_par_habitant = commune('potentiel_financier_par_habitant', period)
        potentiel_financier_par_habitant_strate = commune('potentiel_financier_par_habitant_moyen', period)
        plafond_ratio_pot_fin = parameters(period).dotation_solidarite_rurale.perequation.seuil_rapport_potentiel_financier
        plafond = plafond_ratio_pot_fin * potentiel_financier_par_habitant_strate
        outre_mer = commune('outre_mer', period)
        return (~outre_mer) * (population_dgf < seuil_nombre_habitants) * (potentiel_financier_par_habitant <= plafond)


pourcentage_accroissement_dsr_pq = (653_174_468 - 645_050_872) / 90_000_000


class dsr_montant_total_fraction_perequation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant disponible pour communes éligibles DSR fraction péréquation en métropole"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
    documentation = '''
    En 2019 : La masse des crédits mis en répartition pour la DSR fraction péréquation
    en métropole s'élève en 2019 à 645 050 872 €. Le montant des garanties versées
    aux communes nouvelles inéligibles s’élève à 7 403 713 €.
    '''

    def formula_2013_01(commune, period, parameters):
        montants_an_prochain = commune('dsr_montant_total_fraction_perequation', period.offset(1, 'year'))
        accroissement = parameters(period.offset(1, 'year')).dotation_solidarite_rurale.augmentation_montant
        return montants_an_prochain - accroissement * pourcentage_accroissement_dsr_pq

    def formula_2019_01(commune, period, parameters):
        return 645_050_872

    # A partir de 2020, formule récursive qui bouge en
    # fonction des pourcentages
    # d'augmentation constatés (en vrai il faudrait défalquer
    # des pourcentages de population d'outre-mer)
    # mais c'est une autre histoire
    # La variation sera égale à pourcentage_accroissement *
    # valeur du paramètre "accroissement" pour cette année là.

    def formula_2020_01(commune, period, parameters):
        montants_an_precedent = commune('dsr_montant_total_fraction_perequation', period.last_year)
        accroissement = parameters(period).dotation_solidarite_rurale.augmentation_montant
        return montants_an_precedent + accroissement * pourcentage_accroissement_dsr_pq


class dsr_montant_total_eligibles_fraction_perequation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant disponible pour communes éligibles DSR fraction péréquation en métropole"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"
    documentation = '''
    En 2019 : La masse des crédits mis en répartition pour la DSR fraction péréquation
    en métropole s'élève en 2019 à 645 050 872 €.
    2020 : 653 174 468 € au titre de la fraction « péréquation » (soit 1,26 % de plus qu’en 2019)
    '''

    def formula(commune, period, parameters):
        dsr_montant_total_fraction_perequation = commune('dsr_montant_total_fraction_perequation', period)
        dsr_garantie_commune_nouvelle_fraction_perequation = commune('dsr_garantie_commune_nouvelle_fraction_perequation', period)
        dsr_eligible_fraction_perequation = commune('dsr_eligible_fraction_perequation', period)
        montant_total_a_attribuer = dsr_montant_total_fraction_perequation - ((~dsr_eligible_fraction_perequation) * dsr_garantie_commune_nouvelle_fraction_perequation).sum()

        return montant_total_a_attribuer


class dsr_montant_total_eligibles_fraction_perequation_part_potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction péréquation - potentiel financier par habitant:\
        Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction péréquation de la DSR au titre du potentiel financier par habitant"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_potentiel_financier_par_habitant
        return commune('dsr_montant_total_eligibles_fraction_perequation', period) * poids


class dsr_montant_total_eligibles_fraction_perequation_part_longueur_voirie(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction péréquation - longueur voirie:\
        Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction péréquation de la DSR au titre de la longueur de voirie"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_longueur_voirie
        return commune('dsr_montant_total_eligibles_fraction_perequation', period) * poids


class dsr_montant_total_eligibles_fraction_perequation_part_enfants(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction péréquation - nombre d'enfants:\
        Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction péréquation de la DSR au titre du nombre d'enfants"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_enfants
        return commune('dsr_montant_total_eligibles_fraction_perequation', period) * poids


class dsr_montant_total_eligibles_fraction_perequation_part_potentiel_financier_par_hectare(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total DSR fraction péréquation - potentiel financier par hectare:\
        Valeur totale attribuée (hors garanties de stabilité) aux communes éligibles à la fraction péréquation de la DSR au titre du potentiel financier par hectare"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        poids = parameters(period).dotation_solidarite_rurale.attribution.poids_potentiel_financier_par_hectare
        return commune('dsr_montant_total_eligibles_fraction_perequation', period) * poids


class dsr_score_attribution_perequation_part_potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction péréquation - potentiel financier par habitant:\
        Score d'attribution de la fraction péréquation de la DSR au titre du potentiel financier par habitant"
    reference = [
        "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633",
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """1° Pour 30 % de son montant, en fonction de la population
    pondérée par l'écart entre le potentiel financier par habitant de la
    commune et le potentiel financier moyen par habitant des communes
    appartenant au même groupe démographique ainsi que par l'effort fiscal
    plafonné à 1,2 ;"""

    def formula(commune, period, parameters):
        potentiel_financier_par_habitant = commune('potentiel_financier_par_habitant', period)
        potentiel_financier_par_habitant_strate = commune('potentiel_financier_par_habitant_moyen', period)
        effort_fiscal = commune('effort_fiscal', period)
        dsr_eligible_fraction_perequation = commune("dsr_eligible_fraction_perequation", period)
        population_dgf = commune('population_dgf', period)

        plafond_effort_fiscal = parameters(period).dotation_solidarite_rurale.attribution.plafond_effort_fiscal

        facteur_pot_fin = max_(0, 2 - safe_divide(potentiel_financier_par_habitant, potentiel_financier_par_habitant_strate, 0))
        facteur_effort_fiscal = min_(plafond_effort_fiscal, effort_fiscal)

        return dsr_eligible_fraction_perequation * population_dgf * facteur_pot_fin * facteur_effort_fiscal


class dsr_score_attribution_perequation_part_longueur_voirie(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction péréquation - longueur voirie:\
        Score d'attribution de la fraction péréquation de la DSR au titre de la voirie"
    reference = [
        "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633",
        "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """2° Pour 30 % de son montant, proportionnellement à la longueur
    de la voirie classée dans le domaine public communal ; pour les communes situées
    en zone de montagne ou pour les communes insulaires, la longueur de la voirie est
    doublée. Pour l'application du présent article, une commune insulaire s'entend
    d'une commune de métropole située sur une île qui, n'étant pas reliée au continent
    par une infrastructure routière, comprend une seule commune ou un seul
    établissement public de coopération intercommunale
    """

    def formula(commune, period, parameters):
        longueur_voirie = commune('longueur_voirie', period)
        zone_de_montagne = commune('zone_de_montagne', period)
        dsr_eligible_fraction_perequation = commune("dsr_eligible_fraction_perequation", period)
        insulaire = commune('insulaire', period)

        return dsr_eligible_fraction_perequation * longueur_voirie * where(insulaire | zone_de_montagne, 2, 1)


class dsr_score_attribution_perequation_part_enfants(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction péréquation - enfants:\
        Score d'attribution de la fraction péréquation de la DSR au titre du nombre d'enfants dans la population"
    reference = ["https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633",
            "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """3° Pour 30 % de son montant, proportionnellement au nombre
    d'enfants de trois à seize ans domiciliés dans la commune, établi lors du dernier
    recensement.
    """

    def formula(commune, period, parameters):
        population_enfants = commune('population_enfants', period)
        dsr_eligible_fraction_perequation = commune("dsr_eligible_fraction_perequation", period)

        return dsr_eligible_fraction_perequation * population_enfants


class dsr_score_attribution_perequation_part_potentiel_financier_par_hectare(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Score DSR fraction péréquation - potentiel financier par hectare:\
        Score d'attribution de la fraction péréquation de la DSR au titre du potentiel financier par hectare"
    reference = ["https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633",
            "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"]
    documentation = """4° Pour 10 % de son montant au maximum, en fonction de
    l'écart entre le potentiel financier par hectare de la commune et le potentiel
    financier moyen par hectare des communes de moins de 10 000 habitants."""

    def formula(commune, period, parameters):
        potentiel_financier = commune('potentiel_financier', period)
        outre_mer = commune('outre_mer', period)
        potentiel_financier_par_habitant = commune('potentiel_financier_par_hectare', period)
        dsr_eligible_fraction_perequation = commune("dsr_eligible_fraction_perequation", period)
        population_dgf = commune('population_dgf', period)
        # oui le taille_max_commune est le même que pour le seuil d'éligibilité, notre paramétrisation est ainsi
        taille_max_commune = parameters(period).dotation_solidarite_rurale.seuil_nombre_habitants
        superficie = commune('superficie', period)
        communes_moins_10000 = (~outre_mer) * (population_dgf < taille_max_commune)

        pot_fin_par_hectare_10000 = (sum_(communes_moins_10000 * potentiel_financier)
                / sum_(communes_moins_10000 * superficie))

        facteur_pot_fin = max_(0, 2 - potentiel_financier_par_habitant / pot_fin_par_hectare_10000)

        return dsr_eligible_fraction_perequation * population_dgf * facteur_pot_fin


class dsr_valeur_point_fraction_perequation_part_potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Valeur du point DSR fraction péréquation - part potentiel financier par habitant"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        montant_total_a_attribuer = commune("dsr_montant_total_eligibles_fraction_perequation_part_potentiel_financier_par_habitant", period)
        dsr_score_attribution = commune("dsr_score_attribution_perequation_part_potentiel_financier_par_habitant", period)
        score_total = dsr_score_attribution.sum()
        return montant_total_a_attribuer / score_total


class dsr_valeur_point_fraction_perequation_part_longueur_voirie(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Valeur du point DSR fraction péréquation - part longueur de voirie"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        montant_total_a_attribuer = commune("dsr_montant_total_eligibles_fraction_perequation_part_longueur_voirie", period)
        dsr_score_attribution = commune("dsr_score_attribution_perequation_part_longueur_voirie", period)
        score_total = dsr_score_attribution.sum()
        return montant_total_a_attribuer / score_total


class dsr_valeur_point_fraction_perequation_part_enfants(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Valeur du point DSR fraction péréquation - part enfants"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        montant_total_a_attribuer = commune("dsr_montant_total_eligibles_fraction_perequation_part_enfants", period)
        dsr_score_attribution = commune("dsr_score_attribution_perequation_part_enfants", period)
        score_total = dsr_score_attribution.sum()
        return montant_total_a_attribuer / score_total


class dsr_valeur_point_fraction_perequation_part_potentiel_financier_par_hectare(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Valeur du point DSR fraction péréquation - part potentiel financier par hectare"
    reference = "http://www.dotations-dgcl.interieur.gouv.fr/consultation/documentAffichage.php?id=94"

    def formula(commune, period, parameters):
        montant_total_a_attribuer = commune("dsr_montant_total_eligibles_fraction_perequation_part_potentiel_financier_par_hectare", period)
        dsr_score_attribution = commune("dsr_score_attribution_perequation_part_potentiel_financier_par_hectare", period)
        score_total = dsr_score_attribution.sum()
        return montant_total_a_attribuer / score_total


class dsr_fraction_perequation_part_potentiel_financier_par_habitant(Variable):
    value_type = float
    entity = Commune
    label = "Valeur attribuée (hors garanties de stabilité) à la commune pour la \
    fraction péréquation de la DSR au titre du potentiel financier par habitant"
    definition_period = YEAR

    def formula(commune, period, parameters):
        scores = commune("dsr_score_attribution_perequation_part_potentiel_financier_par_habitant", period)
        valeur_point = commune("dsr_valeur_point_fraction_perequation_part_potentiel_financier_par_habitant", period)
        return scores * valeur_point


class dsr_fraction_perequation_part_longueur_voirie(Variable):
    value_type = float
    entity = Commune
    label = "Valeur attribuée (hors garanties de stabilité) à la commune pour la \
    fraction péréquation de la DSR au titre des enfants"
    definition_period = YEAR

    def formula(commune, period, parameters):
        scores = commune("dsr_score_attribution_perequation_part_longueur_voirie", period)
        valeur_point = commune("dsr_valeur_point_fraction_perequation_part_longueur_voirie", period)
        return scores * valeur_point


class dsr_fraction_perequation_part_enfants(Variable):
    value_type = float
    entity = Commune
    label = "Valeur attribuée (hors garanties de stabilité) à la commune pour la \
    fraction péréquation de la DSR au titre de la longueur de voirie"
    definition_period = YEAR

    def formula(commune, period, parameters):
        scores = commune("dsr_score_attribution_perequation_part_enfants", period)
        valeur_point = commune("dsr_valeur_point_fraction_perequation_part_enfants", period)
        return scores * valeur_point


class dsr_fraction_perequation_part_potentiel_financier_par_hectare(Variable):
    value_type = float
    entity = Commune
    label = "Valeur attribuée (hors garanties de stabilité) à la commune pour la \
    fraction péréquation de la DSR au titre du potentiel financier par hectare"
    definition_period = YEAR

    def formula(commune, period, parameters):
        scores = commune("dsr_score_attribution_perequation_part_potentiel_financier_par_hectare", period)
        valeur_point = commune("dsr_valeur_point_fraction_perequation_part_potentiel_financier_par_hectare", period)
        return scores * valeur_point


class dsr_montant_hors_garanties_fraction_perequation(Variable):
    value_type = float
    entity = Commune
    label = "Valeurs attribuée hors garanties de stabilité aux communes éligibles au titre de la fraction péréquation de la DSR"
    definition_period = YEAR

    def formula(commune, period, parameters):
        part_potentiel_financier_par_habitant = commune('dsr_fraction_perequation_part_potentiel_financier_par_habitant', period)
        part_longueur_voirie = commune('dsr_fraction_perequation_part_longueur_voirie', period)
        part_enfants = commune('dsr_fraction_perequation_part_enfants', period)
        part_potentiel_financier_par_hectare = commune('dsr_fraction_perequation_part_potentiel_financier_par_hectare', period)
        return (part_potentiel_financier_par_habitant
        + part_longueur_voirie
        + part_enfants
        + part_potentiel_financier_par_hectare)


class dsr_montant_eligible_fraction_perequation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant attribué fraction péréquation après garanties de stabilité:\
        Valeur attribuée incluant garanties de stabilité aux communes éligibles au titre de la fraction péréquation de la DSR"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"
    documentation = '''
        A compter de 2012, l'attribution au titre de cette fraction d'une
        commune éligible ne peut être ni inférieure à 90 % ni supérieure à 120 %
        du montant perçu l'année précédente.
        '''

    def formula(commune, period, parameters):
        plancher_progression = parameters(period).dotation_solidarite_rurale.perequation.attribution.plancher_ratio_progression
        plafond_progression = parameters(period).dotation_solidarite_rurale.perequation.attribution.plafond_ratio_progression
        montant_an_precedent = commune("dsr_montant_eligible_fraction_perequation", period.last_year)
        dsr_montant_hors_garanties_fraction_perequation = commune("dsr_montant_hors_garanties_fraction_perequation", period)
        return where((dsr_montant_hors_garanties_fraction_perequation > 0) & (montant_an_precedent > 0), max_(plancher_progression * montant_an_precedent, min_(plafond_progression * montant_an_precedent, dsr_montant_hors_garanties_fraction_perequation)), dsr_montant_hors_garanties_fraction_perequation)


class dsr_garantie_commune_nouvelle_fraction_perequation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Garantie commune nouvelle DSR fraction péréquation:\
        Montant garanti aux communes nouvelles au titre de la fraction péréquation de la dotation de solidarité rurale"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000041473401&cidTexte=LEGITEXT000006070633"
    documentation = '''Au cours des trois années suivant le 1er janvier de l'année de leur création,
        les communes nouvelles [...] perçoivent des attributions au titre [...] des trois
        fractions de la dotation de solidarité rurale au moins égales aux attributions
        perçues au titre de chacune de ces dotations par les anciennes communes l'année
        précédant la création de la commune nouvelle.'''


class dsr_fraction_perequation(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant effectivement attribué DSR fraction péréquation:\
        Montant attribué à la commune au titre de la fraction péréquation de la DSR après garanties de stabilité, et de commune nouvelle"
    reference = "https://www.legifrance.gouv.fr/affichCodeArticle.do?idArticle=LEGIARTI000036433094&cidTexte=LEGITEXT000006070633"

    def formula(commune, period, parameters):
        dsr_garantie_commune_nouvelle_fraction_perequation = commune("dsr_garantie_commune_nouvelle_fraction_perequation", period)
        dsr_montant_eligible_fraction_perequation = commune("dsr_montant_eligible_fraction_perequation", period)
        return max_(
            dsr_montant_eligible_fraction_perequation,
            dsr_garantie_commune_nouvelle_fraction_perequation
            )
