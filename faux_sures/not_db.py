"""
Classes for modeling data 
"""
from __future__ import annotations

import functools
import pydoc
import uuid

from collections import defaultdict
from dataclasses import dataclass, field as dataclass_field, fields as list_dataclass_fields
from typing import Any, Callable, Dict, Iterable, Optional, Type, Tuple, Union, Set, Generator, no_type_check

from faux_sures.exceptions import (
    ModelNotFoundError,
    TypeFieldRequirementException,
    UniqueFieldRequirementException,
    ValidatorFieldRequirementException,
)

ValidatorType = Callable[[Any], bool]


@no_type_check
@functools.lru_cache
def get_type_from_class_name(class_name: Union[str, Type]) -> Type:
    if isinstance(class_name, Type):
        return class_name
    return pydoc.locate(class_name)


class Field:
    """
    A field for a model complete with typing and validation
    """

    def __init__(
        self,
        _type: Union[Type, str],
        validators: Union[ValidatorType, Iterable[ValidatorType]] = tuple(),
        optional: bool = False,
    ):
        """
        Args:
            _type (Type or Str): Appropriate Type. If string instead of type object is passed, lexical cast to type at set time
            validators (Iterable[Callable[[Any] Any]]): Single or Collection of validation functions
            optional (bool): Whether this value is allowed to be None and skip the type and validation checks
        """

        if isinstance(_type, str):
            self.lexical_cast = True
        else:
            self.lexical_cast = False
        self._type = _type
        self.validators: Tuple[ValidatorType] = (
            tuple(validators) if isinstance(validators, Iterable) else (validators,)  # type: ignore
        )
        self.optional = optional
        self.name: Optional[str]

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if not instance:
            return self
        return instance.__dict__.get(self.name, None)

    def __delete__(self, instance):
        del instance.__dict__[self.name]

    def __set__(self, instance, value):

        if self.lexical_cast:
            self._type = get_type_from_class_name(self._type)
            self.lexical_cast = False

        if value is None and self.optional is True:
            pass
        elif not isinstance(value, self._type):
            raise TypeFieldRequirementException(
                f"{self.name!r} values must one of types {self._type!r} not {type(value)}"
            )
        if value is not None:
            for validator in self.validators:
                if validator(value) is False:
                    raise ValidatorFieldRequirementException(f"{self.name} failed to validate {validator.__name__}")
        instance.__dict__[self.name] = value


class UniqueTogetherRestraint:
    """
    Add a check for unique values over a single or a series of values
    """

    def __init__(self, unique_fields: Union[str, Iterable[str]]):
        if not unique_fields:
            raise ValueError("Fields must be supplied for unique constraint")
        self.unique_fields: Tuple[str] = (
            (unique_fields,) if isinstance(unique_fields, str) else tuple(unique_fields)  # type: ignore
        )


@dataclass
class Model:
    """
    Base Data Model
    """

    pk: str = dataclass_field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def class_name(self):
        return str(self.__class__.__name__)

    def __deepcopy__(self, memodict={}):
        """Never duplicate internal key. Preserve unset Fields"""
        _dcopy = self.__class__()
        fields = {f.name for f in list_dataclass_fields(self)}
        fields.remove("pk")
        for _field, value in self.__dict__.items():
            if _field in fields:
                setattr(_dcopy, _field, value)
        return _dcopy

    def serialize(self) -> Dict[str, str]:
        """
        Return dictionary representation of self
        None is represented as empty string
        """
        fields = {f.name for f in list_dataclass_fields(self)}
        return {f: v if v is not None else "" for f, v in self.__dict__.items() if f in fields}

    def checks(self):
        """Run more complicated check functions over the fields of single model"""
        pass

    def iterate_model_fields(self) -> Generator[Optional[str], None, None]:
        """
        Iterate over all attributes of type Field defined for the class
        """
        for _field in vars(self.__class__).values():
            if isinstance(_field, Field):
                yield _field.name

    def iterate_unique_constraints(self) -> Generator[Tuple, None, None]:
        """
        Iterate over all unique constraints and yield values together

        Raises Attribute Exception if field does not exist on Model
        """
        unique_constraints = (
            c_field for c_field in vars(self.__class__).values() if isinstance(c_field, UniqueTogetherRestraint)
        )
        for constraint in unique_constraints:
            values = (getattr(self, value) for value in constraint.unique_fields)
            yield (self.class_name, *values)

    def validate(self):
        """
        Run all validation for a single model
        Raises
            TypeFieldRequirementException if a field is set to None when it is not Optional
            ValidatorFieldRequirementException if a field does not pass a set Validation Requirement
            Other Custom Exceptions if defined on the model


        Args:
            model (Model): Model with Fields for validation and custom checks
        """

        for _field_name in self.iterate_model_fields():
            if getattr(self, _field_name) is None:
                setattr(self, _field_name, None)  # trigger __set__ checks
        self.checks()


class Session:
    """
    Create a singleton session that stores the models and runs validation at commit
    """

    class Indexes:
        """
        An extendable collection of indexes of references
        """

        model_index: Dict[str, Model] = dict()
        class_index: Dict[str, Set[str]] = defaultdict(set)

        @classmethod
        def flush(cls):
            """
            Clear contents and restart
            """
            cls.model_index = dict()
            cls.class_index = defaultdict(set)

    @classmethod
    def add(cls, model: Model):
        """Add a new Model to session and update references"""

        key = model.pk
        cls.Indexes.model_index[key] = model
        cls.Indexes.class_index[model.class_name].add(key)

    @classmethod
    def query_by_key(cls, pk: str) -> Model:
        """From a key recover the original Model. Raises ModelNotFoundError if not found"""
        try:
            return cls.Indexes.model_index[pk]
        except KeyError:
            raise ModelNotFoundError(f"No record {pk} in session")

    @classmethod
    def query_by_type_name(cls, class_name: str) -> Generator[Model, None, None]:
        """Iterate over all objects of a class. Raises ModelNotFoundError if class name is not found"""

        try:
            models = cls.Indexes.class_index[class_name]
        except KeyError:
            raise ModelNotFoundError(f"No record of type {class_name} in session")

        for key in models:
            yield cls.query_by_key(key)

    @classmethod
    def remove(cls, pk: str) -> bool:
        """
        Pass a Model key and remove the Model's references from the session

        Args:
            pk (str): A Model's internal key

        Returns:
            bool: If references were removed
        """
        try:
            model = Session.query_by_key(pk)
        except KeyError:
            return False
        del cls.Indexes.model_index[pk]
        cls.Indexes.class_index[model.class_name].remove(pk)
        return True

    @classmethod
    def commit(cls):
        """
        Run validation and index checks over all added models

        Raises:
            TypeFieldRequirementException if a field is set to None when it is not Optional
            ValidatorFieldRequirementException if a field does not pass a set Validation Requirement
            UniqueFieldRequirementException if fields across Models do not match Uniqueness Requirements
            Other Custom Exceptions if defined on the model


        """
        uniqueness_tracker: Set[Tuple] = set()

        def check_unique(values: Tuple) -> bool:
            """Update unique tracker and return True on unique add"""
            if values in uniqueness_tracker:
                return False
            uniqueness_tracker.add(values)
            return True

        model: Model
        for model in cls.Indexes.model_index.values():
            model.validate()
            for unique_tuple in model.iterate_unique_constraints():
                if not check_unique(unique_tuple):
                    raise UniqueFieldRequirementException(
                        f"{model.class_name}: {model.pk} fails unique constraint for {unique_tuple[1:]}"
                    )

    @classmethod
    def reset(cls):
        """
        Clear contents and restart
        """
        cls.Indexes.flush()

    def __enter__(self):
        return self

    def __close__(self, *args):
        self.reset()
