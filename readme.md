# Kubernetes centric workflow scheduler

## Problem: 

1.5 years in, Airflow still not as stable as we'd like.

* **It's complex to deploy:** 29 .yaml files in the helm chart directory
* **We don’t use most of the features:** It was designed for pre-kubernetes resource allocation. We just use it as a scheduler (KubePodOperator)
* **It’s hard to test dags:** Many data scientists don’t know how to set it up, or run a job locally. 
* **The access control story isn’t great:** We will have to hack around the RBAC system to make it work.
* **The UI kinda sucks**: For one thing, you have to refresh to see updates to state or logs.
* **Other stuff that’s hard:** Customizing scheduling logic, having inter dag dependencies, to run parts of dags, to include dbt in a sane way, to parse through logs, to get a snapshot of state


**Summary**: Airflow is a hugely complex piece of outdated software that everyone acknowledges is bad. While there are some promising alternatives none are clear winners.

## Solution

We need an orchestrator that does a few things very well, most importantly send jobs to a k8s cluster on a schedule, and show their status in a clear UI.

## Proposal
Write one ourselves! A V0 solution must:

* Allow the user to run a command or script in any better Docker image (datalake-etl, reporting-loanfile, analytics, dbt, guzzler)
* Spin up a new pod to run a job as defined above on demand
* Allow a cron schedule to be set for a job, and start runs accordingly.
* Store the stdout and stderr from each run in S3
* Store metadata about each run including link to log in database
* Allow dags to contain tasks with explicit dependencies which are run in correct order.
* Provide a user interface that allows a user to see
	* The status of the last X runs of each dag
	* Logs for any task	
* Alert to slack on failure with link to UI
* Easy local development

References:
* [taichino/croniter](https://github.com/taichino/croniter)
* [CronJob | Kubernetes](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
* [Argo Workflows - The workflow engine for Kubernetes](https://argoproj.github.io/argo/)
* https://github.com/kubernetes-client/python
* [Prefect - The New Standard in Dataflow Automation - Prefect](https://www.prefect.io/)
* [Dagster](https://dagster.io/)
* [Metaflow](https://metaflow.org/)
* https://airflow.apache.org/
* https://github.com/better/mortgage/tree/master/data-jobs
* 