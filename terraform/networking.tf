data "aws_vpc" "default" {
  default = true
}
data "aws_subnet" "selected" {
  id = var.subnet_id
}
data "aws_ami" "selected" {
  owners = ["099720109477"] # Canonical public AMI publisher, not the user's account.
  filter {
    name   = "image-id"
    values = [var.ami_id]
  }
  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}
