# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

### ROADMAP
- Switch to new domain.

## [2.0.1] - 2025-03-04

### Fixed
- Fixed docker image for deployment

## [2.0.0] - 2025-03-03

### Added
- New `/run_simulation_stream` endpoint for streaming simulation results in real-time:
  - Streaming responses include event types and structured JSON data.
- Refactored backend code to reduce duplication and improve maintainability.
- Added unit tests for the streaming endpoint.
- Modified `simulator.hpp` to flush `stdout` after each line for better streaming support (see `src/README.md`).
- Improved the `\help` endpoint with more concise documentation.
- Enabled CORS only for the `/run_simulation_stream` endpoint to allow controlled API access.

### Changed
- Switched to Flex Net Sim v0.8.2.
- Standardized API response format for better consistency:
  - Success responses now use `status: "success"` with data in a `data` field.
  - Error responses now use `status: "error"` with a `message` and detailed `error` fields.
- Reorganized the test suite into separate files for better maintainability.
- Improved parameter validation with descriptive error messages.
- Changed the error response code from `500` to `400` for invalid parameters.
- Moved parameter validation from C++ to the API layer for a better user experience.
- Replaced the `ExactFit` algorithm with `BestFit`.
- Enhanced algorithms

### Fixed
- Fixed error in main.cpp always using FirstFit
- Fixed error in main.cpp always using Fixed-Rate

## [1.1.1] - 2025-03-01

### Added
- Deployed coverage to pages

### Fixed
- Fixed pipeline for GitHub pages
- Fixed badges

## [1.1.0] - 2025-03-01

### Added
- Comprehensive unit tests for all API endpoints and functions
- Test coverage reporting with pytest-cov
- Coverage badges in README.md
- New GitHub Actions workflow for test coverage

### Changed
- Improved documentation in README.md with clearer structure and badges
- Enhanced API documentation in backend.py with better comments and docstrings
- Updated development guide with clearer instructions
- Refactored GitHub Actions workflows to separate testing and deployment
- Improved code comments and function documentation

### Fixed
- Modified .gitignore to handle coverage files

## [1.0.0] - 2025-02-19

### Added

- This API hopefully serves as playground to all new users of Flex Net Sim C++ simulation library.
- The current version utilizes Flex Net Sim v0.8.1.
- `/run_simulation` endpoint for simulation includes parameters such as:
    - `algorithm`: FirstFit, BestFit.
    - `networkType`: Only 1 (EON) available for now.
    - `goalConnections`: 1 to 10,000,000.
    - `confidence`: significance level (alpha) greater than zero.
    - `lambdaParam`: Arrival rate (lambda) of connection requests.
    - `mu`: departure rate of connection requests.
    - `network`: name of the netowrk to simulate, `Cost239`, `EuroCore`, `GermanNet`, `UKNet`, `NSFNet`.
    - `bitrate`: fixed-rate or flex-rate.
    - `K`: Number of paths to consider during allocation, max 6.
- `/help` endpoint provides detailed information about the `/run_simulation` endpoint.
- API allocated in cloud run.
- Documentation README for the process of develop/deployment located in [workflows](https://github.com/MirkoZETA/FlexNetSim-API/tree/master/.github/workflows/README_DEV.md).

[1.0.0]: https://github.com/MirkoZETA/FlexNetSim-API/releases/tag/v1.0.0
[1.1.0]: https://github.com/MirkoZETA/FlexNetSim-API/releases/tag/v1.1.0
[1.1.1]: https://github.com/MirkoZETA/FlexNetSim-API/releases/tag/pipeline-fix
[2.0.0]: https://github.com/MirkoZETA/FlexNetSim-API/releases/tag/v2.0.0
[2.0.1]: https://github.com/MirkoZETA/FlexNetSim-API/releases/tag/v2.0.1