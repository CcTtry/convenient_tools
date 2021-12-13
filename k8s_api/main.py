# @Project -> File   ：python_client_k8s -> main
# @IDE    ：PyCharm
# @Author ：Ctry
# @Date   ：2021/11/28 20:38
# @Desc   ：

from kubernetes import client, config

config.kube_config.load_kube_config(config_file="./kubeconfig.yaml")

# 获取API的CoreV1Api版本对象
v1 = client.CoreV1Api()

# 列出 namespaces
for ns in v1.list_namespace().items:
    print(ns.metadata.name)

# 列出所有的services
ret = v1.list_service_for_all_namespaces(watch=False)
for i in ret.items:
    print(
        "%s \t%s \t%s \t%s \t%s \n" % (i.kind, i.metadata.namespace, i.metadata.name, i.spec.cluster_ip, i.spec.ports))

# 列出所有的pod
ret = v1.list_pod_for_all_namespaces(watch=False)
for i in ret.items:
    print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

# 列出所有deploy
# ret = v1.list_deployments_for_all_namespaces(watch=False)
# for i in ret.items:
#     print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))

##列出其他资源和以上类似，不懂可以查看(kubectl  api-resources)

