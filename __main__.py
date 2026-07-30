from typing import Dict, Any, List

import pulumi
import pulumiverse_scaleway as scw

config = pulumi.Config()
dns_zone = config.require("dns_zone")
sub_zone = config.require("sub_zone")
scw_homelab_project_name = config.require("project_name")
scw_organization_id = config.require("organizationId")
scw_parent_project = scw.account.get_project("hardes", organization_id=scw_organization_id)
scw_homelab_project = scw.account.get_project(name=scw_homelab_project_name, organization_id=scw_organization_id)

# Create the subdomain in the correct homelab project on Scaleway, either `homelab` or `homelab-test`
subdomain = scw.domain.Zone(
    sub_zone,
    scw.domain.ZoneArgs(
        domain=dns_zone,
        subdomain=sub_zone,
        project_id=scw_homelab_project.project_id,
    ),
)

# Create the NS records in the parent DNS zone, also in the parent Scaleway project, to indicate where the
# nameservers are for the subzone
args = scw.domain.RecordArgs(
    name=sub_zone,
    dns_zone=dns_zone,
    type="NS",
    data="ns0.dom.scw.cloud.",
    project_id=scw_parent_project.project_id,
)
scw.domain.Record(
    f"{sub_zone}-ns-1",
    args,
    opts=pulumi.ResourceOptions(
        depends_on=[subdomain],
    )
)

args.data = "ns1.dom.scw.cloud."
scw.domain.Record(
    f"{sub_zone}-ns-2",
    args,
    opts=pulumi.ResourceOptions(
        depends_on=[subdomain],
    )
)

# Create the IAM application and permissions to manage the DNS records within this subdomain
cert_manager_scaleway_webhook_application = scw.iam.Application(
    'certmanager-scaleway-webhook',
    name=f"certmanager-scaleway-webhook-{pulumi.get_stack()}",
    description=f"CertManager Scaleway Webhook for {pulumi.get_stack()}",
    organization_id=scw_organization_id,
)

pulumi_api_key = scw.iam.ApiKey(
    'certmanager-scaleway-webhook',
    application_id=cert_manager_scaleway_webhook_application.id,
    description=f"CertManager Scaleway Webhook for {pulumi.get_stack()}",
    default_project_id=scw_homelab_project.project_id,
)

pulumi_dns_policy = scw.iam.Policy(
    'certmanager-scaleway-webhook',
    scw.iam.PolicyArgs(
        name=f"homelab-dns-admin-{pulumi.get_stack()}",
        description=f"Policy to let the CertManager Scaleway Webhook create & delete DNS records in {sub_zone}.hardes.be",
        application_id=cert_manager_scaleway_webhook_application.id,
        organization_id=scw_organization_id,
        rules=[
            scw.iam.PolicyRuleArgs(
                permission_set_names=["DomainsDNSFullAccess"],
                # TODO limit from org to project level once this is fixed:
                # https://github.com/pulumi/pulumi/issues/17181
                # project_ids=[scw_homelab_project.project_id],
                organization_id=scw_organization_id,
            )
        ]
    )
)
