terraform {
  required_version = ">= 1.6.0"
  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.30"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.13"
    }
  }
}

provider "kubernetes" {
  config_path = var.kubeconfig_path
}

provider "helm" {
  kubernetes {
    config_path = var.kubeconfig_path
  }
}

resource "kubernetes_namespace" "xeip" {
  metadata {
    name = var.namespace
  }
}

resource "helm_release" "xeip" {
  name       = "xeip"
  namespace  = kubernetes_namespace.xeip.metadata[0].name
  chart      = "../helm/xeip"
  dependency_update = false
}

