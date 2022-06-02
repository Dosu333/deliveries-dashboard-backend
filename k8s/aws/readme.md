# Setup AWS KOPS

## Set necessary env variable and create group

```bash
AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export AWS_DEFAULT_REGION=us-east-2
aws iam create-group --group-name kops
```

The response is as follows

```json
{
    "Group": {
        "Path": "/",
        "GroupName": "kops",
        "GroupId": "AGPAX43GMNUGJ3EL62GJE",
        "Arn": "arn:aws:iam::542991215884:group/kops",
        "CreateDate": "2021-10-23T09:43:17+00:00"
    }
}
```

Next, we’ll assign a few policies to the group thus providing the future users of the group with sufficient permissions to create the objects we’ll need. Since our cluster will consist of EC2 instances, the group will need to have the permissions to create and manage them. We’ll need a place to store the state of the cluster so we’ll need access to S3. Furthermore, we need to add VPCs to the mix so that our cluster is isolated from prying eyes. Finally, we’ll need to be able to create additional IAMs.

```bash
aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess --group-name kops
aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess --group-name kops
aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/AmazonVPCFullAccess --group-name kops
aws iam attach-group-policy --policy-arn arn:aws:iam::aws:policy/IAMFullAccess --group-name kops
```

## Create a user

Now that we have a group with the sufficient permissions, we should create a user as well

```bash
aws iam create-user --user-name kops
```

The response is as follows:

```json
{
    "User": {
        "Path": "/",
        "UserName": "kops",
        "UserId": "AIDAX43GMNUGF4SXFLQSL",
        "Arn": "arn:aws:iam::542991215884:user/kops",
        "CreateDate": "2021-10-23T09:50:49+00:00"
    }
}
```

The user we created does not yet belong to the kops group, add the user to the group

```bash
aws iam add-user-to-group --user-name kops --group-name kops
```

Finally, we’ll need access keys for the newly created user. Without them, we would not be able to act on its behalf.

```bash
aws iam create-access-key --user-name kops > aws-kops-creds
cat aws-kops-creds
```

We need the SecretAccessKey and AccessKeyId entries. So, the next step is to parse the content of the aws-kops-creds file and store those two values as the environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY.

In the spirit of full automation, we’ll use jq to parse the contents of the aws-kops-creds file. Please download and install the distribution suited for your OS.

```bash
export AWS_ACCESS_KEY_ID=$(cat aws-kops-creds | jq -r '.AccessKey.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(cat aws-kops-creds | jq -r '.AccessKey.SecretAccessKey')
```

We used cat to output contents of the file and combined it with jq to filter the input so that only the field we need is retrieved.
From now on, all the AWS CLI commands will not be executed by the administrative user you used to register to AWS, but as kops

## Availability zones setup

```bash
aws ec2 describe-availability-zones --region $AWS_DEFAULT_REGION
```

The output

```json
{
    "AvailabilityZones": [
        {
            "State": "available",
            "OptInStatus": "opt-in-not-required",
            "Messages": [],
            "RegionName": "us-east-2",
            "ZoneName": "us-east-2a",
            "ZoneId": "use2-az1",
            "GroupName": "us-east-2",
            "NetworkBorderGroup": "us-east-2",
            "ZoneType": "availability-zone"
        },
        {
            "State": "available",
            "OptInStatus": "opt-in-not-required",
            "Messages": [],
            "RegionName": "us-east-2",
            "ZoneName": "us-east-2b",
            "ZoneId": "use2-az2",
            "GroupName": "us-east-2",
            "NetworkBorderGroup": "us-east-2",
            "ZoneType": "availability-zone"
        },
        {
            "State": "available",
            "OptInStatus": "opt-in-not-required",
            "Messages": [],
            "RegionName": "us-east-2",
            "ZoneName": "us-east-2c",
            "ZoneId": "use2-az3",
            "GroupName": "us-east-2",
            "NetworkBorderGroup": "us-east-2",
            "ZoneType": "availability-zone"
        }
    ]
}
```

As we can see, the region has three availability zones. We’ll store them in an environment variable.

For windows user:
Please use ```tr '\r\n' ', '``` instead of ```tr '\n' ','``` in the command that follows.

```bash
export ZONES=$(aws ec2 describe-availability-zones --region $AWS_DEFAULT_REGION | jq -r '.AvailabilityZones[].ZoneName' | tr '\n' ',' | tr -d ' ')
ZONES=${ZONES%?}
echo $ZONES
```

Just as with the access keys, we used jq to limit the results only to the zone names, and we combined that with tr that replaced new lines with commas. The second command removes the trailing comma. The output of the last command that echoed the values of the environment variable

## Create SSH Key

We create a new key pair, filtered the output so that only the KeyMaterial is returned, and stored it in the devops23.pem file. For security reasons, we should change the permissions of the devops23.pem file so that only the current user can read it. Finally, we’ll need only the public segment of the newly generated SSH key, so we’ll use ssh-keygen to extract it

```bash
aws ec2 create-key-pair --key-name devops23 | jq -r '.KeyMaterial' > devops23.pem
chmod 400 devops23.pem
ssh-keygen -y -f devops23.pem > devops23.pub
```

All those steps might look a bit daunting if this is your first contact with AWS. Nevertheless, they are pretty standard. No matter what you do in AWS, you’d need to perform, more or less, the same actions. Not all of them are mandatory, but they are good practices. Having a dedicated (non-admin) user and a group with only required policies is always a good idea. Access keys are necessary for any aws command. Without SSH keys, no one can interactively log in to a server.

The good news is that we’re finished with the prerequisites. In the next lesson, we can turn our attention towards creating a Kubernetes cluster.

