# Homelab DNS

This Pulumi project sets up separate Scaleway projects to manage the Homelab DNS. 

This stack contains resources created in 2 different Scaleway projects:

* project ${ns1.project_id} (id: ${ns1.project_id})
  * 2 NS records in the parent zone ${ns1.dns_zone} 
* project ${subdomain.project_id} (id: ${subdomain.project_id})
  * Policy ${pulumi_dns_policy.name} allowing for:
    * Full DNS access to the project
  * Application ${cert_manager_scaleway_webhook_application.name}
  * API Key ${pulumi_api_key.id} for programmatic access by the Kubernetes clusters for CertManager usage
