provider "aws" {
  region  = "eu-west-1"
  profile = var.aws_profile
  default_tags {
    tags = {
      Project   = var.project_name
      ManagedBy = "Terraform"
    }
  }
}
