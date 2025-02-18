# Flex Net Sim Backend API

Flask-based backend API for integrating the FlexNetSim C++ library, powering the web application deployed at [www.in-progress.com](www.in-progress.com). While unofficial, it serves as a bridge between the simulation engine and the web interface.

## Prerequisites

*   Python 3.9 or higher
*   g++ (GNU C++ Compiler)
*   Docker (for containerization)
*   Google Cloud SDK (for deployment to GKE) -> In progress.
*   A Google Cloud Project with Google Kubernetes Engine (GKE) and Google Container Registry (GCR) enabled -> In progress.

## Getting Started (Local Development)

1.  **Clone the repository:**
    ```bash
    git clone [repository-url]
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

5.  **Send simulation requests using `curl` or a frontend application:**
    Example `curl` request with minimal parameters (defaults applied):
    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"algorithm": "FirstFit", "networkType": 1, "bitrate": "bitrate"}' [http://127.0.0.1:5000/run_simulation](http://127.0.0.1:5000/run_simulation)
    ```

    Example `curl` request with all parameters specified
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

## Docs: GCloud Deployment Configuration

For detailed step-by-step instructions on configuring Google Cloud (GCloud) aspects such as Kubernetes Cluster creation, Artifact Registry, Service Account creation, and IAM policy binding, please refer to the following video tutorial:

[GCloud Configuration Video Tutorial](https://www.youtube.com/watch?v=KQUKDiBz3IA)

This video will guide you through the necessary configurations in the Google Cloud Console to prepare your project for Kubernetes deployments using GitHub Actions.

**Key Reminders from the Video & for Successful Deployment:**

*   **Keep Track of Docker Image Name, Project ID:**  Note these down during the video configuration, as you will need them in subsequent steps and for your GitHub Actions workflow.
*   **Service Account Email:** Ensure you create a Service Account as shown in the video and securely download and store the JSON key file. You'll also need to note the Service Account's email address.

**Post-Configuration Steps (using `gcloud` and `cloud-run`):**

1.  Activate necesary apis:

    *   `gcloud services enable run.googleapis.com`

2. Create cloud run service:
    *   Navigate to the Cloud Run section in your Google Cloud Console.
    *   Create a **Service**.
    *   Select *Use an inline editor to create a function*.
    *   Set a name, in this case *fns-api-cloud-run* will be used.
    *   Note down the  Endpoint URL, because it will the defaul url for the API.
    *   Select the authetification preferences.
    *   Create.


    *   Choose a cluster name (e.g., `flex-net-sim-cluster`). **Remember this name.**
    *   Select a region for your cluster (e.g., `us-central1`).
    *   For the purpose of this guide, you can use the default settings for node pools, networking, and other configurations, or adjust them based on your specific needs.
    *   Click **Create** to create the cluster. It will take a few minutes for the cluster to be provisioned.

2.  **Set IAM Policy Binding (using `gcloud`):**

    Replace `<YOUR-GOOGLE-PROJECT-ID>` and `<SERVICE_ACCOUNT_EMAIL>` with your actual Google Cloud Project ID and the Service Account Email you noted down.

    ```bash
    gcloud projects add-iam-policy-binding <YOUR-GOOGLE-PROJECT-ID> --member="serviceAccount:<SERVICE_ACCOUNT_EMAIL>" --role="roles/container.admin"
    ```

3.  **Get Kubernetes Cluster Credentials (using `gcloud`):**

    Replace `<CLUSTER-NAME>` and `<YOUR-GOOGLE-PROJECT-ID>` with your Kubernetes Cluster Name and Google Cloud Project ID. Ensure the region is set to `us-central1`.

    ```bash
    gcloud container clusters get-credentials <CLUSTER-NAME> --region us-central1 --project <YOUR-GOOGLE-PROJECT-ID>
    ```

    The command will fetch the cluster credentials and configure `kubectl` to use them. You should see output similar to:

    ```
    Fetching cluster endpoint and auth data.
    kubeconfig entry generated for <CLUSTER-NAME>.
    ```

4.  **Verify `kubectl` Configuration and Service Deployment (using `kubectl`):**

    After the command is successful, verify your `kubectl` configuration and check for the `fns-api-service`:

    ```bash
    kubectl get service fns-api-service
    ```

    If the service is correctly deployed (after your GitHub Actions workflow runs), it should display information about your service, including the `EXTERNAL-IP`.

    You should see output similar to this (the `EXTERNAL-IP` will likely be different):

    ```
    NAME              TYPE           CLUSTER-IP      EXTERNAL-IP     PORT(S)        AGE
    fns-api-service   LoadBalancer   10.3.xxx.xxx    34.56.1.247     80:8080/TCP    20h
    kubernetes        ClusterIP      10.3.xxx.xxx     <none>          443/TCP        21h
    ```

5.  **Test the Deployed API (using `curl`):**

    Use the `curl` command with the `EXTERNAL-IP` you obtained from the previous step to test your deployed API. Replace `<YOUR-EXTERNAL-IP>` with the actual `EXTERNAL-IP`.

    ```bash
    curl -X POST -H "Content-Type: application/json" -d '{"algorithm": "FirstFit", "networkType": 1, "bitrate": "bitrate"}' http://<YOUR-EXTERNAL-IP>/run_simulation
    ```

**Remember**: These GCloud configurations, along with the repository's `gke-cd.yml` GitHub Actions workflow and correctly configured GitHub secrets, are essential for successful automated deployment of your FlexNetSim-API application to Google Cloud Kubernetes Engine.


