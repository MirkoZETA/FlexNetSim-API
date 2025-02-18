# Flex Net Sim Backend API

Flask-based backend API for integrating the FlexNetSim C++ library, powering the web application.

## Prerequisites

*   Python 3.9 or higher
*   g++ (GNU C++ Compiler)
*   Docker (for containerization)
*   Google Cloud SDK (for deployment to Cloud Run)
*   A Google Cloud Project with Cloud Run API enabled.

## Getting Started (Local Development)

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/MirkoZETA/FlexNetSim-API.git](https://github.com/MirkoZETA/FlexNetSim-API.git)
    cd flask-simulation-backend
    ```

2.  **Create a Python virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate  # On Windows
    ```

3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the Flask backend:**
    ```bash
    flask --app backend run
    ```
    The backend will be accessible at `http://127.0.0.1:5000`.

## API Endpoints

### `/run_simulation` (POST)

This endpoint runs a FlexNetSim simulation based on the parameters provided in the JSON request body.

**Request Body Parameters:**

| Parameter         | Type             | Description                                                                    | Allowed Values                  | Default Value | Constraints           |
| :---------------- | :--------------- | :----------------------------------------------------------------------------- | :---------------------------- | :------------ | :-------------------- |
| `algorithm`       | `string`         | Routing and spectrum assignment algorithm to use.                             | `FirstFit`, `ExactFit`        | `FirstFit`    |                       |
| `networkType`     | `integer`        | Type of optical network.                                                      | `1`                             | `1`           | Only `1` (EON) available |
| `goal_connections`| `integer`        | Target number of connection requests for the simulation.                      |                                 | `100000`      | Must be integer > 0   |
| `confidence`      | `number (float)` | Confidence level for the simulation results.                                  |                                 | `0.05`        | Must be > 0           |
| `lambda_param`    | `number (float)` | Arrival rate (lambda) of connection requests.                                  |                                 | `1.0`         | Must be > 0           |
| `mu`              | `number (float)` | Service rate (mu) of connection requests.                                    |                                 | `10.0`        | Must be > 0           |
| `network`         | `string`         | Network topology to simulate.                                                 | `NSFNet`, `Cost239`, `EuroCore`, `GermanNet`, `UKNet` | `NSFNet`    |                       |
| `bitrate`         | `string`         | Type of bitrate allocation.                                                  | `fixed-rate`, `flex-rate`     | `bitrate`     |                       |
| `K`               | `integer`        | Number of paths to compute.                                                    |                                 | `3`           |                       |

**Example `curl` request with minimal parameters (defaults applied):**

```bash
curl -X POST -H "Content-Type: application/json" -d '{"algorithm": "FirstFit", "networkType": 1, "bitrate": "bitrate"}' http://127.0.0.1:5000/run_simulation
```

**Example `curl`request with all parameters specified:**
```bash
    curl -X POST -H "Content-Type: application/json" \
     -d '{
          "algorithm": "FirstFit",
          "networkType": 1, -> (Only EONs available for the moment)
          "goal_connections": 10000000,
          "confidence": 0.05,
          "lambda": 120,
          "mu": 1,
          "network": "NSFNet",
          "bitrate": "bitrate" -> (filename in the ./bitrates folder)
         }' \
     http://127.0.0.1:5000/run_simulation
 ```

 **Response**:
 - 200 OK: Simulation executed successfully. The response body will be a JSON object with the following structure: 
    ```JSON
    {
    "output": "string",  // Simulation output results
    "error": "string"   // Empty string if no errors
    }
    ```
- 400 Bad Request: Indicates an error in the request, such as missing or invalid parameters. The response body will be a JSON object with an `"error"` field describing the issue.
- 500 Internal Server Error: Indicates a server-side error, either during compilation or simulation execution. The response body will be a JSON object with `"error"` and "details" fields providing more information about the error.

### `/help` (GET)

This endpoint provides detailed information about the `/run_simulation` endpoint, including the expected request structure, parameters, allowed values, and response formats.

**Request**:
```bash
curl http://127.0.0.1:5000/help
```

## Dockerization

To build the Docker image:

```bash
docker build -t fns-api .
```
To run:
```bash
docker run -p 8080:8080 fns-api
```
To stop:
```bash
docker stop fns-api
```

## GCloud Deployment Configuration

As a prerequisite is mandatory to apply the following steps to the GCloud project for the docker image build and upload to artifacts, and also service account creation and IAM policy binding:

[GCloud Configuration Video Tutorial](https://www.youtube.com/watch?v=KQUKDiBz3IA)

This video will guide you through the necessary configurations in the Google Cloud Console to prepare your project for Cloud Run deployments using GitHub Actions.

**Key Reminders from the Video & for Successful Deployment:**

*   **Keep Track of Docker Image Name, Project ID:**  Note these down during the video configuration, as you will need them in subsequent steps and for your GitHub Actions workflow.
*   **Service Account Email:** Ensure you create a Service Account as shown in the video and securely download and store the JSON key file. You'll also need to note the Service Account's email address.

**Post-Configuration Steps (using `gcloud` and `cloud-run`):**

1.  Activate necessary apis:

    *   `gcloud services enable run.googleapis.com`

2. Create cloud run service:
    *   Navigate to the Cloud Run section in your Google Cloud Console.
    *   Create a **Service**.
    *   Select *Use an inline editor to create a function*.
    *   Set a name, in this case *fns-api-cloud-run* will be used.
    *   Note down the  Endpoint URL, because it will the defaul url for the API.
    *   Select the authetification preferences.
    *   Create.

3. Update access of service accounts to cloud run resources:

    ```bash
    gcloud projects add-iam-policy-binding "<YOUR-GOOGLE-PROJECT-ID>" --member="serviceAccount:<SERVICE_ACCOUNT_EMAIL>" --role="roles/run.admin"
    ```

    and

    ```bash
    gcloud iam service-accounts add-iam-policy-binding "<YOUR_PROJECT_NUMBER>-compute@developer.gserviceaccount.com" --member="serviceAccount:<SERVICE_ACCOUNT_EMAIL>" --role="roles/iam.serviceAccountActor"
    ``` 

4.  **Test the Deployed API (using `curl`):**

    Use the `curl` command with the `ENDPOINT-URL` you obtained from the previous steps to test your deployed API. Replace `YOUR-ENDPOINT-URL` with the actual `ENDPOINT-URL`.

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"algorithm": "FirstFit", "networkType": 1, "bitrate": "bitrate"}' <YOUR-ENDPOINT-URL>/run_simulation
    ``` 

    Remember that depending on the authetification preferences you might need to authetificate to send request to the Endpoint just created.

**Remember**: These GCloud configurations, along with the repository's `gke-cd.yml` GitHub Actions workflow and correctly configured GitHub secrets, are essential for successful automated deployment of your FlexNetSim-API application to Google Cloud Run.