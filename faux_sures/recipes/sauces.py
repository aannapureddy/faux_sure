"""
Validation Functions that help mesh relations
"""

from faux_sures.not_db import Model
from faux_sures.exceptions import OneToOneException


def one_to_one(from_model: Model, from_field: str, to_model: Model, to_field: str) -> bool:
    """
    Create a validator that enforces a One to One field

    Args:
        from_model (Model): First model
        from_field (str): First models field
        to_model (Model): Second model
        to_field (str): Second models field

    Returns:
        True if both references point back to each other
    """

    if not getattr(from_model, from_field) == to_model:
        raise OneToOneException(f"{from_model} to {to_model} is not One to One")
    if not getattr(to_model, to_field) == from_model:
        raise OneToOneException(f"{from_model} to {to_model} is not One to One")
    return True
