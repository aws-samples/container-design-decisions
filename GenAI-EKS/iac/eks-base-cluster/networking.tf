
data "aws_availability_zones" "available" {
  state = "available"
}




locals {
  common_tags = {
    # Name      = "06"
    Project   = "tf-test-06"
    Managedby = "tf"
  }

  # name            = "${var.shared_config.resources_prefix}-${terraform.workspace}"
  name            = "${var.shared_config.resources_prefix}"
  azs             = slice(data.aws_availability_zones.available.names, 0, 2)
  private_subnets = [for k, v in module.subnets.network_cidr_blocks : v if endswith(k, "/private")]
  public_subnets  = [for k, v in module.subnets.network_cidr_blocks : v if endswith(k, "/public")]

  vpc_cidr_prefix = tonumber(split("/", var.vpc_cidr)[1])

  tags = merge(
    var.tags,
    {
      "Name" : local.name,
      "Environment" : terraform.workspace
      "provisioned-by" : "fm-eks"
    }
  )
}

module "subnets" {
  source  = "hashicorp/subnets/cidr"
  version = "1.0.0"

  base_cidr_block = var.vpc_cidr
  networks = concat(
    [for k, v in local.azs : tomap({ "name" = "${v}/private", "new_bits" = var.private_subnets_cidr_prefix - local.vpc_cidr_prefix })],
    [for k, v in local.azs : tomap({ "name" = "${v}/public", "new_bits" = var.public_subnets_cidr_prefix - local.vpc_cidr_prefix })],
  )
}

module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1"

  name = local.name
  cidr = var.vpc_cidr
  azs  = local.azs

  private_subnets = local.private_subnets
  public_subnets  = local.public_subnets

  public_subnet_tags = {
    "kubernetes.io/role/elb" = 1
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = 1
    # Tags subnets for Karpenter auto-discovery
    "karpenter.sh/discovery" = local.name
  }

  enable_nat_gateway = true
  single_nat_gateway = true

  tags = merge(
    var.tags,

    {
      "Name" : local.name,
      "Environment" : terraform.workspace
      "provisioned-by" : "fm-eks"
      Environment = "dev"
      Terraform   = "true"
    }
  )
}


output "vpc_id" {
  value = module.vpc.vpc_id
  
}

output "private_subnet_ids" {
  value = module.vpc.private_subnets
  
}