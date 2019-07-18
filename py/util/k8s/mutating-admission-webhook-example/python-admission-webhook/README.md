## Prereqs
Kubernetes 1.9.0 or above with the admissionregistration.k8s.io/v1beta1 API enabled. Verify that by the following command:

$ kubectl api-versions | grep admissionregistration.k8s.io/v1beta1

The result should be:
admissionregistration.k8s.io/v1beta1

In addition, the MutatingAdmissionWebhook and ValidatingAdmissionWebhook admission controllers should be added and listed in the correct order in the admission-control flag of kube-apiserver.

Certificate and key signed by the cluster CA with the correct hostname/ips

