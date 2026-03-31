output "public_ip" {
  description = "The public IP address of the origin server"
  value       = aws_instance.origin.public_ip
}
