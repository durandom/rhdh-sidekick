You can install Developer Hub on OpenShift Dedicated on Google Cloud
Platform (GCP) using one of the following methods:

- The Red Hat Developer Hub Operator

- The Red Hat Developer Hub Helm chart

## Installing Red Hat Developer Hub on OpenShift Dedicated on GCP using the Operator {#proc-install-rhdh-osd-gcp-operator_title-install-rhdh-osd-gcp}

You can install Developer Hub on OpenShift Dedicated on GCP using the
Red Hat Developer Hub Operator.

<div>

::: title
Prerequisites
:::

- You have a valid GCP account.

- Your OpenShift Dedicated cluster is running on GCP. For more
  information, see [Creating a cluster on
  GCP](https://docs.redhat.com/en/documentation/openshift_dedicated/4/html/installing_accessing_and_deleting_openshift_dedicated_clusters/osd-creating-a-cluster-on-gcp)
  in Red Hat OpenShift Dedicated documentation.

- You have administrator access to OpenShift Dedicated cluster and GCP
  project.

</div>

<div>

::: title
Procedure
:::

1.  In the **Administrator** perspective of the OpenShift Container
    Platform web console, click **Operators \> OperatorHub**.

2.  In the **Filter by keyword** box, enter Developer Hub and click the
    **Red Hat Developer Hub Operator** card.

3.  On the **Red Hat Developer Hub Operator** page, click **Install**.

4.  In the OpenShift Container Platform console, navigate to **Installed
    Operators** and select **Red Hat Developer Hub Operator**.

5.  From the Developer Hub Operator page, click **Create New Instance**
    and specify the name and namespace where you want to deploy
    Developer Hub.

6.  Configure the required settings such as Git integration, secret
    management, and user permissions.

7.  Review the configuration, select deployment options, and click
    **Create**.

</div>

<div>

::: title
Verification
:::

- To access the Developer Hub, navigate to the Developer Hub URL
  provided in the OpenShift Container Platform web console.

</div>

<div>

::: title
Additional resources
:::

- [Configuring Red Hat Developer
  Hub](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index)

- [Customizing Red Hat Developer
  Hub](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/customizing_red_hat_developer_hub/index)

</div>

## Installing Red Hat Developer Hub on OpenShift Dedicated on GCP using the Helm Chart {#proc-install-rhdh-osd-gcp-helm_title-install-rhdh-osd-gcp}

You can install Developer Hub on OpenShift Dedicated on GCP using the
Red Hat Developer Hub Helm Chart.

<div>

::: title
Prerequisites
:::

- You have a valid GCP account.

- Your OpenShift Dedicated cluster is running on GCP. For more
  information, see [Creating a cluster on
  GCP](https://docs.redhat.com/en/documentation/openshift_dedicated/4/html/installing_accessing_and_deleting_openshift_dedicated_clusters/osd-creating-a-cluster-on-gcp)
  in Red Hat OpenShift Dedicated documentation.

- You have installed Helm 3 or the latest.

</div>

<div>

::: title
Procedure
:::

1.  From the **Developer** perspective on the Developer Hub web console,
    click **+Add**.

2.  From the **Developer Catalog** panel, click **Helm Chart**.

3.  In the **Filter by keyword** box, enter Developer Hub and click the
    **Red Hat Developer Hub** card.

4.  From the Red Hat Developer Hub page, click **Create**.

5.  From your cluster, copy the OpenShift Container Platform router host
    (for example: `apps.<clusterName>.com`).

6.  Select the radio button to configure the Developer Hub instance with
    either the form view or YAML view. The **Form view** is selected by
    default.

    a.  Using **Form view**

        i.  To configure the instance with the Form view, go to **Root
            Schema → global → Enable service authentication within
            Backstage instance** and paste your OpenShift Container
            Platform router host into the field on the form.

    b.  Using **YAML view**

        i.  To configure the instance with the YAML view, paste your
            OpenShift Container Platform router hostname in the
            `global.clusterRouterBase` parameter value as shown in the
            following example:

            ``` yaml
            global:
              auth:
                backend:
                  enabled: true
              clusterRouterBase: apps.<clusterName>.com
              # other Red Hat Developer Hub Helm Chart configurations
            ```

7.  Edit the other values if needed, then click **Create** and wait for
    the database and Developer Hub to start.

</div>

<div>

::: title
Verification
:::

- To access the the Developer Hub, click the **Open URL** icon.

</div>

<div>

::: title
Additional resources
:::

- [Configuring Red Hat Developer
  Hub](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index)

- [Customizing Red Hat Developer
  Hub](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/customizing_red_hat_developer_hub/index)

</div>
