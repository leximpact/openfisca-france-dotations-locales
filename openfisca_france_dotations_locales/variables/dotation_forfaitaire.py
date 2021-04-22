from openfisca_core.model_api import *
from openfisca_france_dotations_locales.entities import *
from numpy import log10, where
from openfisca_france_dotations_locales.variables.base import safe_divide


class dotation_forfaitaire(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Montant total de la dotation forfaitaire (DF)"
    reference = "https://www.legifrance.gouv.fr/codes/section_lc/LEGITEXT000006070633/LEGISCTA000006192290?etatTexte=VIGUEUR&etatTexte=VIGUEUR_DIFF#LEGISCTA000006192290"

    def formula_2018(commune, period, parameters):
        dotation_forfaitaire_an_dernier = commune('dotation_forfaitaire', period.last_year)
        df_evolution_part_dynamique = commune('df_evolution_part_dynamique', period)
        df_montant_ecretement = commune('df_montant_ecretement', period)
        return max_(0, dotation_forfaitaire_an_dernier + df_evolution_part_dynamique - df_montant_ecretement)


class df_coefficient_logarithmique(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Dotation forfaitaire : coefficient logarithmique de la population prise en compte:\
    Coefficient appliqué à la population non majorée pour calcul de la dotation forfaitaire"
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037994287"
    documentation = '''La population prise en compte pour la détermination du potentiel fiscal par habitant est corrigée par un coefficient logarithmique dont la valeur varie de 1 à 2 en fonction croissante de la population de la commune tel que défini pour l'application du 1° du présent I ;'''

    def formula(commune, period, parameters):
        population_dgf = commune('population_dgf', period)

        # On établit le coefficient logarithmique.
        # C'est pas exactement le même que celui dans le calcul
        # de la part dynamique : ici la population dgf n'est
        # pas majorée
        plancher_dgcl_population_dgf = 500
        plafond_dgcl_population_dgf = 200000
        facteur_du_coefficient_logarithmique = 1 / (log10(plafond_dgcl_population_dgf / plancher_dgcl_population_dgf))  # le fameux 0.38431089
        coefficient_logarithmique = max_(1, min_(2, 1 + facteur_du_coefficient_logarithmique * log10(population_dgf / plancher_dgcl_population_dgf)))
        return coefficient_logarithmique


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

        Ici, on déclare comme éligible les communes qui :
          - ont plus de 0.75 du potentiel fiscal moyen
          - auraient une df non nulle hors écrètement
        '''

    def formula(commune, period, parameters):
        pourcentage_potentiel_fiscal = parameters(period).dotation_forfaitaire.ecretement.seuil_rapport_potentiel_fiscal
        potentiel_fiscal = commune('potentiel_fiscal', period)
        df_coefficient_logarithmique = commune("df_coefficient_logarithmique", period)
        population_dgf = commune('population_dgf', period)

        population_logarithmee = population_dgf * df_coefficient_logarithmique
        potentiel_fiscal_moyen_commune = where(population_logarithmee > 0, potentiel_fiscal / population_logarithmee, 0)
        potentiel_fiscal_moyen_national = commune.etat('potentiel_fiscal_moyen_national', period)
        df_an_dernier = commune('dotation_forfaitaire', period.last_year)
        df_evolution_part_dynamique = commune("df_evolution_part_dynamique", period)
        df_hors_ecretement = max_(0, df_an_dernier + df_evolution_part_dynamique)
        df_ecretement_eligible = (potentiel_fiscal_moyen_commune >= pourcentage_potentiel_fiscal * potentiel_fiscal_moyen_national) * (df_hors_ecretement > 0)
        return df_ecretement_eligible


class montant_total_ecretement(Variable):
    value_type = int
    entity = Etat
    definition_period = YEAR
    label = "Montant total d'écrêtement qui sera ventilé entre la dotation forfaitaire et la dotation des EPCI"
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033878417"

    def formula(etat, period, parameters):
        df_montant_total_ecretement_hors_dsu_dsr = etat('df_montant_total_ecretement_hors_dsu_dsr', period)
        accroissement_dsr = parameters(period).dotation_solidarite_rurale.augmentation_montant
        accroissement_dsu = parameters(period).dotation_solidarite_urbaine.augmentation_montant
        acroissement_intercommunalite = parameters(period).dotation_intercommunalite.augmentation_montant
        df_evolution_part_dynamique = etat.members('df_evolution_part_dynamique', period)
        total_evolution_part_dynamique = df_evolution_part_dynamique.sum()
        return (accroissement_dsr
            + accroissement_dsu
            + df_montant_total_ecretement_hors_dsu_dsr
            + acroissement_intercommunalite
            + total_evolution_part_dynamique)


class df_montant_total_ecretement(Variable):
    value_type = int
    entity = Etat
    definition_period = YEAR
    label = "Montant total d'écrêtement à la dotation forfaitaire"
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000033878417"
    documentation = '''
    Le pourcentage d'écrêtement est décidé par le Comité des Finances Locales.
    En 2019, extrait du rapport du gouvernement au parlement :

    Compte tenu des règles de financement entre la dotation forfaitaire des communes
    et la dotation de compensation des EPCI prévues à l’article L. 2334-7-1 du CGCT
    et des choix opérés par le CFL en 2019, 60% des coûts sont supportés
    par la dotation forfaitaire. Par conséquent, 60% du surcoût de 12,7 M€ soit 7,6 M€,
    doit être écrêté en plus.

    Source :
    https://www.banquedesterritoires.fr/sites/default/files/2019-12/Coefficient%20logarithmique%20-%20Rapport%20global%20%282%29.pdf
    '''

    def formula(etat, period, parameters):
        montant_total_ecretement = etat('montant_total_ecretement', period)
        pourcentage_ecretement_attribue_df = 0.6
        return pourcentage_ecretement_attribue_df * montant_total_ecretement


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

    def formula(commune, period, parameters):
        df_eligible_ecretement = commune('df_eligible_ecretement', period)
        df_coefficient_logarithmique = commune("df_coefficient_logarithmique", period)
        potentiel_fiscal = commune('potentiel_fiscal', period)
        population_dgf = commune('population_dgf', period)
        potentiel_fiscal_moyen_national = commune.etat('potentiel_fiscal_moyen_national', period)
        pourcentage_potentiel_fiscal = parameters(period).dotation_forfaitaire.ecretement.seuil_rapport_potentiel_fiscal
        population_logarithmee = population_dgf * df_coefficient_logarithmique
        potentiel_fiscal_moyen_commune = where(population_logarithmee > 0, potentiel_fiscal / population_logarithmee, 0)
        return where(df_eligible_ecretement,
             (potentiel_fiscal_moyen_commune
            - pourcentage_potentiel_fiscal * potentiel_fiscal_moyen_national)
            / (pourcentage_potentiel_fiscal * potentiel_fiscal_moyen_national)
            * population_dgf,
            0)


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

    def formula(commune, period, parameters):
        plancher_dgcl_population_dgf_majoree = 500
        plafond_dgcl_population_dgf_majoree = 200000
        facteur_du_coefficient_logarithmique = 1 / (log10(plafond_dgcl_population_dgf_majoree / plancher_dgcl_population_dgf_majoree))  # le fameux 0.38431089
        population_majoree_dgf = commune('population_dgf_majoree', period)
        population_majoree_dgf_an_dernier = commune('population_dgf_majoree', period.last_year)
        evolution_population = population_majoree_dgf - population_majoree_dgf_an_dernier

        facteur_minimum = parameters(period).dotation_forfaitaire.montant_minimum_par_habitant
        facteur_maximum = parameters(period).dotation_forfaitaire.montant_maximum_par_habitant
        dotation_supp_par_habitant = facteur_minimum + (facteur_maximum - facteur_minimum) * max_(0, min_(1, facteur_du_coefficient_logarithmique * log10(safe_divide(population_majoree_dgf, plancher_dgcl_population_dgf_majoree, 1))))
        return dotation_supp_par_habitant * evolution_population


class recettes_reelles_fonctionnement(Variable):
    value_type = float
    entity = Commune
    definition_period = YEAR
    label = "Recettes réelles de fonctionnement:\
    Recettes réelles de fonctionnement prises en compte pour le plafonnement de l'écrètement de la dotation forfaitaire"
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037994287"


class df_montant_ecretement(Variable):
    value_type = int
    entity = Commune
    definition_period = YEAR
    label = "Ecrètement de la dotation forfaitaire:\
    Montant retiré à la dotation forfaitaire de chaque commune"
    reference = "https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000037994287"
    documentation = '''Cette minoration ne peut être supérieure à 1 % des recettes réelles de fonctionnement de leur budget principal'''

    def formula(commune, period, parameters):
        df_montant_total_ecretement = commune.etat("df_montant_total_ecretement", period)
        df_score_attribution_ecretement = commune('df_score_attribution_ecretement', period)

        valeur_point = df_montant_total_ecretement / df_score_attribution_ecretement.sum()

        ecretement = valeur_point * df_score_attribution_ecretement
        df_an_dernier = commune('dotation_forfaitaire', period.last_year)
        df_evolution_part_dynamique = commune("df_evolution_part_dynamique", period)
        df_hors_ecretement = max_(0, df_an_dernier + df_evolution_part_dynamique)
        ecretement = min_(ecretement, df_hors_ecretement)

        # plafonnement en fonction des recettes réelles

        plafond_recettes = parameters(period).dotation_forfaitaire.ecretement.plafond_pourcentage_recettes_max
        recettes = commune("recettes_reelles_fonctionnement", period)
        ecretement = min_(ecretement, plafond_recettes * recettes)

        return ecretement
