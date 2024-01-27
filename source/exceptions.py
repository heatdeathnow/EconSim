class NegativeAmountError(Exception):
    """ An object that represents something physical has negative size. """

class CannotEmployError(Exception):
    """ A object attempted to employ a pop that is not allowed to be employed. """

class EfficiencyError(Exception):
    """ Over 100% efficiency is not allowed. """