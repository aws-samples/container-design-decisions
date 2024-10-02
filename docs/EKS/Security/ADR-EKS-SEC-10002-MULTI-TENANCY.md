
# Designing a Strategy to Deploy Kubernetes Cluster for Multi-Tenancy

Deploying a Kubernetes (k8s) cluster for multi-tenancy involves choosing an appropriate strategy to manage multiple tenants efficiently while ensuring operational excellence, security, performance, cost management, and reliability.

## Decision Drivers

* **Operational Excellence**: The ease of managing and maintaining the clusters.
* **Security**: Ensuring strong isolation and security between tenants.
* **Performance**: Maintaining high performance and resource efficiency.
* **Cost Management**: Minimizing costs associated with infrastructure and operations.
* **Reliability**: Ensuring high availability and resilience of the clusters.

## Considered Options

* Namespace per tenant
* Virtual Cluster per tenant
* Cluster per tenant


## Pros and Cons of the Options

### Namespace per Tenant

**Description**: Each tenant is assigned a separate namespace within a single Kubernetes cluster.

**Pros:**

* **Cost-Efficient:** Sharing a single cluster reduces infrastructure costs. You can mix different application profiles. For example, combine applications with spiky workloads with those that have steady resource demands. This allows resources to be used effectively when the spiky workloads are idle.
* **Simpler Management:** Easier to manage and monitor compared to maintaining multiple clusters,as all tenants share the same control plane.
* **Resource Quotas and Limits:** Kubernetes allows setting resource quotas and limits at the namespace level, ensuring fair resource distribution.

**Cons:**

* **Security Risks:** Potential for insufficient isolation, which can lead to security risks if not properly managed.
* **Performance Contention:** Resource contention can occur if resource limits and quotas are not correctly configured.
* **Reliability** Large blast radius for outages, planned or unplanned
* **Operational Excellence** Some cluster-level resources and controllers may not be a good fit.


**Considerations:**

* Security risks can be managed through Kubernetes RBAC and network policies, but strong isolation requires careful configuration.
* Requires careful configuration of network policies to isolate network traffic between namespaces.
* Consider 3rd party tools for cost charge back/show back 


### Virtual Cluster per Tenant

**Description**: Each tenant gets a virtual cluster. Virtual clusters are a Kubernetes concept that enables isolated clusters to be run within a single physical Kubernetes cluster. Each cluster has its own API server, often achieved using solutions like Kiosk or vCluster.

**Pros:**

* **Better Isolation for development:**  Compared to namespaces, virtual clusters offer superior isolation from a control plane perspective, as each virtual cluster operates with its own dedicated control plane. Virtual clusters can be spun up and down as needed, providing a fresh environment for development. 
* **Granular Resource Control:** Virtual clusters can help in optimizing resource utilization by allowing dynamic allocation of resources based on demand. 
* **Improved Security:** Virtual clusters provide an additional layer of security by isolating workloads at the control plane level. It is possible to implement more granular access control policies. Each virtual cluster can have its own set of RBAC (Role-Based Access Control) rules, ensuring that only authorized users have access to specific resources and operations within their cluster​ 
* **Operational Excellence** quicky provision Dev/UAT/PreProd environments with virtual clusters. Tenants can be admins inside their virtual cluster without being admin in the underlying cluster.

**Cons:**

* **Operational Overhead:** More complex to set up and manage than namespace isolation.
* **Performance Overhead:** Potential performance overhead due to the additional layer of virtualization. 

**Considerations:**

* It still shares the same control plane, so control plane resource contention is possible.


### Cluster per Tenant

**Description**: The most secure way to run Silo workloads on EKS is to create a distinct EKS cluster for each tenant. In such a design, even a tenant that runs privileged containers and has access to the hosts cannot impact other tenants.

**Pros:**

* **Complete Isolation:** it provides the highest level of isolation, both in terms of security and resources, eliminating noisy neighbor issues. Easy to segregate responsibilities between teams.
* **Flexibility:** Easier to scale and customize for specific tenant requirements without affecting others.
* **Operational Excellence** Better lifecycle management - easier changes, less complexity, fewer dependencies due to reduced surface area.
* **Operational Excellence** Simple human access model
* **Operational Excellence** Simple chargeback/showback model


**Cons:**

* **High Costs:**  Higher costs due to the need for separate infrastructure for each tenant. Separate clusters cannot efficiently merge different application profiles, which limits their ability to maximize resource utilization.
* **OPerational Overhead:** Potential large number of clusters, leading to inefficiencies and higher operational costs.

**Considerations:**

*  It can offer superior performance, but managing multiple clusters requires significant operational effort,requiring robust automation and monitoring tools
*  Consider  gitops to automate provsioning/management of multi-clusters


## Resources

1. [Multi-tenancy - EKS Best Practices Guides](https://aws.github.io/aws-eks-best-practices/security/docs/multitenancy/)
2. [Multi-tenant Design Considerations for Amazon EKS Clusters](https://aws.amazon.com/blogs/containers/multi-tenant-design-considerations-for-amazon-eks-clusters/)
3. [Three Tenancy Models For Kubernetes](https://kubernetes.io/blog/2021/04/15/three-tenancy-models-for-kubernetes/)
4. [Introducing Hierarchical Namespaces](https://kubernetes.io/blog/2020/08/14/introducing-hierarchical-namespaces/)
5. [Set up soft multi-tenancy with Kiosk on Amazon Elastic Kubernetes Service](https://aws.amazon.com/blogs/containers/set-up-soft-multi-tenancy-with-kiosk-on-amazon-elastic-kubernetes-service/)
6. [Configure your cluster for Kubernetes network policies - Amazon EKS](https://docs.aws.amazon.com/eks/latest/userguide/cni-network-policy.html)
7. [Deliver Namespace as a Service multi tenancy for Amazon EKS using Karpenter](https://aws.amazon.com/blogs/containers/deliver-namespace-as-a-service-multi-tenancy-for-amazon-eks-using-karpenter/)
8. [How to track costs in multi-tenant Amazon EKS clusters using Kubecost](https://aws.amazon.com/blogs/containers/how-to-track-costs-in-multi-tenant-amazon-eks-clusters-using-kubecost/)
9. [Security Practices for MultiTenant SaaS Applications using Amazon EKS](https://d1.awsstatic.com/whitepapers/security-practices-for-multi-tenant-saas-apps-using-eks.pdf)


## Discovery Questions 
Use the discovery questions provided here to help you evaluate your requirements, priorities, and constraints, ensuring you make a future-proof architectural decision.

### General

* How many tenants do you anticipate managing within your Kubernetes environment?
* What future changes or expansions do you anticipate that might impact your Kubernetes strategy.
* Which of the business drivers (Operational Excellence, Security, Performance, Cost Management, Reliability) is your top priority, and why?
* Are there any specific technical constraints or legacy systems that need to be integrated with the new Kubernetes setup?
* What is your timeline for deploying a multi-tenant Kubernetes environment?
* What is the current skill level of your team in managing Kubernetes and related technologies?
* Do you have any plans for training or engaging 3rd party to fill skill gaps?

### Operational Excellence

* How do you currently manage and maintain your Kubernetes clusters? What challenges are you facing?
* What level of automation and monitoring do you have in place for your Kubernetes infrastructure?

### Security
* What are your specific security requirements for isolating tenants in a multi-tenant environment? How critical is strong isolation between tenants to your business?
* What is your approach to configuring Kubernetes RBAC and network policies to ensure tenant security?

### Performance
* How do you plan to handle potential resource contention between tenants?

### Cost Management
* How do you track and allocate costs to different tenants or projects?

### Reliability

* What are your uptime and availability requirements for your Kubernetes clusters?
* How do you plan to ensure resilience and high availability for your tenants?
