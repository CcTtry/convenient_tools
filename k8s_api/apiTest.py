# @Project -> File   ：python_client_k8s -> apiTest
# @IDE    ：PyCharm
# @Author ：Ctry
# @Date   ：2021/12/2 19:23
# @Desc   ：
from kubernetes import client, config
from os import path
import yaml
from kubernetes import config, dynamic
from kubernetes.client import api_client
import requests
import json


class k8sapi:
    def __init__(self):
        # 初始化conn
        config.kube_config.load_kube_config(config_file="kubeconfig.yaml")
        self.coreApi = client.CoreV1Api()
        self.CustomObjectsApi = client.CustomObjectsApi()

    def get_all_nodes(self):
        """
        :rtype: V1NodeList 获取所有的node节点
        """
        return self.coreApi.list_node()

    def get_nodes_num(self):
        """
        :rtype: int 获取节点的数目
        """
        return len(self.get_all_nodes().items)

    def get_all_nodes_name(self):
        """
        :rtype: list 获取所有节点的名称
        """
        names = []
        for item in self.get_all_nodes().items:
            names.append(item.metadata.name)
        return names

    def namespaces(self):
        """
        :rtype: 列出 namespaces
        """
        ret = self.coreApi.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s	%s	%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    def services(self):
        # 列出所有的services
        ret = self.coreApi.list_service_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s 	%s 	%s 	%s 	%s " % (
            i.kind, i.metadata.namespace, i.metadata.name, i.spec.cluster_ip, i.spec.ports))

    def pods(self):
        """
        :rtype: list 列出所有的pod
        """
        ret = self.coreApi.list_pod_for_all_namespaces(watch=False)
        for i in ret.items:
            print("%s	%s	%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

    def create(self):
        """
        :rtype: null  通过yaml文件创建deployment
        """
        config.load_kube_config()
        with open(path.join(path.dirname(__file__), "/root/deploy.yaml")) as f:
            dep = yaml.safe_load(f)
            k8s_apps_v1 = client.AppsV1Api()
            resp = k8s_apps_v1.create_namespaced_deployment(
                body=dep, namespace="default")
            print("Deployment created. status='%s'" % resp.metadata.name)

    def delete(self, name='nginx-pod'):
        """
        :rtype: null  通过name 删除pod
        """
        config.load_kube_config()
        k8s_core_v1 = client.CoreV1Api()
        resp = k8s_core_v1.delete_namespaced_pod(namespace="default", name=name)
        print("delete Pod ")


class nodeInfo():
    """
    该类用于汇总节点的信息，包含cpu、memory等一系列信息
    """
    def __init__(self, node):
        '''
            self.total_cpu cpu总量
            self.cpu_usage 利用率
            self.used_cpu 已使用cpu 的量
            self.node 节点名称，用作键值
        '''
        self.node = node
        self.total_cpu = 0
        self.used_cpu = 0

        self.total_mem = 0
        self.used_mem = 0

        self.cpu_usage = -0.01
        self.mem_usage = -0.01
        self.window = 0.00
    def getInfo(self):
        """
        :return:  str
        """
        return "nodeName ={} total_cpu ={}   cpu_usage={:.3}%  total_mem={}Ki  mem_usage={:.3}%  window={}"\
            .format(self.node.__str__(), self.total_cpu, self.cpu_usage, self.total_mem, self.mem_usage, self.window)

    def setInfo(self):
            """
            :return:  str
            """
            self.cpu_usage = self.used_cpu/(self.window * 1e9) * 100.0
            self.mem_usage = self.used_mem/self.total_mem * 100.0


def getNodeUsage():
    """
    1、获取所有节点的全部 CPU数量， memory数量
    2、获取所有节点已使用的CPU数量，memory数量
    3、计算获取CPU、memory利用率
    :return:  dict 字典类型， key为node主机名， value为nodeInfo实例对象
    """
    # 1、获取所有节点的全部 CPU数量， memory数量
    # key-> nodeInfo: 节点名称->nodeInfo类
    info = {

    }

    myk8s = k8sapi()
    nodes = myk8s.get_all_nodes().items
    # 遍历所有的节点，获取每个节点的cpu以及memory参数
    for item in nodes:
        # 每一个 item对应着一个node的参数
        # myk8s.append(item.metadata.name)
        if item.metadata.name in info.keys():
            pass
        else:
            nodeinfo = nodeInfo(item.metadata.name)
            nodeinfo.total_cpu = float(item.status.capacity['cpu'])
            nodeinfo.total_mem = float(item.status.capacity['memory'][0:-2])
            info[item.metadata.name] = nodeinfo

    # 遍历所有的节点，获取每个节点的cpu以及memory 已使用的总量
    k8s_nodes_used = myk8s.CustomObjectsApi.list_cluster_custom_object("metrics.k8s.io", "v1beta1", "nodes")
    for item in k8s_nodes_used['items']:
        if item['metadata']['name'] in info.keys():
            info[item['metadata']['name']].used_cpu = float(item['usage']['cpu'][0: -1])
            info[item['metadata']['name']].window = float(item['window'][0: -1])
            info[item['metadata']['name']].used_mem = float(item['usage']['memory'][0: -2])
            info[item['metadata']['name']].setInfo()
    return info

if __name__ == '__main__':

    # print(myk8s.get_node_label_value(nodesName, 'capacity'))
    # print(myk8s.get_node_label_value(nodesName, 'annotations'))
    # myk8s.pods()

    '''
    1、获取所有节点的全部 CPU数量， memory数量
    2、获取所有节点已使用的CPU数量，memory数量
    3、计算获取CPU、memory利用率
    '''
    info = getNodeUsage()
    for k in info:
        print(info[k].getInfo())

