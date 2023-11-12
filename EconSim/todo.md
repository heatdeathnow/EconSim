# Main objective:

Get what is already coded to work and run tests on it. After I have a working prototype, I can do the first GitHub push and overwrite the old simulation.

## As for now these need to be added or fixed:

- Add a way for a Province object to distribute its stockpile to the pops and have them grow

- Finish unit testing Terrain

- Add a loop that goes on forever showcasing what the simulating economy can do as of now.

- Code clean up.
  1. Create a factory that whose job will be creating the proper Population subclass object for the situation instead of running a bunch of tests every time I want to create one. These factory classes should also be responsible for all of the boiler-plate checks so that the actual classes are cleaner.
  2. Create dataclasses for _bundled-up data_ that is often passed from one method to another instead of using dictionaries. This is for readability. Also, decide if occupation names and goods names should be lowercase, uppercase, or propercase.
  3. Go through every class and decide if it should stay as is or if it should be broken up into a dataclass and a "behaviour" class or several "behaviour functions", for simplifity and readability.

### There could be a few improvements:

- Creating my own exceptions so I don't have to keep writing the error messages one by one.
- An idea: have a metaclass that automatically adds the `__str__` special method to all its class objects. After some testing and consideration, in order for this to work, attributes in classes would have to be proporties, seeing as metaclasses are the classes of classes and not of any specific object, having a defined proceedure to retrieve certain attributes that are not set at class level but only after the object calls `__init__` is impossible. <u>Unless you use `__slots__`</u>.

#### Issues solved and things that have changed:

Changed `get_labor_demand` methodo of `Industry` superclass such that now I can specify which stratum I want or if I want all of them.

Changed the `Province` class in the `Terrain` module to keep a dictionary of the keys 'lower', 'middle', and 'upper' to respective strata objects that have `None` assigned as their occupation. As such, now `Province` objects will only take strata objects with `None` occupation in their `idle_pops` dictionary. Any strata passed with an occupation will have its occupation automatically set to `None`. 

Changed the MethodLogger metaclass to be an instance of `type` and not `ABCMeta`. Now it returns a new `type` (class) instead of calling `ABCMeta`'s `__new__` special method.

Type annotate most of everything that needs to be type annotated.

Changed how the `get_fix_proportion` method works. Now it no longers converges to the correct answer, instead it calculate the correct
sizes for all occupations through assuming the largest one is already correct.

Changed the `get_amount_that_fixes_proportion` method name of the `Industry` class to `get_fix_proportion`.

Objects of subclasses of `Population` can now have `None` as an occupation, representing the lack of an occupation. This is necessary when considering promotions and demotions, since different strata can only have specific occupations. This will, it will be possible to later add the mechanic of unemployed pops to find employment.

The `capacity` attribute was added to the `Industry` superclass in order to correctly calculate its labor demand. Now demand will not only take into account the workers that are needed for fixing proportionality, but also workers needed to reach capacity while keeping proportionality.

The `log` decorator was missing a return value for its wrapper function, which cause it to always return `None`. In addition this also caused all the methods automatically decorated with it through the `MethodLog` metaclass to malfunction. This has since been fixed.

The `log` decorator was logging errors inside the `wrapper` function instead of the actual function where it happend. This has since been fixed. In addition, the `log` decorator no longer attempts to make a distinction between methods and functions, as it was not working.

The two separete loggers for stream logging and file logging have been unified for simplicity. Now it automatically logs everything to a file but only logs `WARNING`s and `CRITICAL`s on the console.
