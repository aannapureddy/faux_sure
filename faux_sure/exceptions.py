class ModelNotFoundError(Exception):
    pass


class UniqueFieldRequirementException(Exception):
    pass


class TypeFieldRequirementException(Exception):
    pass


class ValidatorFieldRequirementException(Exception):
    pass


class OneToOneException(Exception):
    pass
