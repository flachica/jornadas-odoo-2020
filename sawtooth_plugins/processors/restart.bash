kubectl delete pod $(kubectl get pod --all-namespaces | grep sawtooth | awk '{print $2}') -n sawtooth --force --grace-period=0
