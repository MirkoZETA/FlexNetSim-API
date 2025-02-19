# Flex Net Sim Backend API - Development and Deployment Instructions

This document is for developers who want to set up, develop, and deploy the Flex Net Sim Backend API.

## Prerequisites

*   Python 3.9 or higher
*   g++ (GNU C++ Compiler)
*   Docker (for containerization)
*   Google Cloud SDK (for deployment to Google Cloud Run)
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
    ```

    On Linux/macOS:
    ```bash
    source .venv/bin/activate
    ```

    On Windows
    ```bash
    .venv\Scripts\activate  
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

5. **Test**:
    ```bash
    curl http://127.0.0.1:5000/help
    ```
    or
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{}' http://127.0.0.1:5000/run_simulation
    ```

### Dockerization

To build the Docker image:

```bash
docker build -t fns-api .
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
    curl -X POST -H "Content-Type: application/json" -d '{"algorithm": "FirstFit", "networkType": 1, "bitrate": "fixed-rate"}' <YOUR-ENDPOINT-URL>/run_simulation
    ``` 

    Remember that depending on the authetification preferences you might need to authetificate to send request to the Endpoint just created.

**Remember**: These GCloud configurations, along with the repository's `gke-cd.yml` GitHub Actions workflow and correctly configured GitHub secrets, are essential for successful automated deployment of your FlexNetSim-API application to Google Cloud Run.