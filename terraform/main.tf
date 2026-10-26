resource "aws_instance" "node" {
  ami                         = data.aws_ami.selected.id
  instance_type               = var.instance_type
  subnet_id                   = data.aws_subnet.selected.id
  vpc_security_group_ids      = [aws_security_group.node.id]
  associate_public_ip_address = true
  iam_instance_profile        = aws_iam_instance_profile.node.name
  user_data                   = file("${path.module}/cloud-init.yaml")
  user_data_replace_on_change = true
  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 1
  }
  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.root_volume_gib
    encrypted             = true
    delete_on_termination = true
    tags                  = { Project = var.project_name, ManagedBy = "Terraform" }
  }
  dynamic "credit_specification" {
    for_each = startswith(var.instance_type, "t3.") ? [1] : []
    content {
      cpu_credits = "standard"
    }
  }
  tags       = { Name = var.project_name }
  depends_on = [aws_iam_role_policy_attachment.ssm]
  lifecycle {
    precondition {
      condition     = var.approve_public_egress
      error_message = "Public IPv4 outbound networking requires explicit approval before provisioning."
    }
    precondition {
      condition     = data.aws_subnet.selected.vpc_id == data.aws_vpc.default.id
      error_message = "Subnet must belong to the existing default VPC."
    }
    precondition {
      condition     = data.aws_subnet.selected.default_for_az
      error_message = "Select a verified default subnet."
    }
  }
}
