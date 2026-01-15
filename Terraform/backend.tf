terraform {
  backend "remote" {
    organization = "allenac86"

    workspaces {
      name = "spooky-days-gpt"
    }
  }
}