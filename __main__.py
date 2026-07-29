from typing import Dict, Any, List

import pulumi
import pulumiverse_scaleway as scw

config = pulumi.Config()
dns_zone = config.require("dns_zone")
zone = config.require("zone")
scw_homelab_project_name = config.require("project_name")
scw_organization_id = config.require("organizationId")
scw_parent_project = scw.account.get_project("hardes", organization_id=scw_organization_id)
scw_homelab_project = scw.account.get_project(scw_homelab_project_name, organization_id=scw_organization_id)

subdomain = scw.domain.Zone(
    zone,
    scw.domain.ZoneArgs(
        domain=dns_zone,
        subdomain=zone,
        project_id=scw_homelab_project.project_id,
    ),
)

args = scw.domain.RecordArgs(
    name=zone,
    dns_zone=dns_zone,
    type="NS",
    data="ns0.dom.scw.cloud.",
    project_id=scw_parent_project.project_id,
)
scw.domain.Record(
    f"{zone}-ns-1",
    args,
    opts=pulumi.ResourceOptions(
        depends_on=[subdomain],
    )
)

args.data = "ns1.dom.scw.cloud."
scw.domain.Record(
    f"{zone}-ns-2",
    args,
    opts=pulumi.ResourceOptions(
        depends_on=[subdomain],
    )
)
