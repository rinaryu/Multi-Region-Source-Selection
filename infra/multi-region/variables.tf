variable "key_name" {
  description = "The name of the SSH key pair to use for all instances (must exist in all regions, or be left empty if using EC2 Instance Connect)."
  type        = string
  default     = ""
}

variable "instance_type" {
  description = "The EC2 instance type to use. t3.micro is the default free tier for newer regions/accounts."
  type        = string
  default     = "t3.micro"
}
