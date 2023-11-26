## `source.goods` module

## `source.pop` module

### `Strata` Enum

### `Jobs` Enum

### `Pop` dataclass

### `PopFactory` class

### `Community` dict-subclass
This is a container for `Pop` object. It is intended to make operations between several `Pop` easier.

- #### Accessing

`Pop` objects within the `Community` can be accessed several ways:

```
Community[Jobs] -> Pop
Community[Strata] -> Community
Community[Strata, Jobs.NONE] -> Pop
```

The first accesses the Pop with the specified job. The second filters the Community and returns another Community with only pops of the specified stratum. The third accesses unemployed pops of the specified stratum.

- #### Adding pops

`Pop` objects can be added to the community via:

```
Community[Jobs] += Pop  # Assuming it has the correct job
Community += Pop
Community += Community
```

The first accesses the `Pop` object of the specified job and sums the wanted pop to it through the operation defined in the `Pop` class. The second checks for the `Pop`'s job and automatically adds it. The third iterates through the `Pop`s in the second community and adds them to the first.

## `source.prod` module