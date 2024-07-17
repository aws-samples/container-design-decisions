---
layout: page
title: Designing a Strategy to Deploy Kubernetes Cluster for Multi-Tenancy
permalink: /security01
---

---
# These are optional elements. Feel free to remove any of them.
status: {proposed | rejected | accepted | deprecated | … | superseded by [ADR-0005](0005-example.md)}
date: {YYYY-MM-DD when the decision was last updated}
deciders: {list everyone involved in the decision}
consulted: {list everyone whose opinions are sought (typically subject-matter experts); and with whom there is a two-way communication}
informed: {list everyone who is kept up-to-date on progress; and with whom there is a one-way communication}
---
## Designing a Strategy to Deploy Kubernetes Cluster for Multi-Tenancy

Deploying a Kubernetes (k8s) cluster for multi-tenancy involves choosing an appropriate strategy to manage multiple tenants efficiently while ensuring operational excellence, security, performance, cost management, and reliability.

## Decision Drivers

* **Operational Excellence**: The ease of managing and maintaining the clusters.
* **Security**: Ensuring strong isolation and security between tenants.
* **Performance**: Maintaining high performance and resource efficiency.
* **Cost Management**: Minimizing costs associated with infrastructure and operations.
* **Reliability**: Ensuring high availability and resilience of the clusters.

## Considered Options

* Namespace per tenant
* Nodes per tenant
* Cluster per tenant

## Pros and Cons of the Options

### Namespace per Tenant

**Description**: Each tenant is assigned a separate namespace within a single Kubernetes cluster.

* **Good, because** this approach simplifies cluster management, as all tenants share the same control plane【1】【2】.
* **Good, because** it is cost-effective since it leverages a single cluster【3】【4】.
* **Neutral, because** security can be managed through Kubernetes RBAC and network policies, but strong isolation requires careful configuration【5】.
* **Bad, because** resource contention can occur if tenants are not properly isolated, potentially impacting performance【6】【7】.
* **Bad, because** troubleshooting can be complex due to shared resources and potential for noisy neighbors【2】【3】.

### Isolating tenant workloads to specific nodes

**Description**: With this approach, tenant-specific workloads are only run on nodes provisioned for the respective tenants. To achieve this isolation, native Kubernetes properties (node affinity, and taints and tolerations) are used to target specific nodes for pod scheduling, and prevent pods, from other tenants, from being scheduled on the tenant-specific nodes.

* **Good, because** it offers better resource isolation compared to namespaces, reducing the risk of resource contention【3】【8】.
* **Good, because** it allows for tailored performance tuning per tenant【9】.
* **Neutral, because** it still shares the same control plane, so control plane resource contention is possible【7】.
* **Bad, because** it can be more costly than namespace isolation due to the need for dedicated hardware【3】【4】.
* **Bad, because** operational complexity increases with the need to manage node allocations and potential underutilization【9】.

### Cluster per Tenant

**Description**: The most secure way to run Silo workloads on EKS is to create a distinct EKS cluster for each tenant. In such a design, even a tenant that runs privileged containers and has access to the hosts cannot impact other tenants.

* **Good, because** it provides the highest level of isolation, both in terms of security and resources, eliminating noisy neighbor issues【1】【3】.
* **Good, because** it allows for tailored configurations and optimizations per tenant【8】.
* **Neutral, because** it can offer superior performance, but managing multiple clusters requires significant operational effort【2】【4】.
* **Bad, because** it is the most expensive option, with higher infrastructure and management costs【3】【10】.
* **Bad, because** the complexity of managing multiple clusters can be challenging, requiring robust automation and monitoring tools【2】【9】.

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


# Discovery Questions 
Use the discovery questions provided here to help you evaluate your requirements, priorities, and constraints, ensuring you make a future-proof architectural decision.

## Requirements

1. How many tenants do you anticipate managing within your Kubernetes environment?
2. What future changes or expansions do you anticipate that might impact your Kubernetes strategy?

## Business Drivers

- Which of the business drivers (Operational Excellence, Security, Performance, Cost Management, Reliability) is your top priority, and why?

## Constraints

1. Are there any specific technical constraints or legacy systems that need to be integrated with the new Kubernetes setup?
2. What is your timeline for deploying a multi-tenant Kubernetes environment?

## Team Skills

1. What is the current skill level of your team in managing Kubernetes and related technologies?
2. Do you have any plans for training or engaging 3rd party to fill skill gaps?

## Operational Excellence

1. How do you currently manage and maintain your Kubernetes clusters? What challenges are you facing?
2. What level of automation and monitoring do you have in place for your Kubernetes infrastructure?

## Security

1. What are your specific security requirements for isolating tenants in a multi-tenant environment? How critical is strong isolation between tenants to your business?
2. What is your approach to configuring Kubernetes RBAC and network policies to ensure tenant security?

## Performance

1. What performance metrics are most critical for your applications and tenants?
2. How do you plan to handle potential resource contention between tenants?

## Cost Management

1. What is your current budget for Kubernetes infrastructure and operations?
2. How do you track and allocate costs to different tenants or projects?

## Reliability

1. What are your uptime and availability requirements for your Kubernetes clusters?
2. How do you plan to ensure resilience and high availability for your tenants?
