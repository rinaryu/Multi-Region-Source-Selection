terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  alias  = "useast1"
  region = "us-east-1"
}

provider "aws" {
  alias  = "uswest2"
  region = "us-west-2"
}

provider "aws" {
  alias  = "eucentral1"
  region = "eu-central-1"
}

# --- Origin Servers ---
module "origin_us_east_1" {
  source        = "../origin"
  region_name   = "us-east-1"
  instance_type = var.instance_type
  key_name      = var.key_name
  providers     = { aws = aws.useast1 }
}

module "origin_us_west_2" {
  source        = "../origin"
  region_name   = "us-west-2"
  instance_type = var.instance_type
  key_name      = var.key_name
  providers     = { aws = aws.uswest2 }
}

module "origin_eu_central_1" {
  source        = "../origin"
  region_name   = "eu-central-1"
  instance_type = var.instance_type
  key_name      = var.key_name
  providers     = { aws = aws.eucentral1 }
}

# --- Distributed Client Nodes ---
module "client_us_east_1" {
  source        = "../origin"
  region_name   = "client-us-east-1"
  instance_type = var.instance_type
  key_name      = var.key_name
  providers     = { aws = aws.useast1 }
}

module "client_us_west_2" {
  source        = "../origin"
  region_name   = "client-us-west-2"
  instance_type = var.instance_type
  key_name      = var.key_name
  providers     = { aws = aws.uswest2 }
}

module "client_eu_central_1" {
  source        = "../origin"
  region_name   = "client-eu-central-1"
  instance_type = var.instance_type
  key_name      = var.key_name
  providers     = { aws = aws.eucentral1 }
}
