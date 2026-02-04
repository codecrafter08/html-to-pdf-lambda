# Build and push docker image from code

```sh

aws ecr get-login-password --region <your-region> --profile <your-profile> | docker login --username AWS --password-stdin <account-id>.dkr.ecr.<region>.amazonaws.com

docker buildx build --platform linux/amd64 -t htmltopdf-lambda:<tag> .
docker image tag htmltopdf-lambda:<tag> <account-id>.dkr.ecr.<region>.amazonaws.com/htmltopdf-lambda:<tag>
docker image push <account-id>.dkr.ecr.<region>.amazonaws.com/htmltopdf-lambda:<tag>
```