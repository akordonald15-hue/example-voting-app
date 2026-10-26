{{- define "robot.image" -}}
{{- if ne .root.Release.Namespace "robot-shop" }}{{ fail "STOP: Robot Shop namespace only" }}{{ end }}
{{- if or .root.Values.nodeport .root.Values.ocCreateRoute }}{{ fail "STOP: public exposure is not approved" }}{{ end }}
{{- if and .root.Values.localDemo (hasKey .root.Values.localImages .name) }}
{{- $local := index .root.Values.localImages .name }}
{{- if ne $local (printf "capstone2-%s:local" .name) }}{{ fail "only fixed local rehearsal image names permitted" }}{{ end }}
{{- printf "docker.io/library/%s" $local | quote -}}
{{- else }}
{{- $ref := required (printf "review and pin Robot Shop image %s" .name) (index .root.Values.images .name) }}
{{- if not (regexMatch "^[a-z0-9./:_-]+@sha256:[a-f0-9]{64}$" $ref) }}{{ fail "immutable image required" }}{{ end }}
{{- $ref | quote -}}
{{- end }}
{{- end -}}
