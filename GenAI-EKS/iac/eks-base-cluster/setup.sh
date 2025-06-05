terraform init
terraform apply -auto-approve -var-file=dev.tfvars
export EKS_NODE_ROLE=$(terraform output -json | jq -r '."eks_node_role".value')
echo $EKS_NODE_ROLE