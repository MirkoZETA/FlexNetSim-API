## Modification Notice: simulation.hpp

This document describes a modification made to the `simulation.hpp` file, specifically in the `Simulator::printRow` function. The purpose of this change is to enable real-time streaming of simulation output when used with the API, ensuring that data is delivered to the client as soon as it is available.

The original implementation of printRow did not explicitly flush the standard output buffer (`std::cout`). This caused output buffering issues when streaming responses via an API, leading to a delay in data transmission. Since `std::cout` is typically buffered, data was held in memory and only sent in large chunks rather than being streamed line by line in real time.

### Code Change

**From:**

```cpp
void Simulator::printRow(double percentage) {
  
  ...

  std::cout << std::setw(1) << "\n";
}
```
**To:**

```cpp
void Simulator::printRow(double percentage) {

  ...

  std::cout << std::setw(1) << "\n" << std::flush;
}
```

### Future Considerations

If future versions of the library include this feature, this modification may no longer be necessary. Until then, it should be retained to ensure proper streaming behavior.