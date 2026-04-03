{{- define "auth-service.name" -}}
{{ .Chart.Name }}
{{- end }}

{{- define "auth-service.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}
