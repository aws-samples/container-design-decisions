# Store and make sensitive data avaiable for your application on the EKS cluster


## Context

Containers provided a way to standardize application packages that can be deployed across different environments and hardware. However, sensitive data such as passwords to access external resources (such as database) by the application container is not recommended to be stored in the container to reduce attack surface. And different environments probably have different values for the sensitive data (such as passwords for test environment is different than production).

Kubernetes provides Secrets to hold such data and inject into application containers, however these resources are Base64 encoded  and not encrypted. Kubernetes provides ways to secure the secrets such as:

* Kubernetes distributes secrets to nodes running Pods that need it and not all nodes.

* When secrets is available on nodes, they are stored in memory in a tmpfs and never written to physical storage, and Kubernetes remove them when the Pod is no longer available on the node

* Etcd could be encrypted where it stores the Secrets information. Envelope encryption provides a way to encrypt Kubernetes secrets using CMK.

This document captures different ways on how application containers can consume sensitive data such as database password, private keys, and api keys.

## Considered Options

**Option 1:**  Use Kubernetes CSI driver to load data from Secret Store 

**Option 2:**  Encrypt and Store secrets in Git and load and decrypt them via Kubernetes controller such as SealedSecrets 

**Option 3:**  Application to load sensitive data from external store directly 

**Option 4:** Use vendor/OSS provided tool like sidecar to load sensitive information such as HAshiCorp and/or External Secrets Operator

**Option 5:** Use Kubernetes native Secrets 


Let's look into details of these options.

### Option 1: Use Kubernetes CSI driver to load data from Secret Store 

Store sensitive data in an external store such as AWS Secrets Manager. So your sensitive data is outside your Kubernetes cluster.  

Then use the relevant Kubernetes CSI driver to read the sensitive data from the external store and load/mount onto the application container at runtime as a file. The Kubernetes CSI driver option provides flexibility to access different third-party Secrets store and not just as AWS Secrets Manager.

#### Pros

* Avoid storing sensitive data into Kubernetes objects such as secrets. CSI driver mount the sensitive data as files.

* No change in application is required to to read sensitive data from a central store. Application load data from local files.

* Existing GitOps principle could be utilized to approve and audit the use of sensitive data through the use of SecretProviderClass CRD object.  

* easy to migrate to a different backend that also provides industry standard CSI interface


#### Cons
* Storing sensitive data outside of the cluster will add additional dependency which may hurt the availability of the application if Secret store is not operational.

* Additional complexity of running a CSI provider in the Kubernetes cluster

### Option 2: Encrypt and Store secrets in Git and load and decrypt them via Kubernetes controller such as SealedSecrets 

Store sensitive data as encrypted objects in the cluster and a Kubernetes controller decrypts and create Secret objects. The encrypted objects such as SealedSecrets has the encrypted data, and a controller creates the Kubernetes Secrets with the un-encrypted data.

Teams adopting GitOps can create the encrypted SealedSecrets objects and store them in Git. The controller will decrypt and load them as Kubernetes Secrets. The deployment will refer then secrets to be available at runtime for the applications. 

For SealedSecrets, although the controler decrypts the information, the encryption is done outside of cluster using the tooling provided by SealedSecrets project. 

#### Pro

* The team utilities the existing (if any) GitOps principles

* No change in application is required to to read sensitive data from Git Repo.

#### Cons

* Other users of namespace can escalate to access the Secrets that is mounted by the controller. 

* Secrets are not the most secure option. As the information will still be available in the cluster as Secrets which will increase the attack surface area

* Additional complexity of running a Secrets provider in the cluster


#### Option 3: Application to load sensitive data from external store directly 
 
Change application to load and decode encrypted information within the application itself from the exernal store.

Using this approach the application will use the sensitive data provider API to interact and load the data onto application memory.

#### Pros

* Direct coupling may help to use more features provided by the external store vendor

* More secure approach as sensitive data resides in memory of the application container

#### Cons

* This option will result in changes in multiple applications which result in more maintenance and difficult to change providers.

* High cost if you want to move to another vendor

* Couples the application logic with configuration security. 

* generally anti pattern https://12factor.net/config


### Option 4: Use vendor/OSS provided tool to load sensitive information such as HashiCorp Vault sidecar or External Secrets Operator

Some external sensitive data stores such as Hashicorp Vault, provide an sidecar container that can be associated with your application. The container works as a bridge for what data is needed by the application container and how to get it from the external store. This is implemented as a  mutating webhook, that allows modification of any resource when it is created through intercepting Kubernetes API calls. When a Pod specification contains a vault-specific annotation, the  controller will add a container for syncing with Vault and to mount a volume for the secret data onto the application container.

You can use other provider such as External Secrets Operator which integrates with an dedicated secret store such as AWS Secrets Manager which can perform the encryption.


#### Pros
* No change in application is required to to read sensitive data from a central store.
* Direct coupling may help to use more features provided by the external store vendor

#### Cons
* Tight coupling between the vendor provided container may result in lock-in
* High cost if you want to move to another vendor




## Best practices for managing Sensitive Data

* Enable Audit for Kubernetes and Secret Store (if using). 
* Prefer sensitive data mounted on volumes over Environment variables or Secrets.
* De-couple the sensitive data provider from the application. Use Kubernetes or vendor components such as sidecar to load and make sensitive data available to application

Please refer to [EKS Best practices](https://aws.github.io/aws-eks-best-practices/security/docs/data/).



## What option is the right fit for my usecase?
This section aims to provide multiple perspectives of this decision and how you assess the right fit for your use case. 

#### What’s the impact if the sensitive data is compromised?  
This document does not deal with if the sensitive data store in compromised. However, if one or a list od secrets are compromised, immediately rotate them. It is therefore important to select a sensitive data provider that supports rotation and have a routine rotation policy implemented. 

#### Do you use an existing sensitive data provider as part of your enterprise?
If you want to continue with your Enterprise standards, Kubernetes CSI Driver and External Secrets Operator may provided integration with your existing sensitive data provider. 


#### What are the security and compliance requirements for storing and accessing the sensitive data (e.g., encryption at rest, access control, auditing, monitor, rotation)?
Managing sensitive data lifecycle is a specialized task. Adopting dedicated stores such as AWS Secrets Manager would result in reducing the complexity of your architecture. These stores provides observability, access control and lifecycle of your sensitive data. 
Use Kubernetes components with audit trails to load and make these data available to your applications Kubernetes CSI driver and external secrets operator options provide integration with state of the art external sensitive data stores and could be considered

#### Do you want to decouple the configuration security concerns from the application logic? 
It is recommended to avoid making your application aware of sensitive data location. Application shall load the sensitive data using standard approaches such as files mounted on the container volume. All options other than the “change application to load data directly from sensitive data store” provide this option and could be a good fit.

#### Do you want to use open solution for better flexibility and not relying on 3rd party support?
Kubernetes CSI driver, External Secrets Operator provide use standard Kubernetes constructs such as controllers and support for a variety of external sensitive data stores with source code available openly. SealedSecrets also falls into this category with the sensitive data stored in Git.

#### How important is the availability of the sensitive data provider to your application's functionality? Can your application gracefully handle temporary unavailability of the sensitive data provider?
Since loading data onto the applications via external sensitive data store requires access to the secrets store. It’s availability may reduce your application resilience because your application may fail to start new instances if the store is not available. In this case loading secrets onto your Kubernetes cluster would makes more sense. Do note that cloud based sensitive data provider such as KMS has a very high SLA.



## Other things to consider
The section provide additional considerations that may be useful for adopting a particular solution. Howver, this ADR will not provide any recommendations for these considetaions.

* Do you have an enterprise standard in your org to manage Secret? How will it add to complexity if you are not consistent with your enpterprise standard and what features your existing solution may not provide?

* Is your secret management solution subject to any internal or external regulatory requirements standards?

* Do you have an centralised team to manage sensitive data? How your decision will effect the process of sensitive data management? 





