"""
    LAMP v4
    Nutanix Calm DSL blueprint designed to semi-replicate the Calm Marketplace "LAMP" blueprint
"""

import json

from calm.dsl.builtins import (
    ref,
    basic_cred,
    secret_cred,
    CalmVariable,
    CalmTask,
    action,
    parallel,
    CalmVariable as Variable
)
from calm.dsl.builtins import Service, Package, Substrate
from calm.dsl.builtins import Deployment, Profile, Blueprint
from calm.dsl.builtins import (
    read_provider_spec,
    read_local_file,
    read_file,
    vm_disk_package,
)
from calm.dsl.builtins import read_ahv_spec, read_vmw_spec

# use the locally-stored private and public key files to generate
# an SSH-based credential
# this credential will be used as the default credential within the blueprint
CENTOS_USER = "centos"
CENTOS_KEY = read_local_file("keys/centos_priv")
CENTOS_PUBLIC_KEY = read_local_file("keys/centos_pub")
default_credential = basic_cred(
    CENTOS_USER, CENTOS_KEY, name="CENTOS", type="KEY", default=True,
)

class MySQLService(Service):
    @action
    def __create__():
        """Application MySQL database server"""

class APACHE_PHP(Service):

    dependencies = [ref(MySQLService)]    

    @action
    def __create__():
        """Application web servers"""

        pass

class HAProxyService(Service):

    dependencies = [ref(APACHE_PHP)]

    @action
    def __create__():
        """HAProxy application entry point"""

class HAProxyPackage(Package):

    services = [ref(HAProxyService)]

    @action
    def __install__():
        """Package installation tasks for the HAProxy server"""

        CalmTask.Exec.ssh(
            name="PackageInstallTask", filename="scripts/haproxy-install.sh", target=ref(HAProxyService)
        )

class ApachePHPPackage(Package):

    services = [ref(APACHE_PHP)]

    @action
    def __install__():
        """Package installation tasks for the Nginx web servers"""

        CalmTask.Exec.ssh(
            name="PackageInstallTask", filename="scripts/apache-php-install.sh", target=ref(APACHE_PHP)
        )

class MySQLPackage(Package):

    services = [ref(MySQLService)]

    @action
    def __install__():
        """Package installation tasks for the MySQL database server"""

        CalmTask.Exec.ssh(
            name="PackageInstallTask", filename="scripts/mysql-install.sh", target=ref(MySQLService)
        )

# disk image that will be used as the base for all VMs/services in this applicationb
CENTOS_7_CLOUD = vm_disk_package(
    name="CENTOS_7_CLOUD",
    description="",
    config={
        "image": {
            "name": "CentOS-7-x86_64-1810.qcow2",
            "type": "DISK_IMAGE",
            "source": "http://download.nutanix.com/calm/CentOS-7-x86_64-1810.qcow2",
            "architecture": "X86_64",
        },
        "product": {"name": "CentOS", "version": "7"},
        "checksum": {},
    },
)


class MySQLSubstrate(Substrate):

    os_type = "Linux"
    provider_type = "AHV_VM"
    provider_spec = read_ahv_spec(
        "specs/mysql-spec.yaml", disk_packages={1: CENTOS_7_CLOUD}
    )
    readiness_probe = {
        "connection_type": "SSH",
        "connection_port": 22,
        "connection_protocol": "",
        "timeout_secs": "",
        "delay_secs": "60",
        "retries": "5",
        "address": "@@{platform.status.resources.nic_list[0].ip_endpoint_list[0].ip}@@",
        "disabled": False,
    }
    readiness_probe["credential"] = ref(default_credential)

class ApachePHPSubstrate(Substrate):

    os_type = "Linux"
    provider_type = "AHV_VM"
    provider_spec = read_ahv_spec(
        "specs/apache-php-spec.yaml", disk_packages={1: CENTOS_7_CLOUD}
    )
    readiness_probe = {
        "connection_type": "SSH",
        "connection_port": 22,
        "connection_protocol": "",
        "timeout_secs": "",
        "delay_secs": "60",
        "retries": "5",
        "address": "@@{platform.status.resources.nic_list[0].ip_endpoint_list[0].ip}@@",
        "disabled": False,
    }
    readiness_probe["credential"] = ref(default_credential)   

class HAProxySubstrate(Substrate):

    os_type = "Linux"
    provider_type = "AHV_VM"
    provider_spec = read_ahv_spec(
        "specs/haproxy-spec.yaml", disk_packages={1: CENTOS_7_CLOUD}
    )
    readiness_probe = {
        "connection_type": "SSH",
        "connection_port": 22,
        "connection_protocol": "",
        "timeout_secs": "",
        "delay_secs": "60",
        "retries": "5",
        "address": "@@{platform.status.resources.nic_list[0].ip_endpoint_list[0].ip}@@",
        "disabled": False,
    }
    readiness_probe["credential"] = ref(default_credential)

class MySQLDeployment(Deployment):

    min_replicas = "1"
    max_replicas = "1"

    packages = [ref(MySQLPackage)]
    substrate = ref(MySQLSubstrate)

class ApachePHPDeployment(Deployment):

    min_replicas = "2"
    max_replicas = "3"

    packages = [ref(ApachePHPPackage)]
    substrate = ref(ApachePHPSubstrate)

class HAProxyDeployment(Deployment):

    min_replicas = "1"
    max_replicas = "1"

    packages = [ref(HAProxyPackage)]
    substrate = ref(HAProxySubstrate)    


class Default(Profile):

    deployments = [ MySQLDeployment, ApachePHPDeployment, HAProxyDeployment ]
    # runtime variable for user to provide MySQL database password
    MYSQL_PASSWORD = Variable.Simple.Secret("", runtime=True)


class lamp_v4_bp(Blueprint):

    services = [MySQLService, APACHE_PHP, HAProxyService]
    packages = [MySQLPackage, ApachePHPPackage, HAProxyPackage, CENTOS_7_CLOUD]
    substrates = [MySQLSubstrate, ApachePHPSubstrate, HAProxySubstrate]
    profiles = [Default]
    credentials = [default_credential]
