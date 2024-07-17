# Chose a host OS for your EKS worker nodes

Deciding on the right host image for EKS worker nodes is crucial to optimizing performance, security, and operational excellence based on an organization's specific needs. The host image provides the base operating system and runtime for the nodes.

## Decision Drivers

- Security - Ability to harden and control the host environment 
- Performance - Optimized for running containers and Kubernetes 
- Operational Excellence - Reliability, automation, and ease of management 
- Benefits - Balancing benefits with operation overhead

## Considered Options

- Build EKS worker node AMI on Amazon EKS Optimised AMI
- Build EKS worker node AMI on Organisation Hardened Linux SOE (i.e. RHEL)  
- Build EKS worker node AMI on Amazon EKS Optimised AMI
- Bottlerocket

## Pros and Cons of the Options


### Build EKS worker node AMI on Amazon Linux AMI

Amazon Linux is a general purpose OS provided by AWS. This is a solution that customer will need to manage the lifecycle of building EKS worker node AMI based on Amazon Linux AMI. They could refer to the open source Amazon Optimized EKS AMI on what packages to be installed. [1]


* Good, Customers have full control on the lifecycle of the worker node AMIs, which could meet their organisation SLAs
* Good, leverage some built-in benefits included in Amazon Linux such as acclerated instance support 
* Bad, because lacks EKS specific optimizations
* Bad, remarkable effort is required to build and manage the worker node AMI lifecycle.


### Organisation Hardened Linux SOE (i.e. RHEL)
This is a solution that customer will need to manage the lifecycle of building EKS worker node AMI based on their organisational Hardened Linux SOE They could refer to the open source Amazon Optimized EKS AMI on what packages to be installed. [2]


* Good, because provides full flexibility to customize to unique needs
* Good, Customers have full control on the lifecycle of the worker node AMIs, which could meet their organisation SLAs.
* Bad, because lacks EKS specific optimizations
* Bad, Significant effort is required to build and manage the worker node AMI lifecycle. 


### Amazon EKS Optimised AMI

This is a solution that customer will need to manage the lifecycle of building EKS worker node AMI based on Amazon EKS Optimised AMI. [3]

* Good, because it is purpose-built by AWS for EKS performance and security 
* Good, leverage some built-in benefits included in Amazon Linux such as acclerated instance support 
* Good, leverage 
* Neutral, because relies on AWS to release the base image  


### Bottlerocket - AWS managed minimal OS for containers

Bottlerocket is a dedicated Linux OS for running containers, managed by AWS.

* Good, because optimized specifically for container workloads 
* Good, Reduces the effort to manage additional packages since it has been pre-tested by AWS to work with EKS.
* Good, Reduce container startup time on Amazon EKS with Bottlerocket data volume
* Neutral, because limited flexibility as a minimal OS  
* Bad, because may not support running third-party agents 

## Resources


1. [Amazon EKS AMI Build Specification](https://github.com/awslabs/amazon-eks-ami/tree/main)

2. [Amazon EKS AMI RHEL Build Specification](https://github.com/aws-samples/amazon-eks-ami-rhel)

3. [Amazon EKS Custom AMIs](https://github.com/aws-samples/amazon-eks-custom-amis
)
4. [Amazon EKS Now Supports Bottlerocket](https://aws.amazon.com/blogs/containers/amazon-eks-now-supports-bottlerocket/)

5. [AWS Bottlerocket](https://aws.amazon.com/bottlerocket/) 

6. [Amazon Linux Security Center](https://alas.aws.amazon.com/alas2023.html)

7. [Amazon EKS Optimized AMI releases](https://github.com/awslabs/amazon-eks-ami/releases)

8. [Reduce container startup time on Amazon EKS with Bottlerocket data volume](https://aws.amazon.com/blogs/containers/reduce-container-startup-time-on-amazon-eks-with-bottlerocket-data-volume/)



### Discovery Questions

1. How much effort are you able to dedicate to hardening and optimizing a custom host image? The less effort available, the more a managed image like Bottlerocket may be preferred.

2. Do you have any unique requirements or dependencies that would require a customized or full Linux distribution like Ubuntu or RHEL? 

3. Are there any regulatory compliance or security certifications you need to adhere to that may constrain the host image?

4. What level of performance and low latency is needed for your containerized applications? Any specific requrement of start time of conatiner if you image size is very big. 

5. Do you need to run third-party agents or software outside of containers on the host? This may rule out minimal OS options.  

6. Do you expect to need to frequently SSH into worker nodes for troubleshooting or maintenance?

7. Do you want the OS managed fully by AWS or require more customization control?

