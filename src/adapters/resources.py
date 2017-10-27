# Copyright © 2017-2019 Zuercher Hochschule fuer Angewandte Wissenschaften.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import os
import shutil
from typing import Dict
import yaml
import tarfile
import tempfile

# XXX these docker imports are internal and not supported to be used by external processes
from compose.cli.main import TopLevelCommand
from compose.cli.command import project_from_options

# from kubernetes import client, config
import adapters.log
from epm_client.apis.package_api import PackageApi
from epm_client.apis.resource_group_api import ResourceGroupApi

LOG = adapters.log.get_logger(name=__name__)


class Backend(object):
    def create(self, instance_id: str, content: str, c_type: str, **kwargs) -> None:
        pass

    def info(self, instance_id: str, **kwargs) -> Dict[str, str]:
        pass

    def delete(self, instance_id: str, **kwargs) -> None:
        pass


class DockerBackend(Backend):
    def __init__(self) -> None:
        super().__init__()
        LOG.info('Adding DockerBackend')
        self.options = {
            "--no-deps": False,
            "--abort-on-container-exit": False,  # do not set to True
            "SERVICE": "",
            "--remove-orphans": False,
            "--no-recreate": True,
            "--force-recreate": False,
            "--build": False,
            '--no-build': False,
            '--no-color': False,
            # "--rmi": "none",
            "--volumes": "/private",
            # "--follow": False,
            # "--timestamps": False,
            # "--tail": "all",
            "-d": True,
            "-q": False,  # quiet
            "--scale": [],  # don't need this but have to supply
        }

        # TODO this location needs to be configurable
        self.manifest_cache = '/tmp'

    def create(self, instance_id: str, content: str, c_type: str, **kwargs) -> None:
        if c_type == 'docker-compose':
            LOG.warn('WARNING: this is for local-only deployments.')
            return self._create_compose(inst_id=instance_id, content=content, **kwargs)
        else:
            raise NotImplementedError('The type ({type}) of cluster manager is unknown'.format(type=c_type))

    def _create_compose(self, inst_id: str, content: str, **kwargs) -> None:
        """
        This creates a set of containers using docker compose.
        Note: the use of the docker compose python module is unsupported by docker inc.
        :param content: the docker compose file as a string
        :return:
        """

        # when we get the manifest, we have to dump it to a temporary file
        # to allow for multiple stack instances we need to have multiple projects!
        # this means multiple directories
        mani_dir = self.manifest_cache + '/' + inst_id

        if not os.path.exists(mani_dir):
            os.makedirs(mani_dir)
        else:
            LOG.info('The instance is already running with the following project: {mani_dir}'.format(mani_dir=mani_dir))
            LOG.warn('Content in this directory will be overwritten.')
            # XXX shouldn't this raise an exception?

        # can supply external parameters here...
        # parameters is the name set in the OSBA spec for additional parameters supplied on provisioning
        # if none supplied, we use an empty dict
        # add optionally supplied parameters as environment variables
        # XXX this is a naive approach and should be revisited
        parameters = kwargs.get('parameters', dict())
        env_list = list()
        for k, v in parameters.items():
            LOG.info('Including as environment variable: {k}={v}'.format(k=k, v=v))
            env_list.append(k + '=' + v)

        if len(env_list) > 0:
            m = yaml.load(content)
            for k, v in m['services'].items():
                v['environment'] = env_list
            # yaml.Dumper.ignore_aliases = True
            content = yaml.dump(m)

        LOG.debug('writing to: {compo}'.format(compo=mani_dir + '/docker-compose.yml'))
        m = open(mani_dir + '/docker-compose.yml', 'wt')
        m.write(content)
        m.close()

        project = project_from_options(mani_dir, self.options)
        cmd = TopLevelCommand(project)
        cmd.up(self.options)  # WARNING: this method can call sys.exit() but only if --abort-on-container-exit is True

    def info(self, instance_id: str, **kwargs) -> Dict[str, str]:
        mani_dir = self.manifest_cache + '/' + instance_id

        if not os.path.exists(mani_dir):
            LOG.warn('requested directory does not exist: {mani_dir}'.format(mani_dir=mani_dir))
            return {}

        LOG.debug('info from: {compo}'.format(compo=mani_dir + '/docker-compose.yml'))
        project = project_from_options(mani_dir, self.options)
        # cmd = TopLevelCommand(project)

        containers = project.containers(service_names=self.options['SERVICE'], stopped=True)

        # containers = sorted(
        #     self.project.containers(service_names=options['SERVICE'], stopped=True) +
        #     self.project.containers(service_names=options['SERVICE'], one_off=OneOffFilter.only),
        #     key=attrgetter('name'))

        info = dict()
        for c in containers:
            LOG.debug('{name} container image name: {img_name}'
                      .format(name=c.name, img_name=c.image_config['RepoTags'][0]))
            info[c.name+'_image_name'] = c.image_config['RepoTags'][0]
            LOG.debug('{name} container image: {img}'.format(name=c.name, img=c.image))
            info[c.name + '_image_id'] = c.image

            LOG.debug(c.ports)
            for k, v in c.ports.items():
                if isinstance(v, list):
                    for i in v:
                        info[c.name + '_' + k + '/HostIp'] = i['HostIp']
                        info[c.name + '_' + k + '/HostPort'] = i['HostPort']
                else:
                    info[c.name + '_' + k] = v

            LOG.debug(c.environment)
            for k, v in c.environment.items():
                info[c.name + '_environment_' + k] = v

            # add the IP address of the container
            # XXX assumes there's only 1 IP address assigned to container
            ip = [value.get('IPAddress') for value in c.dictionary['NetworkSettings']['Networks'].values()]
            info[c.name + '_' + 'Ip'] = ip[0]

            LOG.debug('{name} container command: {cmd}'.format(name=c.name, cmd=c.human_readable_command))
            info[c.name + '_cmd'] = c.human_readable_command

            LOG.debug('{name} container state: {state}'.format(name=c.name, state=c.human_readable_state))
            info[c.name + '_state'] = c.human_readable_state

        states = set([v for k, v in info.items() if k.endswith('state')])

        # states from compose.container.Container: 'Paused', 'Restarting', 'Ghost', 'Up', 'Exit %s'
        # states for OSBA: in progress, succeeded, and failed
        for state in states:
            if state.startswith('Exit'):
                # there's been an error with docker
                info['srv_inst.state.state'] = 'failed'
                info['srv_inst.state.description'] = \
                    'There was an error in creating the instance {error}'.format(error=state)
                # return 'Error with docker: {error}'.format(error=state), 500

        if len(states) == 1:  # if all states of the same value
            if states.pop() == 'Up':  # if running: Up
                info['srv_inst.state.state'] = 'succeeded'
                info['srv_inst.state.description'] = 'The service instance has been created successfully'
        else:
            # still waiting for completion
            info['srv_inst.state.state'] = 'in progress'
            info['srv_inst.state.description'] = 'The service instance is being created.'

        return info

    def delete(self, instance_id: str, **kwargs) -> None:
        mani_dir = self.manifest_cache + '/' + instance_id

        if not os.path.exists(mani_dir):
            LOG.warn('requested directory does not exist: {mani_dir}'.format(mani_dir=mani_dir))
            # raise Exception('requested directory does not exist: {mani_dir}'.format(mani_dir=mani_dir))
            return

        self.options["--force"] = True
        self.options["--rmi"] = "none"
        LOG.info('destroying: {compo}'.format(compo=mani_dir + '/docker-compose.yml'))
        project = project_from_options(mani_dir, self.options)
        cmd = TopLevelCommand(project)
        cmd.down(self.options)

        try:
            shutil.rmtree(mani_dir)
        except PermissionError:
            # Done to let travis pass
            LOG.warn('Could not delete the directory {dir}'.format(dir=mani_dir))


class EPMBackend(Backend):
    def __init__(self) -> None:
        super().__init__()
        LOG.info('Adding EPMBackend')
        self.sid_to_rgid = dict()  # TODO make this persistent
        self.api_endpoint = os.environ.get('ET_EPM_API', 'http://localhost:8180/') + 'v1'
        LOG.info('EPM API Endpoint: ' + self.api_endpoint)

    def create(self, instance_id: str, content: str, c_type: str, **kwargs) -> None:
        super().create(instance_id, content, c_type, **kwargs)

        if c_type != 'epm':
            raise NotImplementedError('The type ({type}) of cluster manager is unknown'.format(type=c_type))

        # create the tar file including metadata.yaml and docker-compose.yaml
        dirpath = tempfile.mkdtemp()

        with open(dirpath + 'metadata.yaml', 'w') as out:
            out.write('name: ' + instance_id)

        # update parameters if they're supplied
        with open(dirpath + 'docker-compose.yaml', 'w') as out:
            out.write(content)

        with tarfile.open(dirpath + 'service.tar', mode='w') as tf:
            tf.add(dirpath + 'metadata.yaml', arcname='metadata.yaml', recursive=False)
            tf.add(dirpath + 'docker-compose.yaml', arcname='docker-compose.yml', recursive=False)

        package = PackageApi()
        package.api_client.host = self.api_endpoint

        # submit service tar to EPM
        pkg = package.receive_package(dirpath + "service.tar")

        # record the service instance ID against the resource group ID returned by EPM # TODO make persistent
        self.sid_to_rgid[instance_id] = pkg.to_dict()['id']

    def info(self, instance_id: str, **kwargs) -> Dict[str, str]:
        super().info(instance_id, **kwargs)
        # source: we have a resource group ID. iterate through the VDUs to return the info
        # output:
        #
        # {'id': 'ca35a24a-1016-46fa-8aa4-7d52e692867e',
        #  'name': 'test-id-123',
        #  'networks': [{'cidr': '172.23.0.0/16',
        #                'id': '81147bc2-d6b1-4be8-9a04-2d6ec3f3a712',
        #                'name': 'testid123_default',
        #                'networkId': 'c7f903db071b48dc93acb13fd91b7056733fcc4214d3063de0be6a1c6000a18c',
        #                'poPName': 'docker-local'}],
        #  'pops': [],
        #  'vdus': [{'computeId': '273e094737ee316856f089f5a464560d395b9315142af6f7a3e9e77d94adb692',
        #            'events': [],
        #            'id': '009e77d4-254a-4752-bd3f-d8bea76475d4',
        #            'imageName': 'elastest/ebs-spark:latest',
        #            'ip': '172.23.0.2',
        #            'metadata': [{'id': '43117b4b-d360-427a-92f4-89fe74e84c73',
        #                          'key': 'PORT_BINDING',
        #                          'value': '8080:8080/tcp'},
        #                         {'id': '9e9c45dc-de07-410b-933e-adfd559779d5',
        #                          'key': 'PORT_BINDING',
        #                          'value': '7077:7077/tcp'}],
        #            'name': '/spark-master',
        #            'netName': 'testid123_default',
        #            'poPName': '',
        #            'status': None},
        #           {'computeId': 'afee33cdd0a5ce2b26f262762a1ccfce89056ff0f839a0188c30c600b9f422a9',
        #            'events': [],
        #            'id': '3ed4dde7-543a-4cfe-abbc-a5352c202826',
        #            'imageName': 'elastest/ebs:latest',
        #            'ip': '172.23.0.4',
        #            'metadata': [{'id': '8dd88b81-4c15-4f2f-ac45-c00a3854a163',
        #                          'key': 'PORT_BINDING',
        #                          'value': '5000:5000/tcp'}],
        #            'name': '/testid123_rest-api_1',
        #            'netName': 'testid123_default',
        #            'poPName': '',
        #            'status': None},
        #           {'computeId': 'fbae3639bc32390844c578bf9e183f39c7fa0c63686df08aa764839908c7bcc7',
        #            'events': [],
        #            'id': '1ae0af11-ff1e-4559-a574-d826f0799a67',
        #            'imageName': 'elastest/ebs-spark:latest',
        #            'ip': '172.23.0.3',
        #            'metadata': [{'id': 'dc70c8ea-b470-4e76-bdd1-b5741a8c59d5',
        #                          'key': 'PORT_BINDING',
        #                          'value': ':8081/tcp'}],
        #            'name': '/testid123_spark-worker_1',
        #            'netName': 'testid123_default',
        #            'poPName': '',
        #            'status': None}]}

        # XXX not enough to satisfy what's currently sent to end-user/TORM
        rgrp = ResourceGroupApi()
        rgrp.api_client.host = self.api_endpoint
        info = rgrp.get_resource_group_by_id(id=self.sid_to_rgid[instance_id])

        info = info.to_dict()
        info['srv_inst.state.state'] = 'ok'  # what should this be from EPM? the status field?
        info['srv_inst.state.description'] = ''  # what should this be from EPM?

        return info

    def delete(self, instance_id: str, **kwargs) -> None:
        super().delete(instance_id, **kwargs)
        # delete the resource group (created by package) by ID will remove the containers
        # XXX note this is a synchronous operation... potential for proxy timeouts
        package = PackageApi()
        package.api_client.host = self.api_endpoint
        LOG.info('Deleting the package/resource group ID: ' + self.sid_to_rgid[instance_id])
        package.delete_package(id=self.sid_to_rgid[instance_id])


class KubernetesBackend(Backend):
    def __init__(self) -> None:
        super().__init__()
        LOG.info('Adding KubernetesBackend')
        # self.directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
        # prefix = "k8s_"
        # Identify all kubernetes files to process
        # self.files = [os.path.join(self.directory, filename) for filename in os.listdir(self.directory)
        #               if filename.startswith(prefix) and filename.endswith(".yaml")]
        # k8s_config_file = os.path.abspath(os.path.join(self.directory, 'k8s_config'))
        # self.api = pykube.HTTPClient(pykube.KubeConfig.from_file(k8s_config_file))
        # config.load_kube_config()
        # self.k8s_beta = client.ExtensionsV1beta1Api()

    def create(self, instance_id: str, content: str, c_type: str, **kwargs) -> None:
        super().create(instance_id, content, c_type)
        # dep = yaml.load(content)
        # resp = self.k8s_beta.create_namespaced_deployment(body=dep, namespace="default")
        # print("Deployment created. status='%s'" % str(resp.metadata.uid))
        # print("Deployment created. status='%s'" % str(resp.status))
        # return resp.metadata.uid

    def info(self, instance_id: str, **kwargs) -> Dict[str, str]:
        super().info(instance_id)
        return {}

    def delete(self, instance_id: str, **kwargs) -> None:
        super().delete(instance_id)
        # content = ''
        # dep = yaml.load(content)
        # resp = self.k8s_beta.delete_collection_namespaced_deployment(body=dep, namespace="default")


class DummyBackend(Backend):
    def __init__(self) -> None:
        super().__init__()
        LOG.info('Adding DummyBackend')

    def create(self, instance_id: str, content: str, c_type: str, **kwargs) -> None:
        super().create(instance_id, content, c_type)
        LOG.info('DummyBackend driver: create called')

    def info(self, instance_id: str, **kwargs) -> Dict[str, str]:
        super().info(instance_id)
        LOG.info('DummyBackend driver: info called')

        info = {
            'testid123_spark-worker_1_image_name': 'elastest/ebs-spark-base:0.5.0',
            'testid123_spark-worker_1_image_id':
                'sha256:138a91572bd6bdce7d7b49a44b91a4caf4abdf1a75f105991e18be971353d5cb',
            'testid123_spark-worker_1_8080/tcp': None,
            'testid123_spark-worker_1_8081/tcp/HostIp': '0.0.0.0',
            'testid123_spark-worker_1_8081/tcp/HostPort': '32784',
            'testid123_spark-worker_1_cmd': '/usr/bin/supervisord --configuration=/opt/conf/slave.conf',
            'testid123_spark-worker_1_state': 'Up',
            'spark-master_image_name': 'elastest/ebs-spark-base:0.5.0',
            'spark-master_image_id': 'sha256:138a91572bd6bdce7d7b49a44b91a4caf4abdf1a75f105991e18be971353d5cb',
            'spark-master_8080/tcp/HostIp': '0.0.0.0',
            'spark-master_8080/tcp/HostPort': '8080',
            'spark-master_cmd': '/usr/bin/supervisord --configuration=/opt/conf/master.conf',
            'spark-master_state': 'Up',
            'srv_inst.state.state': 'succeeded',
            'srv_inst.state.description': 'The service instance has been created successfully'
        }

        # TODO FIXME below until return is duplicated code!!!!
        states = set([v for k, v in info.items() if k.endswith('state')])

        # states from compose.container.Container: 'Paused', 'Restarting', 'Ghost', 'Up', 'Exit %s'
        # states for OSBA: in progress, succeeded, and failed
        for state in states:
            if state.startswith('Exit'):
                # there's been an error with docker
                info['srv_inst.state.state'] = 'failed'
                info['srv_inst.state.description'] = 'There was an error in creating the instance {error}'.format(
                    error=state)
                # return 'Error with docker: {error}'.format(error=state), 500

        if len(states) == 1:  # if all states of the same value
            if states.pop() == 'Up':  # if running: Up
                info['srv_inst.state.state'] = 'succeeded'
                info['srv_inst.state.description'] = 'The service instance has been created successfully'
        else:
            # still waiting for completion
            info['srv_inst.state.state'] = 'in progress'
            info['srv_inst.state.description'] = 'The service instance is being created.'

        LOG.info('Dummy data:\n{dummy}'.format(dummy=info))
        return info

    def delete(self, instance_id: str, **kwargs) -> None:
        super().delete(instance_id)
        LOG.info('DummyBackend driver: delete called')


class ResourceManager(Backend):

    def __init__(self) -> None:
        self.backends = {
            'docker': DockerBackend(),
            'kubernetes': KubernetesBackend(),
            'dummy': DummyBackend(),
            'epm': EPMBackend(),
        }
        # set an alias to the docker-compose driver
        LOG.info('Adding docker-compose alias to DockerBackend')
        self.backends['docker-compose'] = self.backends.get('docker')
        LOG.info('Adding k8s alias to KubernetesBackend')
        self.backends['k8s'] = self.backends.get('kubernetes')

    def create(self, instance_id: str, content: str, c_type: str, **kwargs):
        be = self.backends.get(c_type, self.backends['dummy'])
        be.create(instance_id, content, c_type, **kwargs)

    def info(self, instance_id: str, **kwargs) -> Dict[str, str]:
        if 'manifest_type' in kwargs:
            manifest_type = kwargs.get('manifest_type', 'dummy')
            be = self.backends.get(manifest_type, self.backends['dummy'])
        else:
            raise RuntimeError('manifest_type parameter not specified in call to info()')

        return be.info(instance_id, **kwargs)

    def delete(self, instance_id: str, **kwargs):
        if 'manifest_type' in kwargs:
            manifest_type = kwargs.get('manifest_type', 'dummy')
            be = self.backends.get(manifest_type, self.backends['dummy'])
        else:
            raise RuntimeError('manifest_type parameter not specified in call to info()')

        be.delete(instance_id, **kwargs)


RM = ResourceManager()
