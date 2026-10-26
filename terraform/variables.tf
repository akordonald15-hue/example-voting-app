variable "aws_profile" {
  type    = string
  default = "capstone"
}
variable "project_name" {
  type    = string
  default = "devops-capstone-k3s"
  validation {
    condition     = can(regex("^[a-z][a-z0-9-]{2,39}$", var.project_name))
    error_message = "Use 3-40 lowercase letters, digits and hyphens, starting with a letter."
  }
}
variable "subnet_id" {
  description = "Explicit existing default subnet in eu-west-1."
  type        = string
  default     = "subnet-0cfe9064bc272550c"
}
variable "ami_id" {
  description = "Pinned Canonical Ubuntu 24.04 amd64 AMI discovered in Ireland."
  type        = string
  default     = "ami-03c066fbf8c68378e"
}
variable "instance_type" {
  type    = string
  default = "t3.medium"
  validation {
    condition     = contains(["t3.medium", "t3.large", "t3.xlarge", "m6i.xlarge"], var.instance_type)
    error_message = "Select a reviewed x86_64 instance type."
  }
}
variable "root_volume_gib" {
  type    = number
  default = 30
  validation {
    condition     = var.root_volume_gib >= 30 && var.root_volume_gib <= 100 && floor(var.root_volume_gib) == var.root_volume_gib
    error_message = "Disk must be a whole number from 30 to 100 GiB. Shrinking is not supported."
  }
}
variable "approve_public_egress" {
  description = "Require explicit approval of public IPv4 outbound networking before provisioning."
  type        = bool
  default     = false
}
