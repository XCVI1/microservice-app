{{- define "core-service.name" -}}
{{ .Chart.Name }}
{{- end }}

{{- define "core-service.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}
