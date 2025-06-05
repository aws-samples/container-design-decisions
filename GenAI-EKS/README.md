# eks-genai-hosting

> Warning:

Make sure that you have kubectl and sed installed where are you running these scripts. The k8s cluster version is 1.32 and a compatible kubectl is requried.

## Cluster Setup
- Run iac/eks-base-cluster/setup.sh via source which is Terraform based. 
```code
    cd iac/eks-base-cluster
    chmod 755 ./setup.sh
    source ./setup.sh
```

## Create Node pools for GPU
- Run iac/auto-mode-config/setup.sh
```code
    cd platform-components/auto-mode-config
    chmod 755 ./setup.sh
    source ./setup.sh
```

## Setup LangFuse
- Run platform-components/model-observability/setup.sh via source
```code
    cd platform-components/model-observability
    chmod 755 ./setup.sh
    source ./setup.sh
```

- Login to LangFuse via port-forwarding langfuse
```code
    kubectl port-forward service/langfuse-web 3000:3000 -n genai
```

Access LangFuse at localhost:3000 and create organisation named "test" and a project inside it named as "demo". Then setup tracing 
from the "Tracing" menu bar and record the PK/SK which will be used for recordnig trace.
Export keys with the variable named as LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY 

TODO: Still debating the auto creation of the keys via amending the deployment and add LANGFUSE_INIT_* params. Check out [langfuse latest instructions](https://langfuse.com/self-hosting/headless-initialization)

## Setup models
- Define and export a variable named HF_TOKEN with your Hugging Face Key
- Run platform-components/model-hosting/setup.sh
```code
    cd platform-components/model-hosting
    chmod 755 ./setup.sh
    ./setup.sh
```


## Setup Gateway
- Run platform-components/model-gateway/setup.sh
- Login to LiteLLM via portforwaring litellm
```code
    kubectl port-forward services/litellm 4000:4000 -n genai
```
- Login us "admin" and "sk-123456"
- Goto Virtual Keys on the sidebar and define a key. Mark "All Team Models" for the models field
- Store the secret key generated. Set an env variable named: "LLAMA_VISION_MODEL_KEY"

## Setup MCP Servers and agentic application
- Run defect-detection-agentic-flow/run_app.sh


## Basic Validation
- Run the following script to validate the setup
```

    kubectl port-forward services/langfuse-web 3000:3000 -n genai

    
```
- You can login to langfuse and vlidate if the traces have been captured correctly. Make sure that port-forward for the langfuse service is running.



Enjoy!


