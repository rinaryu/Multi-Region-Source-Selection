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

# Deploy Origin to US East 1
module "origin_us_east_1" {
  source        = "../origin"
  region_name   = "us-east-1"
  instance_type = var.instance_type
  key_name      = var.key_name

  providers = {
    aws = aws.useast1
  }
}

# Deploy Origin to US West 2
module "origin_us_west_2" {
  source        = "../origin"
  region_name   = "us-west-2"
  instance_type = var.instance_type
  key_name      = var.key_name

  providers = {
    aws = aws.uswest2
  }
}

# Deploy Origin to EU Central 1
module "origin_eu_central_1" {
  source        = "../origin"
  region_name   = "eu-central-1"
  
  # eu-central-1 sometimes has limited t2.micro capacity in newer accounts, 
  # but t2.micro is often still the free tier default. If it fails, users can switch to t3.micro.
  instance_type = var.instance_type
  key_name      = var.key_name

  providers = {
    aws = aws.eucentral1
  }
}
