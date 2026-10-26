{{- define "voting.fullname" -}}
{{- $name := printf "%s-%s" .Release.Name .Chart.Name -}}
{{- if gt (len $name) 40 -}}
{{- printf "%s-%s" ($name | trunc 31 | trimSuffix "-") ($name | sha256sum | trunc 8) -}}
{{- else -}}
{{- $name -}}
{{- end -}}
{{- end -}}
{{- define "voting.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | quote }}
{{- end -}}
{{- define "voting.selector" -}}
app.kubernetes.io/instance: {{ .root.Release.Name }}
app.kubernetes.io/name: {{ .root.Chart.Name }}
app.kubernetes.io/component: {{ .component }}
{{- end -}}
{{- define "voting.image" -}}
{{- if .digest -}}
{{- printf "%s@%s" .repository .digest -}}
{{- else -}}
{{- if eq .tag "latest" -}}{{ fail "latest image tags are forbidden; use a version tag or digest" }}{{- end -}}
{{- printf "%s:%s" .repository .tag -}}
{{- end -}}
{{- end -}}
