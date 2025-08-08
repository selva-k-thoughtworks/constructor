This repo is the constructor, which holds the terraform code to create s3 bucket and IAM Role with policy - which allow PUT action on the bucket created.  

<img width="2098" height="1116" alt="image" src="https://github.com/user-attachments/assets/1fef9248-0072-4d37-bc57-353aa73f7929" />

As per the image which is the repo on the right. 

So the **DataProduct** repo can trigger the workflow to create the resources defined **only** with the **config.yaml** file.

<h3> Config </h3>
The sample config is as below

<br/> <br/>

```
project: selva-project
buckets:
- name: logs
  iam_role_name: writer-role-logs
  write_prefix: FOOBAR/logs/
  prefix: selva-logs
```
<br/> <br/>

| Field                      | Details                                |
|----------------------------|----------------------------------------|
| project                    | Name of the dataproduct without space <br> you can use "-" |
| buckets                    | List                                   |
| buckets.name               | Name of the s3 bucket to create        |
| buckets.iam_role_name      | Name of the IAM role to create         | 
| buckets.write_prefix       | The path access in the s3 bucket       |
| buckets.prefix             | Prefix to be added for s3 bucket       | 

<h3>Validation </h3>

It does basic validation of the config in case if the Dataproduct passes wrong config it throws an error. 

<h4>Sample error </h4>

<img width="1976" height="1518" alt="image" src="https://github.com/user-attachments/assets/38040ae2-cecf-4d41-bb7b-4b3f2994fe39" />

<br/> <br/>

<h3>Successful deployment</h3>

In case of successful deployment, it provides the summary of resources created.

<img width="2338" height="1668" alt="image" src="https://github.com/user-attachments/assets/be6e4c91-398e-4770-bdde-0b87b55edd30" />

<h4> Reference: </h4>

- https://github.com/selva-k-thoughtworks/data-product-1

