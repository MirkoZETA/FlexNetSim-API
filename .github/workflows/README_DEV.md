# Flex Net Sim API - Development Guide

This guide helps developers set up, test, and deploy the Flex Net Sim Backend API.

## Prerequisites

* Python 3.9+
* g++ (GNU C++ Compiler)
* Docker (for containerization)
* A Google Cloud Project with Cloud Run API enabled

## Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/MirkoZETA/FlexNetSim-API.git
   cd FlexNetSim-API
   ```

2. **Set up Python environment:**
   ```bash
   # Create virtual environment
   python3 -m venv .venv
   
   # Activate (Linux/macOS)
   source .venv/bin/activate
   
   # Activate (Windows)
   .venv\Scripts\activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   flask --app backend run
   ```
   The API will be available at `http://127.0.0.1:5000`.

4. **Test the API:**
   ```bash
   # Test help endpoint
   curl http://127.0.0.1:5000/help
   
   # Test simulation endpoint
   curl -X POST -H "Content-Type: application/json" -d '{}' http://127.0.0.1:5000/run_simulation
   ```

## Testing

Run the test suite to ensure code quality:

```bash
pytest --cov=backend tests/
```

## Docker Deployment

Build and run the Docker container locally:

```bash
# Build image
docker build -t fns-api .

# Run container
docker run -p 5000:5000 fns-api
```

## Google Cloud Deployment Configuration

The following steps are required to configure your Google Cloud project for deployment. These steps focus solely on the Google Cloud setup, not the GitHub Actions workflow configuration.

[GCloud Configuration Video Tutorial](https://www.youtube.com/watch?v=KQUKDiBz3IA)

**Note: This video demonstrates only the Google Cloud Console configurations.** The YAML workflow files shown in the video may be outdated and are not necessary for current deployments.

Follow the Google Cloud setup steps from the video, focusing on:

* Creating a project
* Setting up Docker repositories
* Creating service accounts
* Configuring permissions

**Key Information to Record During Setup:**

* **Docker Image Name and Project ID:**  Note these for your deployment process
* **Service Account Email:** Create a Service Account, download its JSON key file, and record the email address

**Post-Configuration Steps (using `gcloud` CLI):**

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
    curl -X POST -H "Content-Type: application/json" -d '{"algorithm": "FirstFit", "networkType": 1, "bitrate": "fixed-rate"}' <YOUR-ENDPOINT-URL>/run_simulation
    ``` 

    Remember that depending on the authetification preferences you might need to authetificate to send request to the Endpoint just created.

**Remember**: These GCloud configurations, along with the repository's `gke-cd.yml` GitHub Actions workflow and correctly configured GitHub secrets, are essential for successful automated deployment of your FlexNetSim-API application to Google Cloud Run.