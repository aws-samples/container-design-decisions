variable "cluster_name" {
  description = "The name of the EKS cluster"
  type        = string
  validation {
    condition     = length(var.cluster_name) > 0
    error_message = "The cluster name must not be an empty string"
  }

}

variable "region" {
  description = "The AWS region where the EKS cluster will be deployed"
  type        = string
  default     = "ap-southeast-2"
}


variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}


variable "private_subnets_cidr_prefix" {
  description = "CIDR prefix for the private subnets"
  type        = number
  default     = 20
}

variable "public_subnets_cidr_prefix" {
  description = "CIDR prefix for the public subnets"
  type        = number
  default     = 24
}

variable "subnet_cidrs" {
  description = "The CIDR blocks for the subnets"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}


variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}

variable "shared_config" {
  description = "Shared configuration across all modules/folders"
  type        = map(any)
  default     = {}
}

