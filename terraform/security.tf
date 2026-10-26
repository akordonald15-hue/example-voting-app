resource "aws_security_group" "node" {
  name_prefix = "${var.project_name}-"
  description = "K3s lab: no inbound ports; administration through SSM"
  vpc_id      = data.aws_vpc.default.id
}
resource "aws_vpc_security_group_egress_rule" "https" {
  security_group_id = aws_security_group.node.id
  description       = "SSM, registries and pinned release downloads"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 443
  to_port           = 443
}
resource "aws_vpc_security_group_egress_rule" "http" {
  security_group_id = aws_security_group.node.id
  description       = "Ubuntu bootstrap package repositories"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "tcp"
  from_port         = 80
  to_port           = 80
}
resource "aws_vpc_security_group_egress_rule" "dns" {
  for_each          = toset(["tcp", "udp"])
  security_group_id = aws_security_group.node.id
  description       = "VPC DNS resolver"
  cidr_ipv4         = "${cidrhost(data.aws_vpc.default.cidr_block, 2)}/32"
  ip_protocol       = each.value
  from_port         = 53
  to_port           = 53
}
resource "aws_vpc_security_group_egress_rule" "time" {
  security_group_id = aws_security_group.node.id
  description       = "Amazon Time Sync"
  cidr_ipv4         = "169.254.169.123/32"
  ip_protocol       = "udp"
  from_port         = 123
  to_port           = 123
}
data "aws_partition" "current" {}
resource "aws_iam_role" "node" {
  name_prefix = "${var.project_name}-"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Action    = "sts:AssumeRole"
      Principal = { Service = "ec2.amazonaws.com" }
    }]
  })
}
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.node.name
  policy_arn = "arn:${data.aws_partition.current.partition}:iam::aws:policy/AmazonSSMManagedInstanceCore"
}
resource "aws_iam_instance_profile" "node" {
  name_prefix = "${var.project_name}-"
  role        = aws_iam_role.node.name
}
