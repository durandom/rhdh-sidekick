You can install Red Hat Developer Hub on OpenShift Container Platform by
using one of the following installers:

The Red Hat Developer Hub Operator

:   - Ready for immediate use in OpenShift Container Platform after an
      administrator installs it with OperatorHub

    - Uses Operator Lifecycle Management (OLM) to manage automated
      subscription updates on OpenShift Container Platform

    - Requires preinstallation of Operator Lifecycle Management (OLM) to
      manage automated subscription updates on Kubernetes

The Red Hat Developer Hub Helm chart

:   - Ready for immediate use in both OpenShift Container Platform and
      Kubernetes

    - Requires manual installation and management

Use the installation method that best meets your needs and preferences.

<div>

::: title
Additional resources
:::

- For more information about choosing an installation method, see [Helm
  Charts vs.
  Operators](https://www.redhat.com/en/technologies/cloud-computing/openshift/helm)

- For more information about the Operator method, see [Understanding
  Operators](https://docs.openshift.com/container-platform/4.15/operators/understanding/olm-what-operators-are.html).

- For more information about the Helm chart method, see [Understanding
  Helm](https://docs.openshift.com/container-platform/4.15/applications/working_with_helm_charts/understanding-helm.html).

</div>

## Installing Red Hat Developer Hub on OpenShift Container Platform with the Operator {#assembly-install-rhdh-ocp-operator}

You can install Red Hat Developer Hub on OpenShift Container Platform by
using the Red Hat Developer Hub Operator in the OpenShift Container
Platform console.

### Installing the Red Hat Developer Hub Operator {#proc-install-operator_assembly-install-rhdh-ocp-operator}

As an administrator, you can install the Red Hat Developer Hub Operator.
Authorized users can use the Operator to install Red Hat Developer Hub
on Red Hat OpenShift Container Platform (OpenShift Container Platform)
and supported Kubernetes platforms. For more information on supported
platforms and versions, see the [Red Hat Developer Hub Life
Cycle](https://access.redhat.com/support/policy/updates/developerhub)
page.

Containers are available for the following CPU architectures:

- AMD64 and Intel 64 (`x86_64`)

<div>

::: title
Prerequisites
:::

- You are logged in as an administrator on the OpenShift Container
  Platform web console.

- You have configured the appropriate roles and permissions within your
  project to create or access an application. For more information, see
  the [Red Hat OpenShift Container Platform documentation on Building
  applications](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/building_applications/index#building-applications-overview).

</div>

:::: important
::: title
:::

For enhanced security, better control over the Operator lifecycle, and
preventing potential privilege escalation, install the Red Hat Developer
Hub Operator in a dedicated default `rhdh-operator` namespace. You can
restrict other users\' access to the Operator resources through role
bindings or cluster role bindings.

You can also install the Operator in another namespace by creating the
necessary resources, such as an Operator group. For more information,
see [Installing global Operators in custom
namespaces](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/operators/index#olm-installing-global-namespaces_olm-adding-operators-to-a-cluster).

However, if the Red Hat Developer Hub Operator shares a namespace with
other Operators, then it shares the same update policy as well,
preventing the customization of the update policy. For example, if one
Operator is set to manual updates, the Red Hat Developer Hub Operator
update policy is also set to manual. For more information, see
[Colocation of Operators in a
namespace](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/operators/index#olm-colocation-namespaces_olm-colocation).
::::

<div>

::: title
Procedure
:::

1.  In the **Administrator** perspective of the OpenShift Container
    Platform web console, click **Operators \> OperatorHub**.

2.  In the **Filter by keyword** box, enter Developer Hub and click the
    **Red Hat Developer Hub** Operator card.

3.  On the **Red Hat Developer Hub Operator** page, click **Install**.

4.  On the **Install Operator** page, use the **Update channel**
    drop-down menu to select the update channel that you want to use:

    - The **fast** channel provides y-stream (x.y) and z-stream (x.y.z)
      updates, for example, updating from version 1.1 to 1.2, or from
      1.1.0 to 1.1.1.

      :::: important
      ::: title
      :::

      The `fast` channel includes all of the updates available for a
      particular version. Any update might introduce unexpected changes
      in your Red Hat Developer Hub deployment. Check the release notes
      for details about any potentially breaking changes.
      ::::

    - The **fast-1.1** channel only provides z-stream updates, for
      example, updating from version 1.1.1 to 1.1.2. If you want to
      update the Red Hat Developer Hub y-version in the future, for
      example, updating from 1.1 to 1.2, you must switch to the **fast**
      channel manually.

5.  On the **Install Operator** page, choose the **Update approval**
    strategy for the Operator:

    - If you choose the **Automatic** option, the Operator is updated
      without requiring manual confirmation.

    - If you choose the **Manual** option, a notification opens when a
      new update is released in the update channel. The update must be
      manually approved by an administrator before installation can
      begin.

6.  Click **Install**.

</div>

<div>

::: title
Verification
:::

- To view the installed Red Hat Developer Hub Operator, click **View
  Operator**.

</div>

<div>

::: title
Additional resources
:::

- [Deploying Red Hat Developer Hub on OpenShift Container Platform with
  the
  Operator](#proc-install-rhdh-ocp-operator_assembly-install-rhdh-ocp-operator)

- [Installing from OperatorHub by using the web
  console](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/operators/index#olm-installing-from-operatorhub-using-web-console_olm-adding-operators-to-a-cluster)

</div>

### Deploying Red Hat Developer Hub on OpenShift Container Platform with the Operator {#proc-install-rhdh-ocp-operator_assembly-install-rhdh-ocp-operator}

As a developer, you can deploy a Red Hat Developer Hub instance on
OpenShift Container Platform by using the **Developer Catalog** in the
Red Hat OpenShift Container Platform web console. This deployment method
uses the Red Hat Developer Hub Operator.

<div>

::: title
Prerequisites
:::

- [An OpenShift Container Platform administrator has installed the Red
  Hat Developer Hub
  Operator](#proc-install-operator_assembly-install-rhdh-ocp-operator).

- [You have provisioned your custom config maps and secrets in your
  `<my-rhdh-project>`
  project](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index.html#provisioning-your-custom-configuration).

- [You have authored your Backstage custom
  resource](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index.html#using-the-operator-to-run-rhdh-with-your-custom-configuration).

</div>

<div>

::: title
Procedure
:::

1.  In the OpenShift Container Platform web console, select your
    `<my-rhdh-project>` project.

2.  From the **Developer** perspective on the OpenShift Container
    Platform web console, click **+Add**.

3.  From the **Developer Catalog** panel, click **Operator Backed**.

4.  In the **Filter by keyword** box, enter *Developer Hub* and click
    the **Red Hat Developer Hub** card.

5.  Click **Create**.

6.  [Add your Backstage custom resource
    content](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/configuring_red_hat_developer_hub/index.html#using-the-operator-to-run-rhdh-with-your-custom-configuration).

7.  On the **Create Backstage** page, click **Create**

</div>

:::: formalpara
::: title
Verification
:::

After the pods are ready, you can access the Red Hat Developer Hub
platform by opening the URL.
::::

1.  Confirm that the pods are ready by clicking the pod in the
    **Topology** view and confirming the **Status** in the **Details**
    panel. The pod status is **Active** when the pod is ready.

2.  From the **Topology** view, click the **Open URL** icon on the
    Developer Hub pod.

    ![operator install 1](images/rhdh/operator-install-1.png)

:::: {#additional-resources_proc-install-rhdh-ocp-operator}
::: title
Additional resources
:::

- [OpenShift Container Platform - Building applications
  overview](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/building_applications/index#building-applications-overview)
::::

## Installing Red Hat Developer Hub on OpenShift Container Platform with the Helm chart {#assembly-install-rhdh-ocp-helm}

You can install Red Hat Developer Hub on OpenShift Container Platform by
using the Helm chart with one of the following methods:

- The OpenShift Container Platform console

- The Helm CLI

### Deploying Developer Hub from the OpenShift Container Platform web console with the Helm Chart {#proc-install-rhdh-ocp-helm-gui_assembly-install-rhdh-ocp-helm}

You can use a Helm chart to install Developer Hub on the Red Hat
OpenShift Container Platform web console.

Helm is a package manager on OpenShift Container Platform that provides
the following features:

- Applies regular application updates using custom hooks

- Manages the installation of complex applications

- Provides charts that you can host on public and private servers

- Supports rolling back to previous application versions

The Red Hat Developer Hub Helm chart is available in the Helm catalog on
OpenShift Dedicated and OpenShift Container Platform.

<div>

::: title
Prerequisites
:::

- You are logged in to your OpenShift Container Platform account.

- A user with the OpenShift Container Platform `admin` role has
  configured the appropriate roles and permissions within your project
  to create an application. For more information about OpenShift
  Container Platform roles, see [Using RBAC to define and apply
  permissions](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/authentication_and_authorization/index#authorization-overview_using-rbac).

- You have created a project in OpenShift Container Platform. For more
  information about creating a project in OpenShift Container Platform,
  see [Red Hat OpenShift Container Platform
  documentation](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/building_applications/index#working-with-projects).

</div>

<div>

::: title
Procedure
:::

1.  From the **Developer** perspective on the Developer Hub web console,
    click **+Add**.

2.  From the **Developer Catalog** panel, click **Helm Chart**.

3.  In the **Filter by keyword** box, enter *Developer Hub* and click
    the **Red Hat Developer Hub** card.

4.  From the Red Hat Developer Hub page, click **Create**.

5.  From your cluster, copy the OpenShift Container Platform router host
    (for example: `apps.<clusterName>.com`).

6.  Select the radio button to configure the Developer Hub instance with
    either the form view or YAML view. The Form view is selected by
    default.

    - Using **Form view**

      a.  To configure the instance with the Form view, go to **Root
          Schema** → **global** → **Enable service authentication within
          Backstage instance** and paste your OpenShift Container
          Platform router host into the field on the form.

    - Using **YAML view**

      a.  To configure the instance with the YAML view, paste your
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

7.  Edit the other values if needed.

    :::: note
    ::: title
    :::

    The information about the host is copied and can be accessed by the
    Developer Hub backend.

    When an OpenShift Container Platform route is generated
    automatically, the host value for the route is inferred and the same
    host information is sent to the Developer Hub. Also, if the
    Developer Hub is present on a custom domain by setting the host
    manually using values, the custom host takes precedence.
    ::::

8.  Click **Create** and wait for the database and Developer Hub to
    start.

9.  Click the **Open URL** icon to start using the Developer Hub
    platform.

    ![rhdh helm install](images/rhdh/rhdh-helm-install.png)

</div>

:::: note
::: title
:::

Your `developer-hub` pod might be in a `CrashLoopBackOff` state if the
Developer Hub container cannot access the configuration files. This
error is indicated by the following log:

``` log
Loaded config from app-config-from-configmap.yaml, env
...
2023-07-24T19:44:46.223Z auth info Configuring "database" as KeyStore provider type=plugin
Backend failed to start up Error: Missing required config value at 'backend.database.client'
```

To resolve the error, verify the configuration files.
::::

### Deploying Developer Hub on OpenShift Container Platform with the Helm CLI {#proc-install-rhdh-ocp-helm-cli_assembly-install-rhdh-ocp-helm}

You can use the Helm CLI to install Red Hat Developer Hub on Red Hat
OpenShift Container Platform.

<div>

::: title
Prerequisites
:::

- You have installed the OpenShift CLI (`oc`) on your workstation.

- You are logged in to your OpenShift Container Platform account.

- A user with the OpenShift Container Platform admin role has configured
  the appropriate roles and permissions within your project to create an
  application. For more information about OpenShift Container Platform
  roles, see [Using RBAC to define and apply
  permissions](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/authentication_and_authorization/index#authorization-overview_using-rbac).

- You have created a project in OpenShift Container Platform. For more
  information about creating a project in OpenShift Container Platform,
  see [Red Hat OpenShift Container Platform
  documentation](https://docs.redhat.com/en/documentation/openshift_container_platform/4.18/html-single/building_applications/index#working-with-projects).

- You have installed the Helm CLI tool.

</div>

<div>

::: title
Procedure
:::

1.  Create and activate the *\<my-rhdh-project\>* OpenShift Container
    Platform project:

        NAMESPACE=<emphasis><rhdh></emphasis>
        oc new-project ${NAMESPACE} || oc project ${NAMESPACE}

2.  Install the Red Hat Developer Hub Helm chart:

        helm upgrade redhat-developer-hub -i https://github.com/openshift-helm-charts/charts/releases/download/redhat-redhat-developer-hub-1.6.0/redhat-developer-hub-1.6.0.tgz

3.  Configure your Developer Hub Helm chart instance with the Developer
    Hub database password and router base URL values from your OpenShift
    Container Platform cluster:

        PASSWORD=$(oc get secret redhat-developer-hub-postgresql -o jsonpath="{.data.password}" | base64 -d)
        CLUSTER_ROUTER_BASE=$(oc get route console -n openshift-console -o=jsonpath='{.spec.host}' | sed 's/^[^.]*\.//')
        helm upgrade redhat-developer-hub -i "https://github.com/openshift-helm-charts/charts/releases/download/redhat-redhat-developer-hub-1.6.0/redhat-developer-hub-1.6.0.tgz" \
            --set global.clusterRouterBase="$CLUSTER_ROUTER_BASE" \
            --set global.postgresql.auth.password="$PASSWORD"

4.  Display the running Developer Hub instance URL:

        echo "https://redhat-developer-hub-$NAMESPACE.$CLUSTER_ROUTER_BASE"

</div>

<div>

::: title
Verification
:::

- Open the running Developer Hub instance URL in your browser to use
  Developer Hub.

</div>

<div>

::: title
Additional resources
:::

- [Installing
  Helm](https://docs.redhat.com/en/documentation/openshift_dedicated/4/html-single/building_applications/index#installing-helm)

</div>
