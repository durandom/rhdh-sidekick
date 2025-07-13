## Plugins in Red Hat Developer Hub {#con-rhdh-plugins}

The Red Hat Developer Hub (RHDH) application offers a unified platform
with various plugins. Using the plugin ecosystem within the RHDH
application, you can access any kind of development infrastructure or
software development tool.

Plugins are modular extensions for RHDH that extend functionality,
streamline development workflows, and improve the developer experience.
You can add and configure plugins in RHDH to access various software
development tools.

Each plugin is designed as a self-contained application and can
incorporate any type of content. The plugins utilize a shared set of
platform APIs and reusable UI components. Plugins can also retrieve data
from external sources through APIs or by relying on external modules to
perform the tasks.

RHDH provides both static and dynamic plugins that enhance its
functionality. Static plugins are integrated into the core of the RHDH
application, while dynamic plugins can be sideloaded into your Developer
Hub instance without the need to recompile your code or rebuild the
container.

To install or update a static plugin you must update your RHDH
application source code and rebuild the application and container image.

To install or update a dynamic plugin, you must restart your RHDH
application source code after installing the plugin.

You can also import your own custom-built or third-party plugins or
create new features using dynamic plugins.

Dynamic plugins boost modularity and scalability by enabling more
flexible and efficient functionality loading, significantly enhancing
the developer experience and customization of your RHDH instance.

### Dynamic plugins in Red Hat Developer Hub {#_dynamic-plugins-in-red-hat-developer-hub}

You can use RHDH dynamic plugins in environments where flexibility,
scalability, and customization are key. Using dynamic plugins in RHDH
provides:

Modularity and extensibility

:   You can add or modify features without altering the core RHDH
    application. This modular approach makes it easier to extend
    functionality as needs evolve.

Customization

:   You can tailor RHDH to fit specific workflows and use cases,
    enhancing the overall user experience.

Reduced maintenance and update overhead

:   You can deploy the updates or new features independently of the main
    RHDH codebase, reducing the risks and efforts associated with
    maintaining and updating the platform.

Faster iteration

:   You can create and test new features more rapidly as plugins,
    encouraging experimentation and enabling you to quickly iterate
    based on feedback.

Improved collaboration

:   You can share plugins across teams or even externally. This sharing
    can foster collaboration and reduce duplication of effort, as well
    as help establish best practices across an organization.

Scalability

:   As organizations grow, their needs become complex. Dynamic plugins
    enable RHDH to scale alongside such complex needs, accommodating an
    increasing number of users and services.

Ecosystem growth

:   Fostering the development of plugins can create a dynamic ecosystem
    around RHDH. This community can contribute to plugins that cater to
    different needs, thereby enhancing the platform.

Security and compliance

:   You can develop plugins with specific security and compliance
    requirements in mind, ensuring that RHDH installations meet the
    necessary standards without compromising the core application.

Overall, the use of dynamic plugins in RHDH promotes a flexible,
adaptable, and sustainable approach to managing and scaling development
infrastructure.

### Comparing dynamic plugins to static plugins {#_comparing-dynamic-plugins-to-static-plugins}

Static plugins are built into the core of the RHDH application.
Installing or updating a static plugin requires a restart of the
application after installing the plugin.

The following table provides a comparison between static and dynamic
plugins in RHDH.

+----------------------+----------------------+-----------------------+
| **Feature**          | **Static plugins**   | **Dynamic plugins**   |
+======================+======================+=======================+
| Integration          | Built into the core  | Loaded at runtime,    |
|                      | application.         | separate from the     |
|                      |                      | core.                 |
+----------------------+----------------------+-----------------------+
| Flexibility          | Requires core        | Add or update         |
|                      | changes to add or    | features without core |
|                      | update features.     | changes.              |
+----------------------+----------------------+-----------------------+
| Development speed    | Slower, requires a   | Faster, deploy new    |
|                      | complete rebuild for | functionalities       |
|                      | new features.        | quickly.              |
+----------------------+----------------------+-----------------------+
| Customization        | Limited to           | Easy to tailor        |
|                      | predefined options.  | platform by loading   |
|                      |                      | specific plugins.     |
+----------------------+----------------------+-----------------------+
| Maintenance          | More complex due to  | Enhanced by modular   |
|                      | tightly coupled      | architecture.         |
|                      | features.            |                       |
+----------------------+----------------------+-----------------------+
| Resource use         | All features loaded  | Only necessary        |
|                      | at startup.          | plugins loaded        |
|                      |                      | dynamically.          |
+----------------------+----------------------+-----------------------+
| Innovation           | Slower               | Quick experimentation |
|                      | experimentation due  | with new plugins.     |
|                      | to rebuild cycles.   |                       |
+----------------------+----------------------+-----------------------+
