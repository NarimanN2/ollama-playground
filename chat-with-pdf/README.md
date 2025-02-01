# Chat with PDF
A simple RAG (Retrieval-Augmented Generation) system using Deepseek, LangChain, and Streamlit to chat with PDFs and answer complex questions about your local documents.

You can watch the video on how it was built on my [YouTube](https://youtu.be/M6vZ6b75p9k).

# Pre-requisites
Install Ollama on your local machine from the [official website](https://ollama.com/). And then pull the Deepseek model:

```bash
ollama pull deepseek-r1:14b
```

Install the dependencies using pip:

```bash
pip install -r requirements.txt
```

# Run
Run the Streamlit app:

```bash
streamlit run pdf_rag.py
```

# Running and Testing the Docker Container Locally

## Build the Docker Image

Make sure you’re in the same directory as your `Dockerfile` and that the required files (such as `requirements.txt` and your Streamlit app file) are present. Then build your image with a command like:

```bash
docker build -t my-streamlit-app .
```

This command creates an image tagged `my-streamlit-app`.

### Run the Docker Container

Once the build is complete, run the container mapping the container’s port (8501) to your local machine:

```bash
docker run -p 8501:8501 my-streamlit-app
```

This command starts your Streamlit app inside the container. Open your browser and navigate to [http://localhost:8501](http://localhost:8501) to view and interact with your app.

# Running and Testing the RAG APP using Kubernetes


 **Save the YAML File**  
   Ensure your YAML content is saved in a file, for example,  i named it  `deployment.yaml`.

 **Apply the YAML Configuration**  
   Use the `kubectl apply` command to create (or update) the resources:
   
   ```bash
   kubectl apply -f deployment.yaml
   ```

   This command tells Kubernetes to read the configuration from the file and create the Deployment and Service as specified.

 **Verify the Deployment**  
   After applying the configuration, you can check the status of your resources:

   - **List Deployments:**
     ```bash
     kubectl get deployments
     ```
   
   - **List Pods:**
     ```bash
     kubectl get pods
     ```
     
   - **List Services:**
     ```bash
     kubectl get services
     ```
You can determine the node IP address by using the `kubectl` command to list your nodes along with their IP addresses. Here’s how you can do it:

 **Run the Command:**

   ```bash
   kubectl get nodes -o wide
   ```

**Check the Output:**

   The output will look something like this:

   ```
   NAME             STATUS   ROLES    AGE   VERSION   INTERNAL-IP      EXTERNAL-IP   OS-IMAGE             KERNEL-VERSION      CONTAINER-RUNTIME
   your-node-name   Ready    <none>   134d   v1.30.9   192.168.1.28     <none>        Ubuntu 23.10     6.5.0-44-generic    containerd://1.6.28
   ```

   - **INTERNAL-IP:** This is the IP address assigned to the node within your cluster’s network.
   - **EXTERNAL-IP:** If your node has an externally accessible IP (e.g., in cloud environments), it will appear here.
 **Accessing The Application**  
   Since your Service is configured as a `NodePort` on port `30001`, you can access your Streamlit app by visiting:
   
   ```
   http://192.168.1.28:30001
   ```
   
   Replace `<node-ip>` with the IP address of one of your Kubernetes nodes.

---

**Additional Tips:**

- If you make any changes to your `deployment.yaml`, you can re-run the `kubectl apply -f deployment.yaml` command to update the deployment.
- To see more detailed logs for troubleshooting, you can use:
  
  ```bash
  kubectl logs <pod-name>
  ```
  
  where `<pod-name>` is the name of one of your pods (which you can get using `kubectl get pods`).


