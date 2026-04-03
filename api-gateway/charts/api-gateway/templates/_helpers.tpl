{{- define "api-gateway.name" -}}
{{ .Chart.Name }}
{{- end }}

{{- define "api-gateway.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}

{{- define "api-gateway.chart" -}}
{{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}
