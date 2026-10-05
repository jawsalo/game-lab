{{- define "game-lab.name" -}}
{{- default .Chart.Name .Values.platform.name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "game-lab.labels" -}}
app.kubernetes.io/name: {{ include "game-lab.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
app.kubernetes.io/part-of: {{ .Values.platform.name }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end -}}

{{- define "game-lab.webHost" -}}
{{- if .Values.modules.web.hostname -}}
{{- .Values.modules.web.hostname -}}
{{- else -}}
{{- printf "%s.%s" .Values.modules.web.subdomain .Values.platform.baseDomain -}}
{{- end -}}
{{- end -}}
