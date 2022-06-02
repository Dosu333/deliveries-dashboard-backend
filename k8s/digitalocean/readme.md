# Digital Ocean Kubernetes Deploymment 

## Create a cluster 
## Install doctl 
```
brew install doctl
```

Create a DigitalOcean API token for your account with read and write access from the [Applications & API page](https://cloud.digitalocean.com/account/api/tokens) in the control panel. The token string is only displayed once, so save it in a safe place.

Use the API token to grant doctl access to your DigitalOcean account. Pass in the token string when prompted by doctl auth init, and give this authentication context a name.

```
doctl auth init --context <NAME>
doctl auth list
doctl auth switch --context <NAME>
doctl account get
```

A certificate is required to authenticate, it lasts one week. You can either automatically refresh the certificate or manually update it weekly.
Automatically renew your clusters certificate.
```
doctl kubernetes cluster kubeconfig save <cluster id>
```


