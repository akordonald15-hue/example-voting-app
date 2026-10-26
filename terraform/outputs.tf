output "instance_id" {
  value = aws_instance.node.id
}
output "availability_zone" {
  value = aws_instance.node.availability_zone
}
output "vpc_id" {
  value = data.aws_vpc.default.id
}
output "ssm_tunnel_command" {
  value = "aws ssm start-session --target ${aws_instance.node.id} --document-name AWS-StartPortForwardingSession --parameters portNumber=6443,localPortNumber=16443 --profile ${var.aws_profile} --region eu-west-1"
}
