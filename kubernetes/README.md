# Kubernetes篇

1. 請列舉kubernetes組成元件及其功用
> **Control Plane Components** 
<br>kube-apiserver: to expose k8s api(front-end)<br>
etcd: to store all cluster data<br>
kube-scheduler: select a node for pod to run<br>
**Node Components**
<br>kubelet: makes sure containers are running in a Pod healthily<br>
kube-proxy: maintains network rules on nodes. kube-proxy forwards the traffic itself
2. 你為何使用kubernetes而不是其他工具如docker-compose, ansible等
> 因一開始DAT使用大部分皆使用
3. 如何在不同的kubernetes config中切換
> 在環境變數(KUBECONFIG)加上config的位置並使用kubectl config指定其位置
4. 什麼時候會需要在一個Pod中有多個container
> 一個pod中的container資源是共享的，volume的內容也是，當我們須在服務中共享各容器不斷更新的資料時
5. 解釋Deployment, StatefulSet, DaemonSet各自有何區別

| \ | Deployment | StatefulSet | DaemonSet |
| :---: | --- | --- | --- |
| Replicas | {deployment-name}-{replica-set-id}-{pod-id} | index starts from 0 | {DaemonSet-name}-{replica-set-id}-{pod-id} |
| Pod Located | a specific node | a specific node | every node |
| PVC | sharing storage | independent storage | sharing storage |
| Timing | Stateless | Stateful | log collection(promtail), monitoring(prometheus), storage |
| Rollback | V | X (since no ReplicaSet created) | X |
| Pause, Resume Supported | V | X | X |  
| Example | Grafana | Loki | promtail |

6. 現有一個deployment-a需要更新image版本，如何使用kubectl達成
> kubectl set image deployment/a {container-name}=image:{new-tag}
7. 呈上，更新image後發現錯誤，如何退回前次舊版本，如何退回前5次版本
> to see previous version's details: `kubectl rollout history deployment a --revision=5`<br>
to rollback to the previous deployment:
`kubectl rollout undo deployment/a --to-revision=5`<br>
to check the rollout status:
`kubectl rollout status deployment/a`
8. 如何在版本列表中寫註釋
> --record=false: Record current kubectl command in the resource annotation. If set to false, do
not record the command. If set to true, record the command. If not set, default to updating the
existing annotation value only if one already exists.
9. node selector, nodeAffinity, podAffinity使用時機分別有何不同
> __node selector__ would be recommended if assigning pod in a node with specific label considered.<br>As for __nodeAffinity__ which offers more matching rule provides 2 methods: requiredDuringSchedulingIgnoredDuringExecution(hard), preferredDuringSchedulingIgnoredDuringExecution(soft).<br>soft method would try the expression, and apply on elsewhere if policy not possible.<br>if __podAffinity__ is applied, the node the pod created on would consider the pod running on it.
10. 為了保證服務穩定，有一個replica = 3的deployment希望每一個Pod均運行在不同node上，請問如何實現
```yaml
    affinity:
        podAntiAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
          - labelSelector:
              matchExpressions:
              - key: app
                operator: In
                values:
                - web-store
            topologyKey: "kubernetes.io/hostname"
```
11. 簡單解釋HorizontalPodAutoScalar
> scale pods in replication controller, deployment on observed CPU utilization <br>
**desiredReplicas = ceil[currentReplicas * ( currentMetricValue / desiredMetricValue )]**
12. 當你有特定的一個Pod不能被隨意重啟，如何確保其他人在drain node時會收到通知
> Pod disruption budget: Deployment, ReplicationController, ReplicaSet, StatefulSet could be selected. When it only exists one instance, PDB should be set maxUnavailable as 0. Moreover, when it exists several instances, PDB should be set maxUnavailable as 1. <br>
 <del> A pod with priorityClassName which has higher value meaning higher priority. Prometheus monitors on kube_pod_container_status_restarts_total. <del>
13. 如何在kubernetes實現blue/green deployment
> we can use change selector or set policy to RollingUpdate for updating deployment seamlessly
14. 當service無法從kubernetes外部存取時，你會如何debug
> kubectl exec 進入容器確認是否在容器中可以存取，若可以可能是暴露服務方式錯誤或防火牆未開
15. 請說明Service中，ClusterIP, NodePort, LoadBalancer之間的差異

| \ | ClusterIP | NodePort | LoadBalancer |
| :---: | --- | --- | --- |
| Include | ClusterIP | ClusterIP, NodePort | ClusterIP, NodePort, LoadBalancer |
| port interval | * | 30000-32767 (to change its range through **--extra-config=apiserver.ServiceNodePortRange={PORT_RANGE}**) | * |
| expose port to its worker node | X (kubectl proxy to expose) | V | V |
16. 舉出三個為kubernetes提供networking的方案，簡單描述其間的差異
> flannel(overlay, assigning ip like 10.42.*.*, 10.43.*.*), calico(support and have to NetworkPolicy), canel(calino overlay; flannel mentioned above), Weave...
<br> <del> Pod networking: <br>* Flat Routed Network: routing inside physical network<br> * Overlay: tunnel for standing out clusters  <del>
17. kubernetes如何實現node之間的通訊
> As worker nodes, they shares node states, health by kubelet and kube-proxy, and system critical info by etcd. Master nodes run an apiserver to access the point to the k8s cluster state ( stored in etcd ).
18. 承上題，當在node A的service A需要與node B的service B或node A上的service C通訊時，封包所經過的路徑分別為何
> [Website with animation of explanation](https://sookocheff.com/post/kubernetes/understanding-kubernetes-networking-model/) <br> **Node A service A - Node B service B**: A - router - eth0 - VXLAN or tunnel(overlay) or physical network routing(proxy) - eth1 - router - B<br>
**Node A service A - Node A service C**: A - router (proxy) - C
19. 如果有部分服務無法部署在kubernetes中，要如何將其表示為一個普通的Service，使kubernetes中的其他服務無須寫死IP和port
> with selector, it creates endpoint automatically. To connect to svc in k8s, it could be achieved by creating endpoint by yaml  k8s service and applying the endpoint in the svc.
20. 解釋headless service
> A headless service is a service with a service IP but instead of load-balancing it will return the IPs of our associated Pods. This allows us to interact directly with the Pods instead of a proxy. Just specify `.spec.clusterIP` as `None`.
21. 現有一service-a，我希望只有service-b能夠存取，kubernetes內的其他服務則均不可連接到service-a，請問如何實現
> NetworkPolicy (egress connect specific ips, ingress be connected specific ips) <br>
<del> RBAC? Service Account? <del>
22. 請說明StorageClass, PersistentVolume, PersistentVolumeClaim之間的關係
> **PersistentVolume** defines based on StorageClass. pvc is a request from a user, similar to pods.<br>
When none of the static PVs the administrator created match a user's PersistentVolumeClaim, to enable dynamic storage provisioning, the cluster administrator should enable DefaultStorageClass. <br>**PersistentVolume** have two reclaim policies: Retain & Delete. Default policy would be Delete to achieve dynamic provisioning. To recover precious data from `released` state manually after deleted, pv's retain policy should be defined to `Retain` 
```
# Choose one of your PersistentVolumes and change its reclaim policy:
kubectl patch pv <your-pv-name> -p '{"spec":{"persistentVolumeReclaimPolicy":"Retain"}}'
```
> pv: 已定義位置的空間, pvc: 動態配置指定的大小和pv, StorageClass: globally all kinds of storage
23. 請說明ServiceAccount, Role, RoleBinding之間的關係
##### [swpc in dgx2 management config](https://gitlab-k8s.wzs.wistron.com.cn/bigdata-server-admin/rke-dgx2-cluster/tree/master)
> RoleBinding將定義好的role指定給特定ServiceAccount <br> **Role** always set permission within particular namespace, (Role **namespaced** and ClusterRole **not-namespaced**); <br> A **Role Binding** grants the permissions defined in a Role to a user or set of users;<br>**ServiceAccount** is for managing API in k8s. In any service, default parts were defined in its belonging ServiceAccount. ServiceAccount is also a subject for RoleBinding to bind just like User, Group in subject.
```
Note:
1. system:serviceaccount: (singular) is the prefix for service account usernames.
system:serviceaccounts = (system:authenticated): (plural) is the prefix for service account groups

2. All of the default ClusterRoles and ClusterRoleBindings
are labeled with kubernetes.io/bootstrapping=rbac-defaults.

3. To opt out of this reconciliation, set the rbac.authorization.kubernetes.io/autoupdate annotation 
on a default cluster role or rolebinding to false. 
Be aware that missing default permissions and subjects can result in non-functional clusters.
```
24. 為何我們需要ServiceAccount
> 以區分各使用者的權限 & authentication of all kinds of API 
25. 如何更新ServiceAccount的token
> Delete matched secret, it would auto create new ones <br>
<del> Recommended by K8s, it's better to delete and create a new one with new token<del>
26. 如何禁止使用hostPath
##### [release hostPath in specific directory for promtail](https://gitlab-k8s.wzs.wistron.com.cn/lita/server-setup/blob/master/logging/promtail-swpc/podsecuritypolicy.yaml)
##### [hostPath forbidden on dgx2 in gitlab](https://gitlab-k8s.wzs.wistron.com.cn/bigdata-server-admin/rke-dgx2-cluster/blob/master/policy/podsecuritypolicy.yaml)
> by defining podsecuritypolicy
27. 現有一駭客攔截你與kube-apiserver之間的通訊，他是否可以獲得你存取kubernetes所使用的token明文
> certificate-authority-data, client-certificate-data in kubeconfig have already been encoded. Without decode key from k8s, hackers could not get the token for accessing k8s cluster. 
28. 如果我使用etcd備份回復，現有的kubernetes cluster可能會發生什麼變化
> sync to etcd state
29. 試舉出kubernetes的限制和缺點
30. 如果有多個使用者想要用kubernetes，你會如何切分隔離這些使用者。試舉出至少兩種方法和其利弊
31. CNI, CSI, CRI分別代表什麼
> Container Network, Storage, Runtime Interface
32. 列出三個除了docker以外的container runtime
> containerd
