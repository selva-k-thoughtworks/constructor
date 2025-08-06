variable "buckets" {
  type = list(object({
    name           = string
    prefix         = string
    iam_role_name  = string
    write_prefix   = string
  }))
}
