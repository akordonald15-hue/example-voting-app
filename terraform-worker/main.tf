data "aws_subnet" "worker" { id = var.subnet_id }
data "aws_vpc" "existing" { id = data.aws_subnet.worker.vpc_id }
data "aws_security_group" "server" { id = var.server_security_group_id }
data "aws_ami" "worker" {
  owners = ["099720109477"]
  filter {
    name   = "image-id"
    values = [var.ami_id]
  }
}
resource "aws_security_group" "worker" {
  name_prefix = "capstone2-worker-"
  description = "Private K3s worker; no public ingress or SSH"
  vpc_id      = data.aws_subnet.worker.vpc_id
}
resource "aws_vpc_security_group_egress_rule" "internet" {
  for_each          = toset(["80", "443"])
  security_group_id = aws_security_group.worker.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = tonumber(each.value)
  to_port           = tonumber(each.value)
}
resource "aws_vpc_security_group_egress_rule" "dns" {
  for_each          = toset(["tcp", "udp"])
  security_group_id = aws_security_group.worker.id
  cidr_ipv4         = "${cidrhost(data.aws_vpc.existing.cidr_block, 2)}/32"
  ip_protocol       = each.value
  from_port         = 53
  to_port           = 53
}
resource "aws_vpc_security_group_egress_rule" "time" {
  security_group_id = aws_security_group.worker.id
  cidr_ipv4         = "169.254.169.123/32"
  ip_protocol       = "udp"
  from_port         = 123
  to_port           = 123
}
locals {
  server_in = { api = { protocol = "tcp", port = 6443 }, vxlan = { protocol = "udp", port = 8472 }, kubelet = { protocol = "tcp", port = 10250 } }
  worker_in = { vxlan = { protocol = "udp", port = 8472 }, kubelet = { protocol = "tcp", port = 10250 } }
}
resource "aws_vpc_security_group_ingress_rule" "server_from_worker" {
  for_each                     = local.server_in
  security_group_id            = var.server_security_group_id
  referenced_security_group_id = aws_security_group.worker.id
  ip_protocol                  = each.value.protocol
  from_port                    = each.value.port
  to_port                      = each.value.port
  description                  = "Private Capstone2 worker ${each.key}; no public ingress"
}
resource "aws_vpc_security_group_egress_rule" "worker_to_server" {
  for_each                     = local.server_in
  security_group_id            = aws_security_group.worker.id
  referenced_security_group_id = var.server_security_group_id
  ip_protocol                  = each.value.protocol
  from_port                    = each.value.port
  to_port                      = each.value.port
}
resource "aws_vpc_security_group_ingress_rule" "worker_from_server" {
  for_each                     = local.worker_in
  security_group_id            = aws_security_group.worker.id
  referenced_security_group_id = var.server_security_group_id
  ip_protocol                  = each.value.protocol
  from_port                    = each.value.port
  to_port                      = each.value.port
}
resource "aws_vpc_security_group_egress_rule" "server_to_worker" {
  for_each                     = local.worker_in
  security_group_id            = var.server_security_group_id
  referenced_security_group_id = aws_security_group.worker.id
  ip_protocol                  = each.value.protocol
  from_port                    = each.value.port
  to_port                      = each.value.port
}
resource "aws_instance" "worker" {
  ami                         = data.aws_ami.worker.id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [aws_security_group.worker.id]
  associate_public_ip_address = true
  iam_instance_profile        = var.instance_profile_name
  user_data                   = templatefile("${path.module}/cloud-init.yaml.tftpl", { server_ip = var.server_private_ip })
  user_data_replace_on_change = true
  metadata_options {
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }
  root_block_device {
    volume_type           = "gp3"
    volume_size           = 50
    encrypted             = true
    delete_on_termination = true
  }
  dynamic "credit_specification" {
    for_each = startswith(var.instance_type, "t3.") ? [1] : []
    content { cpu_credits = "standard" }
  }
  tags = { Name = "capstone2-worker", CleanupDeadline = "2026-10-27T10:00:00Z" }
  lifecycle {
    precondition {
      condition     = var.approve_worker_public_egress
      error_message = "Explicit review of worker spend/public egress required."
    }
    precondition {
      condition     = data.aws_security_group.server.vpc_id == data.aws_subnet.worker.vpc_id && data.aws_subnet.worker.default_for_az
      error_message = "Worker must use the reviewed default subnet in the server VPC."
    }
  }
}
output "worker_id" { value = aws_instance.worker.id }
