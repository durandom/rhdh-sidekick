Red Hat Developer Hub (RHDH) is an enterprise-grade internal developer
portal designed to simplify and streamline software development
processes. Combined with Red Hat OpenShift Container Platform, RHDH
empowers platform engineering teams to create customized portals that
improve developer productivity, accelerate onboarding, and enable faster
application delivery. By reducing friction and complexity, RHDH allows
developers to focus on writing high-quality code while adhering to
enterprise-class best practices.

RHDH integrates software templates, pre-designed solutions, and dynamic
plugins into a centralized platform, providing tailored solutions for
operations and development teams in a unified environment.

## Benefits of Red Hat Developer Hub {#benefits-of-rhdh_about-rhdh}

Red Hat Developer Hub offers targeted benefits for developers, platform
engineers, and organizations by simplifying workflows, improving
productivity, and enabling efficient governance.

For developers

:   - Simplified access to tools, resources, and workflows through a
      centralized dashboard.

    - Self-service capabilities with guardrails for cloud-native
      development.

    - Streamlined software and service creation using pre-configured
      templates.

For Platform engineers

:   - Tailored platforms with curated tools to support developers
      efficiently.

    - Centralized repositories for consistent configuration management.

    - Simplified governance of technology choices and operational
      processes.

For organizations

:   - Scalability to onboard new teams quickly while maintaining
      consistency.

    - Enhanced security with enterprise-grade Role-Based Access Control
      (RBAC).

    - Cost and time efficiency by mitigating cognitive load and
      eliminating workflow bottlenecks.

### Key features {#_key-features}

Centralized Dashboard

:   Provides a single interface for accessing developer tools, CI/CD
    pipelines, APIs, monitoring tools, and documentation. Integrated
    with systems like Git, OpenShift, Kubernetes, and JIRA.

Dynamic Plugins

:   Add, update, or remove plugins dynamically without downtime. Popular
    plugins like Tekton, GitOps, Nexus Repository, and JFrog Artifactory
    are supported and verified by Red Hat.

Software Templates

:   Simplify development processes by automating tasks such as
    repository setup, variable insertion, and production pipeline
    creation.

Role-Based Access Control (RBAC)

:   Manage user access with robust security permissions tailored to
    organizational needs.

Scalability

:   Support growing teams and applications while maintaining access to
    the same tools and services.

Configuration Management

:   Centralized repositories ensure synchronized updates, improving
    version control and environment configuration.

<div>

::: title
Additional resources
:::

- For more information about the different features of Red Hat Developer
  Hub and how to extend it, see [Red Hat Developer Hub
  overview](https://developers.redhat.com/rhdh/overview).

</div>

## Integrations in Red Hat Developer Hub {#integrations-in-rhdh_about-rhdh}

Red Hat Developer Hub integrates seamlessly with Red Hat OpenShift
Container Platform and other tools, enabling comprehensive development
and deployment workflows across enterprise.

### Integration with Red Hat OpenShift Container Platform {#_integration-with-red-hat-openshift-container-platform}

Red Hat Developer Hub is fully integrated with Red Hat OpenShift
Container Platform, offering:

- Operators to manage application lifecycle.

- Access to advanced OpenShift capabilities such as service mesh,
  serverless functions, GitOps, and distributed tracing.

- Pipelines and GitOps plugins for streamlined cloud-native workflows.

### Integration with Red Hat Trusted Application Pipeline {#_integration-with-red-hat-trusted-application-pipeline}

Red Hat Trusted Application Pipeline (RHTAP) enhances Red Hat Developer
Hub by providing secure CI/CD capabilities that integrate security
measures into every stage of the development process.

While Red Hat Developer Hub focuses on the inner loop (code, build, and
test), RHTAP manages the outer loop, automating:

- Code scanning

- Image building

- Vulnerability detection

- Deployment

RHTAP includes tools like Red Hat Trusted Artifact Signer (TAS) for code
integrity, Red Hat Trusted Profile Analyzer (TPA) for automated Software
build of Materials (SBOM) creation, and Red Hat Advanced Cluster
Security (ACS) for vulnerability scanning.

### Extending Backstage with Red Hat Developer Hub {#_extending-backstage-with-red-hat-developer-hub}

Red Hat Developer Hub which is a fully supported, enterprise-grade
productized version of upstream Backstage extends the upstream project
by adding:

- Enhanced search capabilities that aggregate data from CI/CD pipelines,
  cloud providers, source control, and more.

- A centralized software catalog for locating applications, APIs, and
  resources.

- Automation through open-source plugins that expand Backstage's core
  functionality.

- Simplified technical documentation using Markdown and GitHub, with
  integrated search for easy navigation.

## Supported platforms {#supported-platforms_about-rhdh}

You can find the supported platforms and life cycle dates for both
current and past versions of Red Hat Developer Hub on the [Life Cycle
page](https://access.redhat.com/support/policy/updates/developerhub).

## Sizing requirements for Red Hat Developer Hub {#rhdh-sizing_about-rhdh}

Scaling the Red Hat Developer Hub requires significant resource
allocation. The following table lists the sizing requirements for
installing and running Red Hat Developer Hub, including Developer Hub
application, database components, and Operator.

+-----------------+-----------------+-----------------+-----------------+
| Components      | Red Hat         | Red Hat         | Red Hat         |
|                 | Developer Hub   | Developer Hub   | Developer Hub   |
|                 | application     | database        | Operator        |
+=================+=================+=================+=================+
| Central         | 4 vCPU          | 2 vCPU          | 1 vCPU          |
| Processing Unit |                 |                 |                 |
| (CPU)           |                 |                 |                 |
+-----------------+-----------------+-----------------+-----------------+
| Memory          | 16 GB           | 8 GB            | 1500 Mi         |
+-----------------+-----------------+-----------------+-----------------+
| Storage size    | 2 GB            | 20 GB           | 50 Mi           |
+-----------------+-----------------+-----------------+-----------------+
| Replicas        | 2 or more       | 3 or more       | 1 or more       |
+-----------------+-----------------+-----------------+-----------------+

: Recommended sizing for running Red Hat Developer Hub

## Red Hat Developer Hub support {#ref-customer-support-info_about-rhdh}

If you experience difficulty with a procedure described in this
documentation, visit the [Red Hat Customer
Portal](http://access.redhat.com). You can use the Red Hat Customer
Portal for the following purposes:

- To search or browse through the Red Hat Knowledgebase of technical
  support articles about Red Hat products.

- To create a [support
  case](https://access.redhat.com/support/cases/#/case/new/get-support?caseCreate=true)
  for Red Hat Global Support Services (GSS). For support case creation,
  select **Red Hat Developer Hub** as the product and select the
  appropriate product version.

- For detailed information about supported platforms and life cycle
  details, see [Red Hat Developer Hub Life
  Cycle](https://access.redhat.com/support/policy/updates/developerhub).

<div>

::: title
Next steps
:::

- [Installing Red Hat Developer Hub on Amazon Elastic Kubernetes
  Service](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_red_hat_developer_hub_on_amazon_elastic_kubernetes_service/index)

- [Installing Red Hat Developer Hub on Google Cloud Platform on Google
  Cloud
  Platform](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_red_hat_developer_hub_on_openshift_dedicated_on_google_cloud_platform/index)

- [Installing Red Hat Developer Hub on Google Kubernetes
  Engine](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_red_hat_developer_hub_on_google_kubernetes_engine/index)

- [Installing Red Hat Developer Hub on Microsoft Azure Kubernetes
  Service](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_red_hat_developer_hub_on_microsoft_azure_kubernetes_service/index)

- [Installing Red Hat Developer Hub on OpenShift Container
  Platform](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_red_hat_developer_hub_on_openshift_container_platform/index)

</div>
