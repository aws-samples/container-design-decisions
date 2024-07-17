---
layout: page
title: Designing Operating Model for Container Platform
permalink: /operations
---

## Designing Operating Model for Container Platform

Designing an operating model for a container platform involves evaluating multiple options to meet specific organizational needs regarding operational excellence, constraints, competency, control and security, consistency, cost management, and productivity.

## Decision Drivers

* **Operational Excellence:** Ensuring efficient management and maintenance of the container platform.
* **Constraints:** Identifying limitations and challenges in the current operational model.
* **Competency:** Assessing the skill level and experience of the team with container technologies and DevOps practices.
* **Control and Security:** Protecting the infrastructure and data from vulnerabilities and breaches.
* **Consistency:** Achieving uniformity in processes and practices across teams.
* **Cost Management:** Balancing performance and resource allocation against cost.
* **Productivity:** Enhancing the efficiency and output of development teams.

## Considered Options

* **Centralized Provisioning**
* **Platform-enabled Golden Path**
* **Embedded DevOps**
* **Decentralized DevOps**

## Pros and Cons of the Options

### Centralized Provisioning

**Description:**
In a centralized provisioning model, a dedicated team is responsible for architecting, deploying, and managing the infrastructure. This model provides central control over resource provisioning but may introduce bottlenecks and slower deployment cycles.

* **Good, because** it ensures consistency and central control over resources.
* **Good, because** it allows specialized teams to handle complex infrastructure tasks.
* **Neutral, because** it may lead to a backlog of requests, slowing down development.
* **Bad, because** it can reduce the autonomy of development teams, leading to frustration.
* **Bad, because** it may become a single point of failure if the central team encounters issues.

### Platform-enabled Golden Path

**Description:**
This model offers a predefined set of best practices and tools, allowing for customization while maintaining consistency. It strikes a balance between flexibility and standardization.

* **Good, because** it promotes best practices and reduces the risk of misconfigurations.
* **Good, because** it enables rapid onboarding of new teams and projects.
* **Neutral, because** it requires significant effort to develop and maintain the golden path.
* **Bad, because** it may limit flexibility for teams with unique requirements.
* **Bad, because** deviations from the golden path might not be well-supported.

### Embedded DevOps

**Description:**
Embedded DevOps places DevOps engineers within individual development teams, ensuring close collaboration and tailored support for each team's needs.

* **Good, because** it fosters close collaboration between developers and operations.
* **Good, because** it allows for tailored solutions that meet the specific needs of each team.
* **Neutral, because** it requires more DevOps resources, which can be costly.
* **Bad, because** it may lead to inconsistencies across the organization.
* **Bad, because** knowledge and expertise can become siloed within individual teams.

### Decentralized DevOps

**Description:**
This model gives development teams full ownership and responsibility for defining and managing their infrastructure and pipelines, offering maximum autonomy and flexibility.

* **Good, because** it maximizes team autonomy and enables rapid innovation.
* **Good, because** it allows teams to tailor their processes and tools to best fit their specific needs.
* **Neutral, because** it requires strong governance and communication to ensure consistency.
* **Bad, because** it can lead to fragmentation and inconsistency, making it harder to maintain standards.
* **Bad, because** it may result in duplicated efforts and increased overhead as each team develops their own solutions.

## Resources

1. [How organizations are modernizing for cloud operations](https://aws.amazon.com/blogs/devops/how-organizations-are-modernizing-for-cloud-operations/)
2. [Modernizing operations in the AWS Cloud](https://docs.aws.amazon.com/prescriptive-guidance/latest/migration-operations-integration/welcome.html)
3. [Strategy for modernizing applications in the AWS Cloud](https://docs.aws.amazon.com/prescriptive-guidance/latest/strategy-modernizing-applications/welcome.html)

## Discovery Questions

1. **Priorities and Requirements:**
   - What are the most important goals you want to achieve with your container platform (e.g., faster deployment, better security, reduced costs)?
   - Are there any specific requirements or constraints that must be met (e.g., regulatory compliance, integration with existing systems)?

2. **Constraints:**
   - What limitations or challenges do you face in your current operational model (e.g., resource bottlenecks, lack of automation)?
   - How do you manage dependencies and coordination between different teams or departments?

3. **Competency:**
   - What is the current skill level and experience of your team with container technologies and DevOps practices?
   - How comfortable are your teams with managing their own infrastructure versus relying on a central team?

4. **Control and Security:**
   - What are your primary security concerns related to container management and orchestration?
   - How do you currently handle security policies and compliance requirements across different teams?

5. **Consistency:**
   - How important is it for your organization to have consistent processes and practices across all teams?
   - What measures do you have in place to ensure uniformity in your operations?

6. **Cost Management:**
   - What is your budget for managing and maintaining your container platform, and how do you plan to control costs?
   - How do you currently allocate resources and manage cost efficiency across your teams?

7. **Productivity:**
   - How do you measure the productivity of your development teams?
   - What tools and practices do you use to enhance the efficiency and output of your teams?

8. **Future Plans:**
   - What are your plans for scaling your container platform, and how do you envision the growth of your DevOps practices?
   - How do you plan to stay updated with the latest technologies and best practices in container management and orchestration?
