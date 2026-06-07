output "namespace" {
  value = kubernetes_namespace.xeip.metadata[0].name
}
