# Flex Net Sim Backend API

[![Static Badge](https://img.shields.io/badge/version-1.1.0-blue)](https://github.com/MirkoZETA/FlexNetSim-API)
![Static Badge](https://img.shields.io/badge/language-python-blue)
[![Static Badge](https://img.shields.io/badge/licese-MIT-green)](https://github.com/MirkoZETA/FlexNetSim-API/blob/master/LICENSE)
[![Test Coverage](https://github.com/MirkoZETA/FlexNetSim-API/actions/workflows/test-coverage.yml/badge.svg)](https://github.com/MirkoZETA/FlexNetSim-API/actions/workflows/test-coverage.yml)
[![Cloud Run Deployment](https://github.com/MirkoZETA/FlexNetSim-API/actions/workflows/gke-cd.yml/badge.svg)](https://github.com/MirkoZETA/FlexNetSim-API/actions/workflows/gke-cd.yml)

A lightweight API for running optical network simulations with [Flex Net Sim C++](https://gitlab.com/DaniloBorquez/flex-net-sim).

## Overview

The Flex Net Sim Backend API provides:

- **Hands-on demonstration** of optical network simulation capabilities
- **Simplified access** to core Flex Net Sim features
- **Quick experimentation** with pre-configured network topologies and parameters

This API serves as an introduction to the full Flex Net Sim library, allowing users to explore basic network simulation concepts through simple HTTP requests.

## Important Limitations

This API is intentionally designed as a limited demonstration platform:

- **Not intended** for complex simulations or algorithm customization
- Provides access to **basic functionalities** only
- For advanced simulation tasks, users should explore **the full library**

For comprehensive resources, see the [Flex Net Sim documentation](https://flex-net-sim-fork.readthedocs.io/stable/).

For development and deployment instructions for this API, refer to [README_DEV.md](.github/workflows/README_DEV.md).

## API Endpoints

### `/run_simulation` (POST)

Runs a network simulation with the provided parameters.

#### Request Parameters

| Parameter       | Type      | Description                | Allowed Values & Constraints                                   | Default   |
|---------------|---------|----------------------------|-------------------------------------------------|-----------|
| `algorithm`    | `string`  | RSA algorithm              | `FirstFit`, `ExactFit`                         | `FirstFit` |
| `networkType`  | `integer` | Network type               | Only `1` (EON) supported                        | `1`       |
| `goalConnections` | `integer` | Target connection requests | Must be > 0 and < 10,000,000                   | `100000`  |
| `confidence`   | `float`   | Confidence level           | Must be > 0 and < 1.0                           | `0.05`    |
| `lambdaParam`  | `float`   | Arrival rate               | Must be > 0                                     | `1.0`     |
| `mu`          | `float`   | Service rate               | Must be > 0                                     | `10.0`    |
| `network`      | `string`  | Network topology           | `NSFNet`, `Cost239`, `EuroCore`, `GermanNet`, `UKNet` | `NSFNet` |
| `bitrate`      | `string`  | Bitrate type               | `fixed-rate`, `flex-rate`                      | `fixed-rate` |
| `K`           | `integer` | Path count                 | Must be > 0 and ≤ 6                             | `3`       |

#### Example: Default Parameters

```bash
curl -X POST -H "Content-Type: application/json" -d '{}' \
  https://fns-api-cloud-run-787143541358.us-central1.run.app/run_simulation
```

#### Example: Custom Parameters

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{ 
  "algorithm": "FirstFit",
  "networkType": 1,
  "goalConnections": 100000,
  "confidence": 0.05,
  "lambdaParam": 120,
  "mu": 1,
  "network": "NSFNet",
  "bitrate": "fixed-rate"
}' \
https://fns-api-cloud-run-787143541358.us-central1.run.app/run_simulation
```

#### Response Codes

- `200 OK`: Success. Returns `{"output": "...", "error": ""}`
- `400 Bad Request`: Invalid parameters
- `500 Internal Server Error`: Server-side error

### `/help` (GET)

Returns detailed API documentation.

```bash
curl https://fns-api-cloud-run-787143541358.us-central1.run.app/help
```