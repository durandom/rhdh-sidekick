You can install Red Hat Developer Hub on Amazon Elastic Kubernetes
Service (EKS) using one of the following methods:

- The Red Hat Developer Hub Operator

- The Red Hat Developer Hub Helm chart

## Installing Developer Hub on EKS with the Operator {#assembly-install-rhdh-eks-operator}

The Red Hat Developer Hub Operator installation requires the Operator
Lifecycle Manager (OLM) framework.

<div>

::: title
Additional resources
:::

- For information about the OLM, see [Operator Lifecycle
  Manager(OLM)](https://olm.operatorframework.io/docs/) documentation.

</div>

### Installing the Developer Hub Operator with the OLM framework {#proc-rhdh-deploy-eks-operator_title-install-rhdh-eks}

You can install the Developer Hub Operator on EKS using the [Operator
Lifecycle Manager (OLM) framework](https://olm.operatorframework.io).
Following that, you can proceed to deploy your Developer Hub instance in
EKS.

<div>

::: title
Prerequisites
:::

- You have set the context to the EKS cluster in your current
  `kubeconfig`. For more information, see [Creating or updating a
  kubeconfig file for an Amazon EKS
  cluster](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html).

- You have installed `kubectl`. For more information, see [Installing or
  updating
  kubectl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html).

- You have subscribed to `registry.redhat.io`. For more information, see
  [Red Hat Container Registry
  Authentication](https://access.redhat.com/RegistryAuthentication).

- You have installed the Operator Lifecycle Manager (OLM). For more
  information about installation and troubleshooting, see [OLM
  QuickStart](https://olm.operatorframework.io/docs/getting-started/) or
  [How do I get Operator Lifecycle
  Manager?](https://operatorhub.io/how-to-install-an-operator#How-do-I-get-Operator-Lifecycle-Manager?)

</div>

<div>

::: title
Procedure
:::

1.  Run the following command in your terminal to create the
    `rhdh-operator` namespace where the Operator is installed:

    ``` terminal
    kubectl create namespace rhdh-operator
    ```

2.  Create a pull secret using the following command:

    ``` terminal
    kubectl -n rhdh-operator create secret docker-registry rhdh-pull-secret \
        --docker-server=registry.redhat.io \
        --docker-username=<user_name> \
        --docker-password=<password> \
        --docker-email=<email>
    ```

    - Enter your username in the command.

    - Enter your password in the command.

    - Enter your email address in the command.

    The created pull secret is used to pull the Developer Hub images
    from the Red Hat Ecosystem.

3.  Create a `CatalogSource` resource that contains the Operators from
    the Red Hat Ecosystem:

    ``` terminal
    cat <<EOF | kubectl -n rhdh-operator apply -f -
    apiVersion: operators.coreos.com/v1alpha1
    kind: CatalogSource
    metadata:
      name: redhat-catalog
    spec:
      sourceType: grpc
      image: registry.redhat.io/redhat/redhat-operator-index:v4.18
      secrets:
      - "rhdh-pull-secret"
      displayName: Red Hat Operators
    EOF
    ```

4.  Create an `OperatorGroup` resource as follows:

    ``` terminal
    cat <<EOF | kubectl apply -n rhdh-operator -f -
    apiVersion: operators.coreos.com/v1
    kind: OperatorGroup
    metadata:
      name: rhdh-operator-group
    EOF
    ```

5.  Create a `Subscription` resource using the following code:

    ``` terminal
    cat <<EOF | kubectl apply -n rhdh-operator -f -
    apiVersion: operators.coreos.com/v1alpha1
    kind: Subscription
    metadata:
      name: rhdh
      namespace: rhdh-operator
    spec:
      channel: fast
      installPlanApproval: Automatic
      name: rhdh
      source: redhat-catalog
      sourceNamespace: rhdh-operator
      startingCSV: rhdh-operator.v1.6.0
    EOF
    ```

6.  Run the following command to verify that the created Operator is
    running:

    ``` terminal
    kubectl -n rhdh-operator get pods -w
    ```

    If the operator pod shows `ImagePullBackOff` status, then you might
    need permissions to pull the image directly within the Operator
    deployment's manifest.

    :::: tip
    ::: title
    :::

    You can include the required secret name in the
    `deployment.spec.template.spec.imagePullSecrets` list and verify the
    deployment name using `kubectl get deployment -n rhdh-operator`
    command:

    ``` terminal
    kubectl -n rhdh-operator patch deployment \
        rhdh.fast --patch '{"spec":{"template":{"spec":{"imagePullSecrets":[{"name":"rhdh-pull-secret"}]}}}}' \
        --type=merge
    ```
    ::::

7.  Update the default configuration of the operator to ensure that
    Developer Hub resources can start correctly in EKS using the
    following steps:

    a.  Edit the `backstage-default-config` ConfigMap in the
        `rhdh-operator` namespace using the following command:

        ``` terminal
        kubectl -n rhdh-operator edit configmap backstage-default-config
        ```

    b.  Locate the `db-statefulset.yaml` string and add the `fsGroup` to
        its `spec.template.spec.securityContext`, as shown in the
        following example:

        ``` yaml
          db-statefulset.yaml: |
            apiVersion: apps/v1
            kind: StatefulSet
        --- TRUNCATED ---
            spec:
            --- TRUNCATED ---
              restartPolicy: Always
              securityContext:
              # You can assign any random value as fsGroup
                fsGroup: 2000
              serviceAccount: default
              serviceAccountName: default
        --- TRUNCATED ---
        ```

    c.  Locate the `deployment.yaml` string and add the `fsGroup` to its
        specification, as shown in the following example:

        ``` yaml
          deployment.yaml: |
            apiVersion: apps/v1
            kind: Deployment
        --- TRUNCATED ---
            spec:
              securityContext:
                # You can assign any random value as fsGroup
                fsGroup: 3000
              automountServiceAccountToken: false
        --- TRUNCATED ---
        ```

    d.  Locate the `service.yaml` string and change the `type` to
        `NodePort` as follows:

        ``` yaml
          service.yaml: |
            apiVersion: v1
            kind: Service
            spec:
             # NodePort is required for the ALB to route to the Service
              type: NodePort
        --- TRUNCATED ---
        ```

    e.  Save and exit.

        Wait for a few minutes until the changes are automatically
        applied to the operator pods.

</div>

### Deploying the Developer Hub instance on EKS with the Operator {#proc-deploy-rhdh-instance-eks.adoc_title-install-rhdh-eks}

<div>

::: title
Prerequisites
:::

- A cluster administrator has installed the Red Hat Developer Hub
  Operator.

- You have an EKS cluster with AWS Application Load Balancer (ALB)
  add-on installed. For more information, see [Application load
  balancing on Amazon Elastic Kubernetes
  Service](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html)
  and [Installing the AWS Load Balancer Controller
  add-on](https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html).

- You have configured a domain name for your Developer Hub instance. The
  domain name can be a hosted zone entry on Route 53 or managed outside
  of AWS. For more information, see [Configuring Amazon Route 53 as your
  DNS
  service](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring.html)
  documentation.

- You have an entry in the AWS Certificate Manager (ACM) for your
  preferred domain name. Make sure to keep a record of your Certificate
  ARN.

- You have subscribed to `registry.redhat.io`. For more information, see
  [Red Hat Container Registry
  Authentication](https://access.redhat.com/RegistryAuthentication).

- You have set the context to the EKS cluster in your current
  `kubeconfig`. For more information, see [Creating or updating a
  kubeconfig file for an Amazon EKS
  cluster](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html).

- You have installed `kubectl`. For more information, see [Installing or
  updating
  kubectl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html).

</div>

<div>

::: title
Procedure
:::

1.  Create a `my-rhdh-app-config` config map containing the
    `app-config.yaml` Developer Hub configuration file by using the
    following template:

    ``` yaml
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: my-rhdh-app-config
    data:
      "app-config.yaml": |
        app:
          title: Red Hat Developer Hub
          baseUrl: https://<rhdh_dns_name>
        backend:
          auth:
            externalAccess:
                - type: legacy
                  options:
                    subject: legacy-default-config
                    secret: "${BACKEND_SECRET}"
          baseUrl: https://<rhdh_dns_name>
          cors:
            origin: https://<rhdh_dns_name>
    ```

2.  Create a Red Hat Developer Hub secret and add a key named
    `BACKEND_SECRET` with a `Base64-encoded` string as value:

    ``` yaml
    apiVersion: v1
    kind: Secret
    metadata:
      name: <my_product_secrets>
    stringData:
      # TODO: See https://backstage.io/docs/auth/service-to-service-auth/#setup
      BACKEND_SECRET: "xxx"
    ```

    - `<my_product_secrets>` is your preferred Developer Hub secret
      name, where `<my_product_secrets>` specifies the unique identifier
      for your secret configuration within Developer Hub.

    :::: important
    ::: title
    :::

    Ensure that you use a unique value of `BACKEND_SECRET` for each
    Developer Hub instance.
    ::::

    You can use the following command to generate a key:

    ``` terminal
    node-p'require("crypto").randomBytes(24).toString("base64")'
    ```

3.  To enable pulling the PostgreSQL image from the Red Hat Ecosystem
    Catalog, add the image pull secret in the default service account
    within the namespace where the Developer Hub instance is being
    deployed:

    ``` terminal
    kubectl patch serviceaccount default \
        -p '{"imagePullSecrets": [{"name": "rhdh-pull-secret"}]}' \
        -n <your_namespace>
    ```

4.  Create your `Backstage` custom resource using the following
    template:

    ``` yaml
    apiVersion: rhdh.redhat.com/v1alpha3
    kind: Backstage
    metadata:
     # TODO: this the name of your Developer Hub instance
      name: my-rhdh
    spec:
      application:
        imagePullSecrets:
        - "rhdh-pull-secret"
        route:
          enabled: false
        appConfig:
          configMaps:
            - name: my-rhdh-app-config
        extraEnvs:
          secrets:
            - name: <my_product_secrets>
    ```

    - `<my_product_secrets>` is your preferred Developer Hub secret
      name, where `<my_product_secrets>` specifies the identifier for
      your secret configuration within Developer Hub.

5.  Create an Ingress resource using the following template, ensuring to
    customize the names as needed:

    ``` yaml
    apiVersion: networking.k8s.io/v1
    kind: Ingress
    metadata:
      # TODO: this the name of your Developer Hub Ingress
      name: my-rhdh
      annotations:
        alb.ingress.kubernetes.io/scheme: internet-facing

        alb.ingress.kubernetes.io/target-type: ip

        # TODO: Using an ALB HTTPS Listener requires a certificate for your own domain. Fill in the ARN of your certificate, e.g.:
        alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-xxx:xxxx:certificate/xxxxxx

         alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'

        alb.ingress.kubernetes.io/ssl-redirect: '443'

        # TODO: Set your application domain name.
        external-dns.alpha.kubernetes.io/hostname: <rhdh_dns_name>

    spec:
      ingressClassName: alb
      rules:
        # TODO: Set your application domain name.
        - host: <rhdh_dns_name>
          http:
            paths:
            - path: /
              pathType: Prefix
              backend:
                service:
                  # TODO: my-rhdh is the name of your `Backstage` custom resource.
                  # Adjust if you changed it!
                  name: backstage-my-rhdh
                  port:
                    name: http-backend
    ```

    In the previous template, replace \` \<rhdh_dns_name\>\` with your
    Developer Hub domain name and update the value of
    `alb.ingress.kubernetes.io/certificate-arn` with your certificate
    ARN.

</div>

:::: formalpara
::: title
Verification
:::

Wait until the DNS name is responsive, indicating that your Developer
Hub instance is ready for use.
::::

## Installing Developer Hub on EKS with the Helm chart {#proc-rhdh-deploy-eks-helm_title-install-rhdh-eks}

When you install the Developer Hub Helm chart in Elastic Kubernetes
Service (EKS), it orchestrates the deployment of a Developer Hub
instance, which provides a robust developer platform within the AWS
ecosystem.

<div>

::: title
Prerequisites
:::

- You have an EKS cluster with AWS Application Load Balancer (ALB)
  add-on installed. For more information, see [Application load
  balancing on Amazon Developer
  Hub](https://docs.aws.amazon.com/eks/latest/userguide/alb-ingress.html)
  and [Installing the AWS Load Balancer Controller
  add-on](https://docs.aws.amazon.com/eks/latest/userguide/aws-load-balancer-controller.html).

- You have configured a domain name for your Developer Hub instance. The
  domain name can be a hosted zone entry on Route 53 or managed outside
  of AWS. For more information, see [Configuring Amazon Route 53 as your
  DNS
  service](https://docs.aws.amazon.com/Route53/latest/DeveloperGuide/dns-configuring.html)
  documentation.

- You have an entry in the AWS Certificate Manager (ACM) for your
  preferred domain name. Make sure to keep a record of your Certificate
  ARN.

- You have subscribed to `registry.redhat.io`. For more information, see
  [Red Hat Container Registry
  Authentication](https://access.redhat.com/RegistryAuthentication).

- You have set the context to the EKS cluster in your current
  `kubeconfig`. For more information, see [Creating or updating a
  kubeconfig file for an Amazon EKS
  cluster](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html).

- You have installed `kubectl`. For more information, see [Installing or
  updating
  kubectl](https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html).

- You have installed Helm 3 or the latest. For more information, see
  [Using Helm with Amazon
  EKS](https://docs.aws.amazon.com/eks/latest/userguide/helm.html).

</div>

<div>

::: title
Procedure
:::

1.  Go to your terminal and run the following command to add the Helm
    chart repository containing the Developer Hub chart to your local
    Helm registry:

    ``` terminal
    helm repo add openshift-helm-charts https://charts.openshift.io/
    ```

2.  Create a pull secret using the following command:

    ``` terminal
    kubectl create secret docker-registry rhdh-pull-secret \
        --docker-server=registry.redhat.io \
        --docker-username=<user_name> \
        --docker-password=<password> \
        --docker-email=<email>
    ```

    - Enter your username in the command.

    - Enter your password in the command.

    - Enter your email address in the command.

    The created pull secret is used to pull the Developer Hub images
    from the Red Hat Ecosystem.

3.  Create a file named `values.yaml` using the following template:

    ``` yaml
    global:
      # TODO: Set your application domain name.
      host: <your Developer Hub domain name>


    route:
      enabled: false


    upstream:
      service:
        # NodePort is required for the ALB to route to the Service
        type: NodePort


      ingress:
        enabled: true
        annotations:
          kubernetes.io/ingress.class: alb


          alb.ingress.kubernetes.io/scheme: internet-facing


          # TODO: Using an ALB HTTPS Listener requires a certificate for your own domain. Fill in the ARN of your certificate, e.g.:
          alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:xxx:xxxx:certificate/xxxxxx


          alb.ingress.kubernetes.io/listen-ports: '[{"HTTP": 80}, {"HTTPS":443}]'


          alb.ingress.kubernetes.io/ssl-redirect: '443'


          # TODO: Set your application domain name.
          external-dns.alpha.kubernetes.io/hostname: <your rhdh domain name>


      backstage:
        image:
          pullSecrets:
          - rhdh-pull-secret
        podSecurityContext:
          # you can assign any random value as fsGroup
          fsGroup: 2000
      postgresql:
        image:
          pullSecrets:
          - rhdh-pull-secret
        primary:
          podSecurityContext:
            enabled: true
            # you can assign any random value as fsGroup
            fsGroup: 3000
      volumePermissions:
        enabled: true
    ```

4.  Run the following command in your terminal to deploy Developer Hub
    using the latest version of Helm Chart and using the values.yaml
    file created in the previous step:

    ``` terminal
    helm install rhdh \
      openshift-helm-charts/redhat-developer-hub \
      [--version 1.6.0] \
      --values /path/to/values.yaml
    ```

</div>

:::: note
::: title
:::

For the latest chart version, see
<https://github.com/openshift-helm-charts/charts/tree/main/charts/redhat/redhat/redhat-developer-hub>
::::

:::: formalpara
::: title
Verification
:::

Wait until the DNS name is responsive, indicating that your Developer
Hub instance is ready for use.
::::
