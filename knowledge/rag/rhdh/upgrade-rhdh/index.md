## Upgrading the Red Hat Developer Hub Operator {#proc-upgrade-rhdh-operator_title-upgrade-rhdh}

If you use the Operator to deploy your Red Hat Developer Hub instance,
then an administrator can use the OpenShift Container Platform web
console to upgrade the Operator to a later version.

OpenShift Container Platform is currently supported from version 4.14 to
4.18. See also the [Red Hat Developer Hub Life
Cycle](https://access.redhat.com/support/policy/updates/developerhub).

<div>

::: title
Prerequisites
:::

- You are logged in as an administrator on the OpenShift Container
  Platform web console.

- You have installed the Red Hat Developer Hub Operator.

- You have configured the appropriate roles and permissions within your
  project to create or access an application. For more information, see
  the [Red Hat OpenShift Container Platform documentation on Building
  applications](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/building_applications/index#building-applications-overview).

</div>

<div>

::: title
Procedure
:::

1.  In the **Administrator** perspective of the OpenShift Container
    Platform web console, click **Operators \> Installed Operators**.

2.  On the **Installed Operators** page, click **Red Hat Developer Hub
    Operator**.

3.  On the **Red Hat Developer Hub Operator** page, click the
    **Subscription** tab.

4.  From the **Upgrade status** field on the **Subscription details**
    page, click **Upgrade available**.

    :::: note
    ::: title
    :::

    If there is no upgrade available, the **Upgrade status** field value
    is **Up to date**.
    ::::

5.  On the **InstallPlan details** page, click **Preview InstallPlan \>
    Approve**.

</div>

<div>

::: title
Verification
:::

- The **Upgrade status** field value on the **Subscription details**
  page is **Up to date**.

</div>

<div>

::: title
Additional resources
:::

- [Installing Red Hat Developer Hub on OpenShift Container Platform with
  the
  Operator](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_red_hat_developer_hub_on_openshift_container_platform/index#proc-install-operator_assembly-install-rhdh-ocp-operator).

- [Installing from OperatorHub by using the web
  console](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/operators/index#olm-installing-from-operatorhub-using-web-console_olm-adding-operators-to-a-cluster)

</div>

## Upgrading the Red Hat Developer Hub Helm Chart {#proc-upgrade-rhdh-helm_title-upgrade-rhdh}

You can upgrade to a later version of Red Hat Developer Hub in OpenShift
Container Platform by using either the web console or the CLI.

- OpenShift Container Platform web console

  1.  In the **Developer** perspective, click **Helm** to open the
      **Helm Releases** tab.

  2.  Click the overflow menu on the Helm release that you want to use
      and select **Upgrade**.

  3.  On the **Upgrade Helm Release** page, select the version of
      Developer Hub that you want to upgrade to from the chart version
      drop-down list.

  4.  Click **Upgrade**.

      :::: note
      ::: title
      :::

      It might take a few minutes to delete the resources in the older
      versions and to start the newer versions of the Developer Hub
      pods.
      ::::

  5.  Close all open Developer Hub web pages, and log in again to verify
      that the upgrade was successful.

- OpenShift Container Platform CLI

  1.  Log in to the OpenShift Container Platform cluster as the cluster
      administrator and switch to the project or namespace in which
      Developer Hub was installed.

      ``` terminal
      oc login -u <user> -p <password> https://api.<HOSTNAME>:6443
      oc project my-rhdh-project
      ```

  2.  For a new version of the Developer Hub Helm chart, run the
      following upgrade command:

      ``` terminal
      helm upgrade -i rhdh -f new-values.yml \
        openshift-helm-charts/redhat-developer-hub --version 1.6.0
      ```

      :::: note
      ::: title
      :::

      You can also provide extra values to the chart by creating a
      `new-values.yml` file on your workstation with values that
      override the attributes in the installed chart or by adding new
      attributes.
      ::::
