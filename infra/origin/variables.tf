variable "region_name" {
  description = "The name of the region (used for naming/tagging resources)"
  type        = string
}

variable "instance_type" {
  description = "The EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "The name of the SSH key pair to use for the instance. Leave empty if using EC2 Instance Connect."
  type        = string
  default     = ""
}
