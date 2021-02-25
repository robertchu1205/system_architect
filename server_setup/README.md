# Install Nvidia Driver
```sh
# disable nouveau driver before install nvidia driver
blacklist nouveau
options nouveau modeset=0

sudo apt-get update
sudo apt-get install -y dkms
sudo update-initramfs -u
sudo shutdown -r now

curl -fsSL -O http://us.download.nvidia.com/XFree86/Linux-x86_64/390.87/NVIDIA-Linux-x86_64-390.87.run
sudo sh ./NVIDIA-Linux-x86_64-390.87.run --dkms

nvidia-smi  # confirm that driver is installed
```
# Install Docker
```sh
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce
sudo systemctl status docker
```
# Install Nvidia Docker
```sh
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2 jq
sudo pkill -SIGHUP dockerd

# Set default proxy for docker
cat <<EOF > /etc/systemd/system/docker.service.d/http-proxy.conf
[Service]
Environment="HTTP_PROXY=${http_proxy}
Environment="HTTPS_PROXY=${https_proxy}
EOF

sudo systemctl daemon-reload
sudo systemctl show --property Environment docker  # confirm proxy is set

# Set default runtime to nvidia
sudo jq '. + { "default-runtime": "nvidia" }' /etc/docker/daemon.json > /etc/docker/daemon.json

sudo systemctl restart docker
sudo docker run --rm nvidia/cuda:9.0-base nvidia-smi  # confirm nvidia runtime is used by default
```
# Install Kubernetes
```sh
swapoff -a
# Install kubeadm, kubelet and kubectl
apt-get update && apt-get install -y apt-transport-https curl
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
cat <<EOF >/etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF
apt-get update
apt-get install -y kubelet kubeadm kubectl
apt-mark hold kubelet kubeadm kubectl
```