### Sharing of `Stockpile` objects through City/Province objects and their composite objects.

Each high level city/province should have a `Stockpile` object and this object should be shared down with all the objects that are composite to it. For example, if there is a city _Trost_ that has a `Pop` object representing idle workers and this city has two `Extractor` objects and each object has one `Pop` object - then all of these objects should share the same stockpile. It should be store in the city and all object composite of it should have a "pointer" to it.

### Simulation process.
1. First the `Extractor` object produces its goods
2. Then the `Workforce` object consumes the goods in the stockpile

If they produce more goods than they consume, they will grow. If not, they will shrink.

The data is gathered before production and before consumption and is plotted into graphs after taking the rolling average of these states.
