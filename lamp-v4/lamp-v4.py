"""
    LAMP v4
    Nutanix Calm DSL blueprint designed to semi-replicate
    the Calm Marketplace "LAMP" blueprint
"""

import os

from calm.dsl.builtins import (
    ref,
    basic_cred,
    CalmTask,
    action,
    CalmVariable as Variable
)
from calm.dsl.builtins import Service, Package, Substrate
from calm.dsl.builtins import Deployment, Profile, Blueprint
from calm.dsl.builtins import (
    read_local_file,
    vm_disk_package,
)
from calm.dsl.builtins import read_ahv_spec

"""
Use the locally-stored private and public key files to generate
an SSH-based credential
This credential will be used as the default credential within the blueprint
Note the Calm DSL will look in .local in the Blueprint root
then ~/.calm/.local when using read_local_file (in that order)
"""
CENTOS_USER = "centos"
CENTOS_KEY = read_local_file(os.path.join("keys", "centos_priv"))
CENTOS_PUBLIC_KEY = read_local_file(os.path.join("keys", "centos_pub"))
default_credential = basic_cred(
    CENTOS_USER, CENTOS_KEY, name="CENTOS", type="KEY", default=True,
)


class MySQLService(Service):
    """
    Service definition for our MySQL server
    Note the VM's installation package is specified further down within this
    blueprint spec and the VM's specifications (CPU/RAM etc) are specified
    in the external files stored in specs/
    """
    @action
    def __create__():
        """Application MySQL database server"""


class APACHE_PHP(Service):
    """
    Similar to the MySQL server, this is the definition for our Apache PHP
    server.  All VM specs are provided the same way, but note the Apache PHP
    servers have an explicit dependency on the MySQL server, indicated by
    the "dependencies" statement.  These dependencies instruct Calm to "wait"
    until the dependent service is completely deployed before beginning to
    deploy this one.
    """

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
    """
    Here we are specifying the packages that will run at various steps during
    the deployment.  In this example, we are configuring a Package Install Task
    that will have its code pulled from the scripts/haproxy-install.sh script.
    At the same time, we are also specifying which Calm service (VM) this
    package will be associated with
    """

    services = [ref(HAProxyService)]

    @action
    def __install__():
        """Package installation tasks for the HAProxy server"""

        CalmTask.Exec.ssh(
            name="PackageInstallTask",
            filename="scripts/haproxy-install.sh",
            target=ref(HAProxyService)
        )


class ApachePHPPackage(Package):

    services = [ref(APACHE_PHP)]

    @action
    def __install__():
        """Package installation tasks for the Nginx web servers"""

        CalmTask.Exec.ssh(
            name="PackageInstallTask",
            filename="scripts/apache-php-install.sh",
            target=ref(APACHE_PHP)
        )


class MySQLPackage(Package):

    services = [ref(MySQLService)]

    @action
    def __install__():
        """Package installation tasks for the MySQL database server"""

        CalmTask.Exec.ssh(
            name="PackageInstallTask",
            filename="scripts/mysql-install.sh",
            target=ref(MySQLService)
        )


"""
Disk image that will be used as the base images for all services/VMs
in this application
"""
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
    """
    The Calm Substrate outlines the "wrapper" for our VM, e.g. the VM's
    operating system, the VM spec from specs/mysql-spec.yaml, the disks
    the VM will have attached etc.
    """

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
    """
    The Calm DSL "Deployment" will allow us to specify things like min and max
    replicas, a key setting that will be used when a VM array is required.
    In our application example, this is critical because the Apache PHP servers
    can be scaled in or out when we add our scaling scripts later.
    """

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

    deployments = [MySQLDeployment, ApachePHPDeployment, HAProxyDeployment]
    # runtime variable for user to provide MySQL database password
    MYSQL_PASSWORD = Variable.Simple.Secret("", runtime=True)

    """
    These custom profile actions control our ScaleOut and ScaleIn
    requirements
    """
    @action
    def ScaleOut():
        """Profile action for scaling out our web servers"""

        """
        Custom action variable that allows the user to specify the
        ScaleOut value i.e. how many new Apache PHP web servers to deploy
        """
        COUNT = Variable.Simple.int("1", runtime=True)

        CalmTask.Scaling.scale_out(
            "@@{COUNT}@@", target=ref(ApachePHPDeployment), name="Scale Out"
        )

        """
        Specify which script will be setup to run when the custom
        action is run, then specify which services/VMs this script
        will run on
        """
        CalmTask.Exec.ssh(
            name="ConfigureHAProxy",
            filename="scripts/haproxy-scaleout.sh",
            target=ref(HAProxyService),
        )

    @action
    def ScaleIn():
        """Profile action for scaling in our web servers"""

        """
        Custom action variable that allows the user to specify the
        ScaleIn value i.e. how many new Apache PHP web servers to destroy
        """
        COUNT = Variable.Simple.int("1", runtime=True)

        CalmTask.Scaling.scale_in(
            "@@{COUNT}@@", target=ref(ApachePHPDeployment), name="Scale In"
        )

        """
        Specify which script will be setup to run when the custom
        action is run, then specify which services/VMs this script
        will run on
        """
        CalmTask.Exec.ssh(
            name="ConfigureHAProxy",
            filename="scripts/haproxy-scalein.sh",
            target=ref(HAProxyService),
        )

    @action
    def DBBackup():
        """Profile action for backing up the MySQL database"""

        """
        Custom action variable that allows the user to specify the
        ScaleIn value i.e. how many new Apache PHP web servers to destroy
        """
        BACKUP_FILE_PATH = Variable.Simple("~/db_backup",
                                           runtime=True)

        """
        Specify which script will be setup to run when the custom
        action is run, then specify which services/VMs this script
        will run on
        """
        CalmTask.Exec.ssh(
            name="BackupDatabase",
            filename="scripts/mysql-backup.sh",
            target=ref(MySQLService),
        )

    @action
    def DBRestore():
        """Profile action for restoring the MySQL database"""

        """
        Custom action variable that allows the user to specify the
        ScaleIn value i.e. how many new Apache PHP web servers to destroy
        """
        RESTORE_FILE_PATH = Variable.Simple("~/db_backup/db_dump.sql.gz",
                                            runtime=True)

        """
        Specify which script will be setup to run when the custom
        action is run, then specify which services/VMs this script
        will run on
        """
        CalmTask.Exec.ssh(
            name="RestoreDatabase",
            filename="scripts/mysql-restore.sh",
            target=ref(MySQLService),
        )


class lamp_v4_bp(Blueprint):

    services = [MySQLService, APACHE_PHP, HAProxyService]
    packages = [MySQLPackage, ApachePHPPackage, HAProxyPackage, CENTOS_7_CLOUD]
    substrates = [MySQLSubstrate, ApachePHPSubstrate, HAProxySubstrate]
    profiles = [Default]
    credentials = [default_credential]
