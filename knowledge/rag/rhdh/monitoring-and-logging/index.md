## Enabling observability for Red Hat Developer Hub on OpenShift Container Platform {#assembly-rhdh-observability}

In OpenShift Container Platform, metrics are exposed through an HTTP
service endpoint under the `/metrics` canonical name. You can create a
`ServiceMonitor` custom resource (CR) to scrape metrics from a service
endpoint in a user-defined project.

### Enabling metrics monitoring in a Red Hat Developer Hub Operator installation on an OpenShift Container Platform cluster {#proc-admin-enabling-metrics-ocp-operator_assembly-rhdh-observability}

You can enable and view metrics for an Operator-installed Red Hat
Developer Hub instance from the **Developer** perspective of the
OpenShift Container Platform web console.

<div>

::: title
Prerequisites
:::

- Your OpenShift Container Platform cluster has [monitoring for
  user-defined
  projects](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/monitoring/index#enabling-monitoring-for-user-defined-projects)
  enabled.

- You have installed Red Hat Developer Hub on OpenShift Container
  Platform using the Red Hat Developer Hub Operator.

- You have installed the OpenShift CLI (`oc`).

</div>

:::: formalpara
::: title
Procedure
:::

Currently, the Red Hat Developer Hub Operator does not support creating
a `ServiceMonitor` custom resource (CR) by default. You must complete
the following steps to create a `ServiceMonitor` CR to scrape metrics
from the endpoint.
::::

1.  Create the `ServiceMonitor` CR as a YAML file:

    ``` yaml
    apiVersion: monitoring.coreos.com/v1
    kind: ServiceMonitor
    metadata:
      name: <developer_hub_service_monitor_name>
      namespace: <rhdh_namespace_name>
      labels:
        app.kubernetes.io/instance: <rhdh_cr_name>
        app.kubernetes.io/name: Backstage
    spec:
      namespaceSelector:
        matchNames:
          - <rhdh_namespace_name>
      selector:
        matchLabels:
          app.kubernetes.io/instance: <deployment_name>
          app.kubernetes.io/name: <rhdh_cr_type>
      endpoints:
      - port: http-metrics
        path: '/metrics'
    ```

    - The name of your `ServiceMonitor` resource, for example,
      `developer_hub_service_monitor`.

    - The namespace where your `ServiceMonitor` will live, for example,
      `my-rhdh-project`.

    - The label name identifying the `ServiceMonitor` CR instance, for
      example, `my-rhdh-custom-resource`.

    - The namespace where your RHDH instance is installed, for example,
      `my-rhdh-project`.

    - The name of your RHDH deployment, for example, `developer-hub`.

    - The name of your RHDH application, for example, `backstage`.

      :::: note
      ::: title
      :::

      `spec.selector.matchLabels` configuration must match the labels of
      your RHDH installation.
      ::::

2.  Apply the `ServiceMonitor` CR by running the following command:

    ``` terminal
    oc apply -f <filename>
    ```

<div>

::: title
Verification
:::

1.  From the **Developer** perspective in the OpenShift Container
    Platform web console, select the **Observe** view.

2.  Click the **Metrics** tab to view metrics for Red Hat Developer Hub
    pods.

3.  From the Developer perspective in the OpenShift Container Platform
    web console, click **Project \> Services** and verify the labels for
    `backstage-developer-hub`.

</div>

### Enabling metrics monitoring in a Helm chart installation on an OpenShift Container Platform cluster {#proc-admin-enabling-metrics-ocp-helm_assembly-rhdh-observability}

You can enable and view metrics for a Red Hat Developer Hub Helm
deployment from the **Developer** perspective of the OpenShift Container
Platform web console.

<div>

::: title
Prerequisites
:::

- Your OpenShift Container Platform cluster has [monitoring for
  user-defined
  projects](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/monitoring/index#enabling-monitoring-for-user-defined-projects)
  enabled.

- You have installed Red Hat Developer Hub on OpenShift Container
  Platform using the Helm chart.

</div>

<div>

::: title
Procedure
:::

1.  From the **Developer** perspective in the OpenShift Container
    Platform web console, select the **Topology** view.

2.  Click the overflow menu of the Red Hat Developer Hub Helm chart, and
    select **Upgrade**.

    ![helm upgrade](images/rhdh/helm-upgrade.png)

3.  On the **Upgrade Helm Release** page, select the **YAML view**
    option in **Configure via**, then configure the `metrics` section in
    the YAML, as shown in the following example:

    ``` yaml
    upstream:
    # ...
      metrics:
        serviceMonitor:
          enabled: true
          path: /metrics
          port: http-metrics
    # ...
    ```

    ![upgrade helm metrics](images/rhdh/upgrade-helm-metrics.png)

4.  Click **Upgrade**.

</div>

<div>

::: title
Verification
:::

1.  From the **Developer** perspective in the OpenShift Container
    Platform web console, select the **Observe** view.

2.  Click the **Metrics** tab to view metrics for Red Hat Developer Hub
    pods.

</div>

<div>

::: title
Additional resources
:::

- [OpenShift Container Platform - Managing
  metrics](https://docs.openshift.com/container-platform/latest/observability/monitoring/managing-metrics.html)

</div>

## Monitoring and logging Red Hat Developer Hub on Amazon Web Services (AWS) {#assembly-monitoring-and-logging-with-aws_assembly-rhdh-observability}

You can configure Red Hat Developer Hub to use Amazon CloudWatch for
real-time monitoring and Amazon Prometheus for comprehensive logging.
This is convenient when hosting Developer Hub on Amazon Web Services
(AWS) infrastructure.

### Monitoring with Amazon Prometheus {#assembly-monitoring-with-amazon-prometheus_assembly-rhdh-observability}

You can configure Red Hat Developer Hub to use Amazon Prometheus for
comprehensive logging. Amazon Prometheus extracts data from pods that
have specific pod annotations.

#### Prerequisites {#_prerequisites}

- You [configured Prometheus for your Elastic Kubernetes Service (EKS)
  clusters](https://docs.aws.amazon.com/eks/latest/userguide/prometheus.htm).

- You [created an Amazon managed service for the Prometheus
  workspace](https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-onboard-create-workspace.html).

- You [configured Prometheus to import the Developer Hub
  metrics](https://docs.aws.amazon.com/prometheus/latest/userguide/AMP-onboard-ingest-metrics.html).

- You ingested Prometheus metrics into the created workspace.

#### Configuring annotations for monitoring with Amazon Prometheus by using the Red Hat Developer Hub Operator {#configuring-annotations-for-monitoring-with-amazon-prometheus-by-using-the-operator_assembly-rhdh-observability}

To enable logging to Amazon Prometheus, you can configure the required
pod annotations by using the Red Hat Developer Hub Operator.

<div>

::: title
Procedure
:::

1.  As an administrator of the Red Hat Developer Hub Operator, edit the
    default configuration to add Prometheus annotations as follows:

        # Update OPERATOR_NS accordingly
        $ OPERATOR_NS=rhdh-operator
        $ kubectl edit configmap backstage-default-config -n "${OPERATOR_NS}"

2.  Find the `deployment.yaml` key in the config map and add the
    annotations to the `spec.template.metadata.annotations` field as
    follows:

    ``` yaml
    deployment.yaml: |-
      apiVersion: apps/v1
      kind: Deployment
      # --- truncated ---
      spec:
        template:
          # --- truncated ---
          metadata:
            labels:
             rhdh.redhat.com/app:  # placeholder for 'backstage-<cr-name>'
            # --- truncated ---
            annotations:
              prometheus.io/scrape: 'true'
              prometheus.io/path: '/metrics'
              prometheus.io/port: '9464'
              prometheus.io/scheme: 'http'
      # --- truncated ---
    ```

3.  Save your changes.

</div>

:::: formalpara
::: title
Verification
:::

To verify if the scraping works:
::::

1.  Use `kubectl` to port-forward the Prometheus console to your local
    machine as follows:

        $ kubectl --namespace=prometheus port-forward deploy/prometheus-server 9090

2.  Open your web browser and navigate to `http://localhost:9090` to
    access the Prometheus console.

3.  Monitor relevant metrics, such as `process_cpu_user_seconds_total`.

#### Configuring annotations for monitoring with Amazon Prometheus by using the Red Hat Developer Hub Helm chart {#configuring-annotations-for-monitoring-with-amazon-prometheus-by-using-the-helm-chart_assembly-rhdh-observability}

To enable logging to Amazon Prometheus, you can configure the required
pod annotations by using the Red Hat Developer Hub Helm chart.

<div>

::: title
Procedure
:::

- To annotate the backstage pod for monitoring, update your
  `values.yaml` file as follows:

  ``` yaml
  upstream:
    backstage:
      # --- TRUNCATED ---
      podAnnotations:
        prometheus.io/scrape: 'true'
        prometheus.io/path: '/metrics'
        prometheus.io/port: '9464'
        prometheus.io/scheme: 'http'
  ```

</div>

:::: formalpara
::: title
Verification
:::

To verify if the scraping works:
::::

1.  Use `kubectl` to port-forward the Prometheus console to your local
    machine as follows:

    ``` bash
    kubectl --namespace=prometheus port-forward deploy/prometheus-server 9090
    ```

2.  Open your web browser and navigate to `http://localhost:9090` to
    access the Prometheus console.

3.  Monitor relevant metrics, such as `process_cpu_user_seconds_total`.

### Logging with Amazon CloudWatch {#assembly-logging-with-amazon-cloudwatch_assembly-rhdh-observability}

Logging within the Red Hat Developer Hub relies on the [Winston
library](https://github.com/winstonjs/winston). The default logging
level is `info`. To have more detailed logs, set the `LOG_LEVEL`
environment variable to `debug` in your Red Hat Developer Hub instance.

#### Configuring the application log level by using the Red Hat Developer Hub Operator {#configuring-the-application-log-level-by-using-the-operator_assembly-rhdh-observability}

You can configure the application log level by using the Red Hat
Developer Hub Operator.

<div>

::: title
Procedure
:::

- Modify the logging level by including the environment variable
  `LOG_LEVEL` in your custom resource as follows:

  ``` yaml
  spec:
    # Other fields omitted
    application:
      extraEnvs:
        envs:
          - name: LOG_LEVEL
            value: debug
  ```

</div>

#### Configuring the application log level by using the Red Hat Developer Hub Helm chart {#configuring-the-application-log-level-by-using-the-helm-chart_assembly-rhdh-observability}

You can configure the application log level by using the Red Hat
Developer Hub Helm chart.

<div>

::: title
Procedure
:::

- Modify the logging level by adding the environment variable
  `LOG_LEVEL` to your Helm chart `values.yaml` file:

  ``` yaml
  upstream:
    backstage:
      # --- Truncated ---
      extraEnvVars:
        - name: LOG_LEVEL
          value: debug
  ```

</div>

#### Retrieving logs from Amazon CloudWatch {#retrieving-logs-from-amazon-cloudwatch_assembly-rhdh-observability}

<div>

::: title
Prerequisites
:::

- CloudWatch Container Insights is used to capture logs and metrics for
  Amazon Elastic Kubernetes Service. For more information, see [Logging
  for Amazon Elastic Kubernetes
  Service](https://docs.aws.amazon.com/prescriptive-guidance/latest/implementing-logging-monitoring-cloudwatch/kubernetes-eks-logging.html)
  documentation.

- To capture the logs and metrics, [install the Amazon CloudWatch
  Observability EKS
  add-on](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Container-Insights-setup-EKS-addon.html)
  in your cluster. Following the setup of Container Insights, you can
  access container logs using Logs Insights or Live Tail views.

- CloudWatch names the log group where all container logs are
  consolidated in the following manner:

      /aws/containerinsights/<cluster_name>/application

</div>

<div>

::: title
Procedure
:::

- To retrieve logs from the Developer Hub instance, run a query such as:

  ``` sql
  fields @timestamp, @message, kubernetes.container_name
  | filter kubernetes.container_name in ["install-dynamic-plugins", "backstage-backend"]
  ```

</div>

## Monitoring and logging with Azure Kubernetes Services (AKS) in Red Hat Developer Hub {#assembly-monitoring-and-logging-aks}

Monitoring and logging are integral aspects of managing and maintaining
Azure Kubernetes Services (AKS) in Red Hat Developer Hub. With features
like Managed Prometheus Monitoring and Azure Monitor integration,
administrators can efficiently monitor resource utilization, diagnose
issues, and ensure the reliability of their containerized workloads.

### Enabling Azure Monitor metrics {#proc-enabling-azure-monitor-metrics_assembly-monitoring-and-logging-aks}

To enable managed Prometheus monitoring, use the
`-enable-azure-monitor-metrics` option within either the `az aks create`
or `az aks update` command, depending on whether you're creating a new
cluster or updating an existing one, such as:

``` bash
az aks create/update --resource-group <your-ResourceGroup> --name <your-Cluster> --enable-azure-monitor-metrics
```

The previous command installs the metrics add-on, which gathers
[Prometheus
metrics](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/prometheus-metrics-overview).
Using the previous command, you can enable monitoring of Azure resources
through both native Azure Monitor metrics. You can also view the results
in the portal under **Monitoring → Insights**. For more information, see
[Monitor Azure resources with Azure
Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/monitor-azure-resource).

Furthermore, metrics from both the Managed Prometheus service and Azure
Monitor can be accessed through Azure Managed Grafana service. For more
information, see [Link a Grafana
workspace](https://learn.microsoft.com/en-us/azure/azure-monitor/essentials/azure-monitor-workspace-manage?tabs=azure-portal#link-a-grafana-workspace)
section.

By default, Prometheus uses the minimum ingesting profile, which
optimizes ingestion volume and sets default configurations for scrape
frequency, targets, and metrics collected. The default settings can be
customized through custom configuration. Azure offers various methods,
including using different ConfigMaps, to provide scrape configuration
and other metric add-on settings. For more information about default
configuration, see [Default Prometheus metrics configuration in Azure
Monitor](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/prometheus-metrics-scrape-default)
and [Customize scraping of Prometheus metrics in Azure Monitor managed
service for
Prometheus](https://learn.microsoft.com/en-us/azure/azure-monitor/containers/prometheus-metrics-scrape-configuration?tabs=CRDConfig%2CCRDScrapeConfig)
documentation.

### Configuring annotations for monitoring {#proc-configure-annotations-for-aks-monitoring_assembly-monitoring-and-logging-aks}

You can configure the annotations for monitoring Red Hat Developer Hub
specific metrics in both Helm deployment and Operator-backed deployment.

Helm deployment

:   To annotate the backstage pod for monitoring, update your
    `values.yaml` file as follows:

    ``` yaml
    upstream:
      backstage:
        # --- TRUNCATED ---
        podAnnotations:
          prometheus.io/scrape: 'true'
          prometheus.io/path: '/metrics'
          prometheus.io/port: '9464'
          prometheus.io/scheme: 'http'
    ```

Operator-backed deployment

:   <div>

    ::: title
    Procedure
    :::

    1.  As an administrator of the operator, edit the default
        configuration to add Prometheus annotations as follows:

        ``` bash
        # Update OPERATOR_NS accordingly
        OPERATOR_NS=rhdh-operator
        kubectl edit configmap backstage-default-config -n "${OPERATOR_NS}"
        ```

    2.  Find the `deployment.yaml` key in the ConfigMap and add the
        annotations to the `spec.template.metadata.annotations` field as
        follows:

        ``` yaml
        deployment.yaml: |-
          apiVersion: apps/v1
          kind: Deployment
          # --- truncated ---
          spec:
            template:
              # --- truncated ---
              metadata:
                labels:
                 rhdh.redhat.com/app:  # placeholder for 'backstage-<cr-name>'
                # --- truncated ---
                annotations:
                  prometheus.io/scrape: 'true'
                  prometheus.io/path: '/metrics'
                  prometheus.io/port: '9464'
                  prometheus.io/scheme: 'http'
          # --- truncated ---
        ```

    3.  Save your changes.

    </div>

:::: formalpara
::: title
Verification
:::

To verify if the scraping works, navigate to the corresponding Azure
Monitor Workspace and view the metrics under **Monitoring → Metrics**.
::::

### Viewing logs with Azure Kubernetes Services (AKS) {#proc-view-logs-aks_assembly-monitoring-and-logging-aks}

You can access live data logs generated by Kubernetes objects and
collect log data in Container Insights within AKS.

<div>

::: title
Prerequisites
:::

- You have deployed Developer Hub on AKS.

</div>

For more information, see [Installing Red Hat Developer Hub on Microsoft
Azure Kubernetes
Service](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_red_hat_developer_hub_on_microsoft_azure_kubernetes_service/index.html#assembly-install-rhdh-aks).

View live logs from your Developer Hub instance

:   1.  Navigate to the Azure Portal.

    2.  Search for the resource group `<your-ResourceGroup>` and locate
        your AKS cluster `<your-Cluster>`.

    3.  Select **Kubernetes resources → Workloads** from the menu.

    4.  Select the `<your-rhdh-cr>-developer-hub` (in case of Helm Chart
        installation) or `<your-rhdh-cr>-backstage` (in case of
        Operator-backed installation) deployment.

    5.  Click **Live Logs** in the left menu.

    6.  Select the pod.

        :::: note
        ::: title
        :::

        There must be only single pod.
        ::::

    Live log data is collected and displayed.

View real-time log data from the Container Engine

:   1.  Navigate to the Azure Portal.

    2.  Search for the resource group `<your-ResourceGroup>` and locate
        your AKS cluster `<your-Cluster>`.

    3.  Select **Monitoring** → **Insights** from the menu.

    4.  Go to the **Containers** tab.

    5.  Find the backend-backstage container and click it to view
        real-time log data as it's generated by the Container Engine.
