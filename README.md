## Faux Sures: The REPL object manager for ProtoTyping domain logic with objects and relations. For Python.
Faux Sures provides a heavily typed system with immediate validation checks to provide a tactile experience while exploring complex domain logic.
Faux Sures is designed for use in a python shell, a notebook, or a short script. The self evaluating Fields system triggers everytime you set an attribute on a model, giving you guardrails while you play around with data. All while encapsulating logic in the Model definition itself
 
### Current Development:
- This package is still in its infancy see below for current issues
- Github Issues is used for reporting both Bugs and requesting Features
- Current development is limiting the traceback printout to a single line


### Examples:

#### See [The Intramural Sports League Story Test](https://github.com/aannapureddy/faux_sure/blob/main/example_tests/test_team_sports/test_team_sports.py)
```
In [5]: from faux_sures import not_db

In [6]: from faux_sures.recipes.curries import in_range

In [7]: class Student(not_db.Model):
   ...:     first_name = not_db.Field(str)
   ...:     last_name = not_db.Field(str)
   ...:     age = not_db.Field(int, in_range(14, 19))
   ...: 
   ...:     name_constraint = not_db.UniqueTogetherRestraint(("first_name", "last_name"))
   ...: 

In [8]: arjun = Student()

In [9]: arjun.age = "13"
---------------------------------------------------------------------------
TypeFieldRequirementException             Traceback (most recent call last)
<ipython-input-9-0a7edcc14936> in <module>
----> 1 arjun.age = "13"

~/Documents/code/faux_sures/faux_sures/not_db.py in __set__(self, instance, value)
     79             pass
     80         elif not isinstance(value, self._type):
---> 81             raise TypeFieldRequirementException(
     82                 f"{self.name!r} values must one of types {self._type!r} not {type(value)}"
     83             )

TypeFieldRequirementException: 'age' values must one of types <class 'int'> not <class 'str'>

In [10]: arjun.age = 13
---------------------------------------------------------------------------
ValidatorFieldRequirementException        Traceback (most recent call last)
<ipython-input-10-65acbd50e86f> in <module>
----> 1 arjun.age = 13

~/Documents/code/faux_sures/faux_sures/not_db.py in __set__(self, instance, value)
     85             for validator in self.validators:
     86                 if validator(value) is False:
---> 87                     raise ValidatorFieldRequirementException(f"{self.name} failed to validate {validator.__name__}")
     88         instance.__dict__[self.name] = value
     89 

ValidatorFieldRequirementException: age failed to validate in_range_14_to_19

In [11]: arjun.age = 17

In [12]: arjun.age
Out[12]: 17

```

### Why you might like Faux Sure
- You like working with Jupyter Notebooks and Ipython
- You are more concerned with solving the domain logic than writing optimized code
- You appreciate the security of a strongly typed system
- You write short scripts over a common memory resource with complex logic
- You like objects and have an imperative mood. But are afraid of regressions
- You are preoccupied with correctness and human understanding. The final solution can wait.

### Why Faux Sure might not be right for you
- You've already got the domain logic figured out completely
- You find strong typing difficult to work with.
- You care about performance. You care about memory overhead.
- You already have a database connected with Check statements
- You'd rather not have code with Side Effects.


### Features
- Field validation by types or validator functions
- Patterns for currying and composing validator functions
- Object relations via higher order types. Validator functions for high order types
- Validator fields for more complex checks such as Unique Together
- Model level checks at commit time
- Domain wide checks at commit time
- Single Class Session which enables state tracking between discrete steps


## Installation
```
pip install faux-sures==0.0.1
```

### Issues and Contributing:
 - Please Help by opening issues and bugs in Issues. For now the Issues page is the project board.
 - If you'd like to contribute code, please open a PR. There is a requirement to pass code quality checks.
 - Current line of progress is limiting the traceback as a default option.
 - Second line of progress is adding more tests and "Story" tests which stress the interactions between 
 - Third line of progress is making Object Relations more ergonomic.
