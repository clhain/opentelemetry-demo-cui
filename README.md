<!-- markdownlint-disable-next-line -->
# <img src="https://opentelemetry.io/img/logos/opentelemetry-logo-nav.png" alt="OTel logo" width="45"> OpenTelemetry Demo With Critical User Interactions

## Background
This is a fork of the opentelemetry-demo which implements "Critical User Interactions",
a technique [published by Google](https://www.tdcommons.org/dpubs_series/6283/) for
helping address common challenges with large-scale distributed systems.

In this fork:

1. Baggage propagation has been added (hastily, not intended as a reference implementation) to all services used in the
  minimal version (docker-compose.minimal.yml).
2. The compose file was refactored to start 2 instances of the frontend service (red shop and
  blue shop), representing tenants in an ecommerce platform.
3. Critical User Interactions (e.g. RED_SHOP/BROWSE, BLUE_SHOP/CHECKOUT) are added to baggage
  headers in the frontend and load generator.
4. Grafana [PromQL Anomaly Detection](https://github.com/grafana/promql-anomaly-detection) rules added
  for all service graph metrics (with and without the critical user interaction dimension)
5. Quick demo dashboards and flagd variable to introduce latency to specific CUIs added.

The basic narrative is:

1. Service graph based metrics and automated anomaly detection are awesome.
2. They sometimes miss more obscure problems, and can be hard for operators to reason about.
3. By adding CUI as a dimension to these metrics, you can set better baselines and make it easier for operators
  to quickly identify "what's broken" in simple terms.

To run the demo:

```
docker compose -f docker-compose.minimal.yml up -d
```
* <wait ~10-20 minutes to allow baselines to establish (or longer for better accuracy)>
* visit http://localhost:8080/feature and enable productCatalogLatency for RED_SHOP.CHECKOUT
* <wait ~3 minutes for the anomaly detection to pick up the issue>
* visit http://localhost:8080/grafana
  * Show the Anomalies dashboard with:
    * ProductCUI=All, Server=ProductCatalog, Client=checkout, anomaly_name='latency_p50' - no problem detected
  * Then show:
    * ProductCUI=RED_SHOP.CHECKOUT, Server=ProductCatalog, Client=checkout, anomaly_name='latency_p50_with_cui' - big problem detected
  * Switch to the Service Graph dashboard:
    * Show CUI=All, Type=latency_p50 - no problems detected, large service graph
    * Show CUI=All, Type=latency_p50_with_cui - problems detected with RED_SHOP.CHECKOUT in upper right table, easily identifyable
    * Show CUI=RED_SHOP.CHECKOUT, Type=latency_p50_with_cui - problems accurately highlighted for this flow, only services in this flow displayed
    * Show CUI=BLUE_SHOP.CHECKOUT, Type=latency_p50_with_cui - no problems detected (correctly), only blue shop services in this flow displayed

The remainder of this Readme is from the upstream project.

## Welcome to the OpenTelemetry Astronomy Shop Demo

This repository contains the OpenTelemetry Astronomy Shop, a microservice-based
distributed system intended to illustrate the implementation of OpenTelemetry in
a near real-world environment.

Our goals are threefold:

- Provide a realistic example of a distributed system that can be used to
  demonstrate OpenTelemetry instrumentation and observability.
- Build a base for vendors, tooling authors, and others to extend and
  demonstrate their OpenTelemetry integrations.
- Create a living example for OpenTelemetry contributors to use for testing new
  versions of the API, SDK, and other components or enhancements.

We've already made [huge
progress](https://github.com/open-telemetry/opentelemetry-demo/blob/main/CHANGELOG.md),
and development is ongoing. We hope to represent the full feature set of
OpenTelemetry across its languages in the future.

If you'd like to help (**which we would love**), check out our [contributing
guidance](./CONTRIBUTING.md).

If you'd like to extend this demo or maintain a fork of it, read our
[fork guidance](https://opentelemetry.io/docs/demo/forking/).

## Quick start

You can be up and running with the demo in a few minutes. Check out the docs for
your preferred deployment method:

- [Docker](https://opentelemetry.io/docs/demo/docker_deployment/)
- [Kubernetes](https://opentelemetry.io/docs/demo/kubernetes_deployment/)

## Documentation

For detailed documentation, see [Demo Documentation][docs]. If you're curious
about a specific feature, the [docs landing page][docs] can point you in the
right direction.

## Demos featuring the Astronomy Shop

We welcome any vendor to fork the project to demonstrate their services and
adding a link below. The community is committed to maintaining the project and
keeping it up to date for you.

|                           |                |                                  |
|---------------------------|----------------|----------------------------------|
| [AlibabaCloud LogService] | [Elastic]      | [OpenSearch]                     |
| [AppDynamics]             | [Google Cloud] | [Oracle]                         |
| [Aspecto]                 | [Grafana Labs] | [Sentry]                         |
| [Axiom]                   | [Guance]       | [ServiceNow Cloud Observability] |
| [Axoflow]                 | [Honeycomb.io] | [Splunk]                         |
| [Azure Data Explorer]     | [Instana]      | [Sumo Logic]                     |
| [Coralogix]               | [Kloudfuse]    | [TelemetryHub]                   |
| [Dash0]                   | [Liatrio]      | [Teletrace]                      |
| [Datadog]                 | [Logz.io]      | [Tracetest]                      |
| [Dynatrace]               | [New Relic]    | [Uptrace]                        |

## Contributing

To get involved with the project see our [CONTRIBUTING](CONTRIBUTING.md)
documentation. Our [SIG Calls](CONTRIBUTING.md#join-a-sig-call) are every other
Wednesday at 8:30 AM PST and anyone is welcome.

## Project leadership

[Maintainers](https://github.com/open-telemetry/community/blob/main/guides/contributor/membership.md#maintainer)
([@open-telemetry/demo-maintainers](https://github.com/orgs/open-telemetry/teams/demo-maintainers)):

- [Juliano Costa](https://github.com/julianocosta89), Datadog
- [Mikko Viitanen](https://github.com/mviitane), Dynatrace
- [Pierre Tessier](https://github.com/puckpuck), Honeycomb

[Approvers](https://github.com/open-telemetry/community/blob/main/guides/contributor/membership.md#approver)
([@open-telemetry/demo-approvers](https://github.com/orgs/open-telemetry/teams/demo-approvers)):

- [Cedric Ziel](https://github.com/cedricziel) Grafana Labs
- [Penghan Wang](https://github.com/wph95), AppDynamics
- [Reiley Yang](https://github.com/reyang), Microsoft
- [Roger Coll](https://github.com/rogercoll), Elastic
- [Ziqi Zhao](https://github.com/fatsheep9146), Alibaba

Emeritus:

- [Austin Parker](https://github.com/austinlparker)
- [Carter Socha](https://github.com/cartersocha)
- [Michael Maxwell](https://github.com/mic-max)
- [Morgan McLean](https://github.com/mtwo)

### Thanks to all the people who have contributed

[![contributors](https://contributors-img.web.app/image?repo=open-telemetry/opentelemetry-demo)](https://github.com/open-telemetry/opentelemetry-demo/graphs/contributors)

[docs]: https://opentelemetry.io/docs/demo/

<!-- Links for Demos featuring the Astronomy Shop section -->

[AlibabaCloud LogService]: https://github.com/aliyun-sls/opentelemetry-demo
[AppDynamics]: https://community.appdynamics.com/t5/Knowledge-Base/How-to-observe-OpenTelemetry-demo-app-in-Splunk-AppDynamics/ta-p/58584
[Aspecto]: https://github.com/aspecto-io/opentelemetry-demo
[Axiom]: https://play.axiom.co/axiom-play-qf1k/dashboards/otel.traces.otel-demo-traces
[Axoflow]: https://axoflow.com/opentelemetry-support-in-more-detail-in-axosyslog-and-syslog-ng/
[Azure Data Explorer]: https://github.com/Azure/Azure-kusto-opentelemetry-demo
[Coralogix]: https://coralogix.com/blog/configure-otel-demo-send-telemetry-data-coralogix
[Dash0]: https://github.com/dash0hq/opentelemetry-demo
[Datadog]: https://docs.datadoghq.com/opentelemetry/guide/otel_demo_to_datadog
[Dynatrace]: https://www.dynatrace.com/news/blog/opentelemetry-demo-application-with-dynatrace/
[Elastic]: https://github.com/elastic/opentelemetry-demo
[Google Cloud]: https://github.com/GoogleCloudPlatform/opentelemetry-demo
[Grafana Labs]: https://github.com/grafana/opentelemetry-demo
[Guance]: https://github.com/GuanceCloud/opentelemetry-demo
[Honeycomb.io]: https://github.com/honeycombio/opentelemetry-demo
[Instana]: https://github.com/instana/opentelemetry-demo
[Kloudfuse]: https://github.com/kloudfuse/opentelemetry-demo
[Liatrio]: https://github.com/liatrio/opentelemetry-demo
[Logz.io]: https://logz.io/learn/how-to-run-opentelemetry-demo-with-logz-io/
[New Relic]: https://github.com/newrelic/opentelemetry-demo
[OpenSearch]: https://github.com/opensearch-project/opentelemetry-demo
[Oracle]: https://github.com/oracle-quickstart/oci-o11y-solutions/blob/main/knowledge-content/opentelemetry-demo
[Sentry]: https://github.com/getsentry/opentelemetry-demo
[ServiceNow Cloud Observability]: https://docs.lightstep.com/otel/quick-start-operator#send-data-from-the-opentelemetry-demo
[Splunk]: https://github.com/signalfx/opentelemetry-demo
[Sumo Logic]: https://www.sumologic.com/blog/common-opentelemetry-demo-application/
[TelemetryHub]: https://github.com/TelemetryHub/opentelemetry-demo/tree/telemetryhub-backend
[Teletrace]: https://github.com/teletrace/opentelemetry-demo
[Tracetest]: https://github.com/kubeshop/opentelemetry-demo
[Uptrace]: https://github.com/uptrace/uptrace/tree/master/example/opentelemetry-demo
