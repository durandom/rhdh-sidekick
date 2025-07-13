## Using Ansible plug-ins for Red Hat Developer Hub {#_using-ansible-plug-ins-for-red-hat-developer-hub}

Ansible plug-ins for Red Hat Developer Hub deliver an Ansible-specific
portal experience with curated learning paths, push-button content
creation, integrated development tools, and other opinionated resources.

:::: important
::: title
:::

The Ansible plug-ins are a Technology Preview feature only.

Technology Preview features are not supported with Red Hat production
service level agreements (SLAs), might not be functionally complete, and
Red Hat does not recommend using them for production. These features
provide early access to upcoming product features, enabling customers to
test functionality and provide feedback during the development process.

For more information on Red Hat Technology Preview features, see
[Technology Preview Features
Scope](https://access.redhat.com/support/offerings/techpreview/).

Additional detail on how Red Hat provides support for bundled community
dynamic plugins is available on the [Red Hat Developer Support
Policy](https://access.redhat.com/policy/developerhub-support-policy)
page.
::::

To use the Ansible plugins, see [*Using Ansible plug-ins for Red Hat
Developer
Hub*](https://docs.redhat.com/en/documentation/red_hat_ansible_automation_platform/2.4/html/using_ansible_plug-ins_for_red_hat_developer_hub/index).

## Using the Argo CD plugin {#_using-the-argo-cd-plugin}

You can use the Argo CD plugin to visualize the Continuous Delivery (CD)
workflows in OpenShift GitOps. This plugin provides a visual overview of
the application's status, deployment details, commit message, author of
the commit, container image promoted to environment and deployment
history.

<div>

::: title
Prerequisites
:::

- You have enabled the Argo CD plugin in Red Hat Developer Hub RHDH.

</div>

<div>

::: title
Procedures
:::

1.  Select the **Catalog** tab and choose the component that you want to
    use.

2.  Select the **CD** tab to view insights into deployments managed by
    Argo CD.

    ![CD tab Argo CD](images/rhdh-plugins-reference/argocd.png)

3.  Select an appropriate card to view the deployment details (for
    example, commit message, author name, and deployment history).

    ![Sidebar](images/rhdh-plugins-reference/sidebar.png)

    a.  Click the link icon (![Link
        icon](images/rhdh-plugins-reference/link.png)) to open the
        deployment details in Argo CD.

4.  Select the **Overview** tab and navigate to the Deployment summary
    section to review the summary of your application's deployment
    across namespaces. Additionally, select an appropriate Argo CD app
    to open the deployment details in Argo CD, or select a commit ID
    from the Revision column to review the changes in GitLab or GitHub.

    ![Deployment
    summary](images/rhdh-plugins-reference/deployment_summary.png)

</div>

<div>

::: title
Additional resources
:::

- For more information on installing dynamic plugins, see [Installing
  and viewing plugins in Red Hat Developer
  Hub](https://docs.redhat.com/en/documentation/red_hat_developer_hub/1.6/html-single/installing_and_viewing_plugins_in_red_hat_developer_hub/index).

</div>

## Using the JFrog Artifactory plugin {#using-jfrog-artifactory_title-plugins-rhdh-using}

The JFrog Artifactory plugin displays information about your container
images within the Jfrog Artifactory registry.

:::: important
::: title
:::

The JFrog Artifactory plugin is a Technology Preview feature only.

Technology Preview features are not supported with Red Hat production
service level agreements (SLAs), might not be functionally complete, and
Red Hat does not recommend using them for production. These features
provide early access to upcoming product features, enabling customers to
test functionality and provide feedback during the development process.

For more information on Red Hat Technology Preview features, see
[Technology Preview Features
Scope](https://access.redhat.com/support/offerings/techpreview/).

Additional detail on how Red Hat provides support for bundled community
dynamic plugins is available on the [Red Hat Developer Support
Policy](https://access.redhat.com/policy/developerhub-support-policy)
page.
::::

<div>

::: title
Prerequisites
:::

- Your Developer Hub application is installed and running.

- You have enabled the JFrog Artifactory plugin.

</div>

<div>

::: title
Procedure
:::

1.  Open your Developer Hub application and select a component from the
    **Catalog** page.

2.  Go to the **Image Registry** tab.

    The **Image Registry** tab contains a list of container images
    within your Jfrog Artifactory repository and related information,
    such as **Version**, **Repositories**, **Manifest**, **Modified**,
    and **Size**.

    ![image-registry-tab-jfrog-artifactory](images/rhdh-plugins-reference/jfrog-artifactory.png)

</div>

## Using Keycloak {#rhdh-keycloak_title-plugins-rhdh-using}

The Keycloak backend plugin, which integrates Keycloak into Developer
Hub, has the following capabilities:

- Synchronization of Keycloak users in a realm.

- Synchronization of Keycloak groups and their users in a realm.

### Importing users and groups in Developer Hub using the Keycloak plugin {#_importing-users-and-groups-in-developer-hub-using-the-keycloak-plugin}

After configuring the plugin successfully, the plugin imports the users
and groups each time when started.

:::: note
::: title
:::

If you set up a schedule, users and groups will also be imported.
::::

<div>

::: title
Procedure
:::

1.  in Red Hat Developer Hub, go to the **Catalog** page.

2.  Select **User** from the entity type filter to display the list of
    imported users.

3.  Browse the list of users displayed on the page.

4.  Select a user to view detailed information imported from Keycloak.

5.  To view groups, select **Group** from the entity type filter.

6.  Browse the list of groups shown on the page.

7.  From the list of groups, select a group to view the information
    imported from Keycloak.

</div>

## Using the Nexus Repository Manager plugin {#_using-the-nexus-repository-manager-plugin}

The Nexus Repository Manager plugin displays the information about your
build artifacts in your Developer Hub application. The build artifacts
are available in the Nexus Repository Manager.

:::: important
::: title
:::

The Nexus Repository Manager plugin is a Technology Preview feature
only.

Technology Preview features are not supported with Red Hat production
service level agreements (SLAs), might not be functionally complete, and
Red Hat does not recommend using them for production. These features
provide early access to upcoming product features, enabling customers to
test functionality and provide feedback during the development process.

For more information on Red Hat Technology Preview features, see
[Technology Preview Features
Scope](https://access.redhat.com/support/offerings/techpreview/).

Additional detail on how Red Hat provides support for bundled community
dynamic plugins is available on the [Red Hat Developer Support
Policy](https://access.redhat.com/policy/developerhub-support-policy)
page.
::::

The Nexus Repository Manager is a front-end plugin that enables you to
view the information about build artifacts.

<div>

::: title
Prerequisites
:::

- Your Developer Hub application is installed and running.

- You have installed the Nexus Repository Manager plugin.

</div>

<div>

::: title
Procedure
:::

1.  Open your Developer Hub application and select a component from the
    **Catalog** page.

2.  Go to the **BUILD ARTIFACTS** tab.

    The **BUILD ARTIFACTS** tab contains a list of build artifacts and
    related information, such as **VERSION**, **REPOSITORY**,
    **REPOSITORY TYPE**, **MANIFEST**, **MODIFIED**, and **SIZE**.

    ![nexus-repository-manager-tab](images/rhdh-plugins-reference/nexus-repository-manager.png)

</div>

## Using the Tekton plugin {#installation-and-configuration-tekton}

You can use the Tekton plugin to visualize the results of CI/CD pipeline
runs on your Kubernetes or OpenShift clusters. The plugin allows users
to visually see high level status of all associated tasks in the
pipeline for their applications.

You can use the Tekton front-end plugin to view `PipelineRun` resources.

<div>

::: title
Prerequisites
:::

- You have installed the Red Hat Developer Hub (RHDH).

- You have installed the Tekton plugin. For the installation process,
  see [Installing and configuring the Tekton
  plugin](#installation-and-configuration-tekton).

</div>

<div>

::: title
Procedure
:::

1.  Open your RHDH application and select a component from the
    **Catalog** page.

2.  Go to the **CI** tab.

    The **CI** tab displays the list of PipelineRun resources associated
    with a Kubernetes cluster. The list contains pipeline run details,
    such as **NAME**, **VULNERABILITIES**, **STATUS**, **TASK STATUS**,
    **STARTED**, and **DURATION**.

    ![ci-cd-tab-tekton](images/rhdh-plugins-reference/tekton-plugin-pipeline.png)

3.  Click the expand row button besides PipelineRun name in the list to
    view the PipelineRun visualization. The pipeline run resource
    includes tasks to complete. When you hover the mouse pointer on a
    task card, you can view the steps to complete that particular task.

    ![ci-cd-tab-tekton](images/rhdh-plugins-reference/tekton-plugin-pipeline-expand.png)

</div>

## Using the Topology plugin {#using-topology-plugin}

Topology is a front-end plugin that enables you to view the workloads as
nodes that power any service on the Kubernetes cluster.

### Enable users to use the Topology plugin

The Topology plugin is defining additional permissions. When
[Authorization in Red Hat Developer
Hub](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/authorization_in_red_hat_developer_hub/index)
is enabled, to enable users to use the Topology plugin, grant them:

- The `kubernetes.clusters.read` and `kubernetes.resources.read`, `read`
  permissions to view the Topology panel.

- The `kubernetes.proxy` `use` permission to view the pod logs.

- The `catalog-entity` `read` permission to view the Red Hat Developer
  Hub software catalog items.

<div>

::: title
Prerequisites
:::

- You are [managing Authorization in Red Hat Developer Hub by using
  external
  files](https://docs.redhat.com/documentation/en-us/red_hat_developer_hub/1.6/html-single/authorization_in_red_hat_developer_hub/index#managing-authorizations-by-using-external-files).

</div>

<div>

::: title
Procedure
:::

- Add the following permission policies to your `rbac-policy.csv` file
  to create a `topology-viewer` role that has access to the Topology
  plugin features, and add the role to the users requiring this
  authorization:

      g, user:default/<YOUR_USERNAME>, role:default/topology-viewer
      p, role:default/topology-viewer, kubernetes.clusters.read, read, allow
      p, role:default/topology-viewer, kubernetes.resources.read, read, allow
      p, role:default/topology-viewer, kubernetes.proxy, use, allow
      p, role:default/topology-viewer, catalog-entity, read, allow

  - Grants the user the ability to see the Topology panel.

  - Grants the user the ability to view the pod logs.

  - Grants the user the ability to see the catalog item.

</div>

### Using the Topology plugin {#using-the-topology-plugin}

<div>

::: title
Prerequisites
:::

- Your Red Hat Developer Hub instance is installed and running.

- You have installed the Topology plugin.

- You have [enabled the users to use the Topology
  plugin](#enable-users-to-use-the-topology-plugin).

</div>

<div>

::: title
Procedure
:::

1.  Open your RHDH application and select a component from the
    **Catalog** page.

2.  Go to the **TOPOLOGY** tab and you can view the workloads such as
    deployments or pods as nodes.

    ![topology-user-1](images/rhdh-plugins-reference/topology-tab-user1.png)

3.  Select a node and a pop-up appears on the right side that contains
    two tabs: **Details** and **Resources**.

    The **Details** and **Resources** tabs contain the associated
    information and resources for the node.

    ![topology-user-2](images/rhdh-plugins-reference/topology-tab-user2.png)

4.  Click the **Open URL** button on the top of a node.

    ![topology-user-3](images/rhdh-plugins-reference/topology-tab-user3.png)

    Click the **Open URL** button to access the associated **Ingresses**
    and run your application in a new tab.

</div>
