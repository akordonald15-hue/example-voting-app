variable "aws_profile" { default = "capstone" }
variable "subnet_id" { type = string }
variable "server_security_group_id" { type = string }
variable "server_private_ip" { type = string }
variable "instance_profile_name" { type = string }
variable "ami_id" { type = string }
variable "instance_type" {
  default = "m7i.xlarge"
  validation {
    condition     = contains(["m7i.xlarge", "t3.xlarge"], var.instance_type)
    error_message = "Only reviewed 4-vCPU/16-GiB types are permitted."
  }
}
variable "approve_worker_public_egress" {
  type        = bool
  default     = false
  description = "Review gate for worker spend and public IPv4 egress; not authorization to apply."
}
