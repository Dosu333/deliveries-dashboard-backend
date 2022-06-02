# README
### Note: Add a secrets folder in k8s as it has been git-ignored 

## Build docker image 

```docker build . -t profmcdan/django-starter-api:v0 -f docker/prod/Dockerfile```

## if using docker-desktop, install and view the kube dashboard 
https://andrewlock.net/running-kubernetes-and-the-dashboard-with-docker-desktop/
```
kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.2.0/aio/deploy/recommended.yaml
kubectl patch deployment kubernetes-dashboard -n kubernetes-dashboard --type 'json' -p '[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--enable-skip-login"}]'
kubectl proxy

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.4.2/components.yaml
kubectl patch deployment metrics-server -n kube-system --type 'json' -p '[{"op": "add", "path": "/spec/template/spec/containers/0/args/-", "value": "--kubelet-insecure-tls"}]'

```

Open the dashboard here

http://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/#/login


## Run Deployment 
```
kubectl apply -f api/deployment-api.yaml
kubectl get deployments
kubectl get pods 
kubectl delete -f api/deployment-api.yaml
```
## Run Service 
```
kubectl delete -f api/service-api.yaml
kubectl get svc
kubectl delete -f api/service-api.yaml
```

## Run Database on Kubernetes
```
kubectl apply -f db/volume.yaml 
kubectl apply -f db/volume_claim.yaml 
kubectl apply -f db/secrets.yaml 
kubectl apply -f db/deployment.yaml
kubectl apply -f db/service.yaml
```

In order to create the database credentials: 
```
echo -n "admin" | base64
echo -n "StrongPass293word" | base64
```

```
kubectl get pv
kubectl get pvc
```

Delete these resources
```
kubectl delete -f db/service.yaml
kubectl delete -f db/deployment.yaml
kubectl delete -f db/secrets.yaml 
kubectl delete -f db/volume_claim.yaml 
kubectl delete -f db/volume.yaml 
```

Use the service name in the database host.

## Run Redis
```
kubectl apply -f redis/deployment.yaml
kubectl apply -f redis/service.yaml

```

## TL;DR;

```
$ kubectl apply -f secrets/
$ kubectl apply -f db/  # See dashboard in browser
$ kubectl apply -f redis/
$ kubectl apply -f api/
$ kubectl apply -f celery/
$ kubectl apply -f flower/
```

## Enable Ingress Controller 
if you are using minikube then run the following:
```
minikube addons list
minikube addons enable ingress
minikube tunnel

```