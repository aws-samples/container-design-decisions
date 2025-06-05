terraform {
  required_version = ">= 1.10.2"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.81"
    }

    random = {
      source  = "hashicorp/random"
      version = "~>3.0"
    }

    time = {
      source  = "hashicorp/time"
      version = "~> 0.7"
    }    
  }
}

provider "aws" {
  region = "ap-southeast-2"
  default_tags {
    tags = {
      Managedby = "fmamazon"
      Environment = "genai-eks"
      cluster-name  = "${var.cluster_name}"
    }
  }
}