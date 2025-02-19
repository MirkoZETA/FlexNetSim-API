# Flex Net Sim Backend API

Welcome to the Flex Net Sim Backend API repository.

This is the **publicly accessible backend API** for the [Flex Net Sim](https://gitlab.com/DaniloBorquez/flex-net-sim) project.

This API provides a **hands-on demonstration**, enabling users to quickly execute pre-configured network simulations and gain an initial understanding of Flex Net Sim's capabilities.

Through simple POST requests, initiated via command-line tools or the [playground page](www.in-progress.com), users can experiment with a defined set of parameters and algorithms. This allows for exploration of fundamental network simulation concepts using Flex Net Sim.

It is important to note that **this API is intentionally designed as a limited demonstration platform**.  It serves as a **simplified method of accessing** and showcasing the **basic functionalities** of Flex Net Sim.  **It is not intended for complex simulations or for algorithm customization.**  Algorithm customization is a core strength of Flex Net Sim, and this advanced capability is exclusively unlocked when working directly with **the library**.

The purpose of this API is to introduce users to Flex Net Sim and encourage exploration of **the full library** for advanced simulation tasks.  **The full library** offers significantly greater power, flexibility, and customization potential.

For users interested in progressing beyond this introductory API, comprehensive resources and documentation are available at the official [Flex Net Sim documentation](https://flex-net-sim-fork.readthedocs.io/stable/).

For **Development and Deployment Instructions** of this API (the playground itself), please refer to [README_DEV.md](README_DEV.md).

## API Endpoints

### `/run_simulation` (POST)

This endpoint runs a Flex Net Sim simulation based on the parameters provided in the JSON request body.

**Request Body Parameters:**

| Parameter         | Type             | Description                                            | Allowed Values                  | Default Value | Constraints           |
| :---------------- | :-------------- | :-----------------------------------------------------  | :---------------------------- | :------------ | :-------------------- |
| `algorithm`       | `string`        | Routing and spectrum assignment algorithm to use.       | `FirstFit`, `ExactFit`        | `FirstFit`    |                       |
| `networkType`    | `integer`        | Type of optical network.                                | `1`                           | `1`           | Only `1` (EON) available |
| `goalConnections`| `integer`        | Target number of connection requests for the simulation.|                               | `100000`      | Must be integer > 0   |
| `confidence`      | `number (float)`| Confidence level for the simulation results.            |                               | `0.05`        | Must be > 0           |
| `lambdaParam`    | `number (float)` | Arrival rate (lambda) of connection requests.           |                               | `1.0`         | Must be > 0           |
| `mu`              | `number (float)`| Service rate (mu) of connection requests.              |                               | `10.0`        | Must be > 0           |
| `network`         | `string`        | Network topology to simulate.                          | `NSFNet`, `Cost239`, `EuroCore`, `GermanNet`, `UKNet` | `NSFNet`    |                       |
| `bitrate`         | `string`        | Type of bitrate allocation.                            | `fixed-rate`, `flex-rate`     | `bitrate`     |                       |
| `K`               | `integer`       | Number of paths to consider.                           |                               | `3`           |                       |

**Example `curl` request with no parameters (defaults applied):**

```bash
curl -X POST -H "Content-Type: application/json" -d '{}' https://fns-api-cloud-run-787143541358.us-central1.run.app/run_simulation
```

**Example `curl`request with all parameters specified:**

```bash
curl -X POST -H "Content-Type: application/json" \
-d '{ "algorithm": "FirstFit",
      "networkType": 1,
      "goalConnections": 1000000,
      "confidence": 0.05,
      "lambdaParam": 120,
      "mu": 1,
      "network": "NSFNet",
      "bitrate": "fixed-rate"
    }' \
  https://fns-api-cloud-run-787143541358.us-central1.run.app/run_simulation
``` 

 **Response**:
  - `200` OK: Simulation executed successfully. The response body will be a JSON object with the following structure: 
    ```JSON
    {
    "output": "string",
    "error": "string"
    }
    ```
  - `400` Bad Request: Indicates an error in the request, such as missing or invalid parameters. The response body will be a JSON object with an `error` field describing the issue.
  - `500` Internal Server Error: Indicates a server-side error, either during compilation or simulation execution. The response body will be a JSON object with `error` and "details" fields providing more information about the error.

### `/help` (GET)

This endpoint provides detailed information about the `/run_simulation` endpoint, including the expected request structure, parameters, and response formats.

**Request**:
```bash
curl https://fns-api-cloud-run-787143541358.us-central1.run.app/help
```