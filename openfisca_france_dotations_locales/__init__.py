# -*- coding: utf-8 -*-

import os

from openfisca_core.taxbenefitsystems import TaxBenefitSystem

from openfisca_france_dotations_locales import entities
from openfisca_france_dotations_locales.situation_examples import communes_dsr


COUNTRY_DIR = os.path.dirname(os.path.abspath(__file__))


# Our country specific microsimulation system class inherits from the general TaxBenefitSystem class.
# The name CountryTaxBenefitSystem must not be changed,
# as all tools of the OpenFisca ecosystem expect a CountryTaxBenefitSystem class
# to be exposed in the __init__ module of a country package.
class CountryTaxBenefitSystem(TaxBenefitSystem):
    def __init__(self):
        # We initialize our microsimulation system with the general constructor
        super(CountryTaxBenefitSystem, self).__init__(entities.entities)

        # We add to our microsimulation system all the variables
        self.add_variables_from_directory(os.path.join(COUNTRY_DIR, 'variables'))

        # We add to our microsimulation system all the legislation parameters defined in the  parameters files
        param_path = os.path.join(COUNTRY_DIR, 'parameters')
        self.load_parameters(param_path)

        # We define which variable, parameter and simulation example will be used in the OpenAPI specification
        self.open_api_config = {
            "variable_example": "population_dgf_plafonnee",
            "parameter_example": "dotation_solidarite_rurale.seuil_nombre_habitants",
            "simulation_example": communes_dsr,
            }
