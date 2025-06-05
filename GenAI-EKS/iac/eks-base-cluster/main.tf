# locals {
#   private_subnet_ids       = data.terraform_remote_state.vpc.outputs.private_subnet_ids
# }



module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.31"

  cluster_name    = var.cluster_name
  cluster_version = "1.32"

  # Optional
  cluster_endpoint_public_access = true

  # Optional: Adds the current caller identity as an administrator via cluster access entry
  enable_cluster_creator_admin_permissions = true

  authentication_mode = "API"

  cluster_compute_config = {
    enabled    = true
    node_pools = ["general-purpose"]
  }

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cloudwatch_log_group_retention_in_days = 1
  cluster_security_group_description = format(
  "EKS cluster [%s] security group",
  var.cluster_name
  )



  tags = merge(
    var.tags,

    {
      "Name" : local.name,
      "Environment" : terraform.workspace
      "provisioned-by" : "fm-eks"
      Environment = "dev"
      Terraform   = "true"    
      "cluster-name" = var.cluster_name  
    }
  )
}



resource "null_resource" "wait_10_seconds" {
  provisioner "local-exec" {
    command = "sleep 10"
  }

  depends_on = [module.eks]
}

resource "null_resource" "update_kubeconfig" {
  provisioner "local-exec" {
    command = "aws eks update-kubeconfig --name ${var.cluster_name} --region ${var.region}"
  }

  depends_on = [module.eks, null_resource.wait_10_seconds]
}


output "eks_cluster_name" {
  value = module.eks.cluster_name
  
}

output "eks_node_sg_id" {
  value = module.eks.node_security_group_id
  
}

output "eks_node_role" {
  value = module.eks.node_iam_role_name
  
}



