terraform {
  required_version = ">= 1.15.0, < 2.0.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 6.0" }
  }
}
provider "aws" {
  profile = var.aws_profile
  region  = "eu-west-1"
  default_tags { tags = { Project = "devops-capstone-k3s", ManagedBy = "Terraform" } }
}
