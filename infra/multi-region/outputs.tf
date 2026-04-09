output "us_east_1_ip" {
  description = "Public IP of the US-East-1 Origin Server"
  value       = module.origin_us_east_1.public_ip
}

output "us_west_2_ip" {
  description = "Public IP of the US-West-2 Origin Server"
  value       = module.origin_us_west_2.public_ip
}

output "eu_central_1_ip" {
  description = "Public IP of the EU-Central-1 Origin Server"
  value       = module.origin_eu_central_1.public_ip
}

output "client_us_east_1_ip" {
  description = "Public IP of the US-East-1 Client Node"
  value       = module.client_us_east_1.public_ip
}

output "client_us_west_2_ip" {
  description = "Public IP of the US-West-2 Client Node"
  value       = module.client_us_west_2.public_ip
}

output "client_eu_central_1_ip" {
  description = "Public IP of the EU-Central-1 Client Node"
  value       = module.client_eu_central_1.public_ip
}
