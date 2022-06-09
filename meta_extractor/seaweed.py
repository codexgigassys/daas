from pyseaweed import WeedFS

seaweedfs = WeedFS('seaweedfs_master', 9333)
# Comment the line above and uncomment the line below to work with k8s cluster
# seaweedfs = WeedFS('seaweedfs-master', 9333)
