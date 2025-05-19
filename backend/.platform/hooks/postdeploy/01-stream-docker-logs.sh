#!/bin/bash
# Robust CloudWatch log streaming for EB Docker (AL2023)
set -euo pipefail
IFS=$'\n\t'

log()  { echo "[${TZ:=UTC} $(date -u +'%Y-%m-%dT%H:%M:%SZ')] $*"; }
fail(){ echo "[${TZ:=UTC} $(date -u +'%Y-%m-%dT%H:%M:%SZ')] FATAL: $*" >&2; exit 1; }
warn(){ echo "[${TZ:=UTC} $(date -u +'%Y-%m-%dT%H:%M:%SZ')] WARN: $*" >&2; }

### 0. Constants ###############################################################
LOG_FILE="/var/log/docker-app.log"
EB_ENV_NAME="$(
  /opt/elasticbeanstalk/bin/get-config container -k environment_name 2>/dev/null || \
  awk -F= '/^ENVIRONMENT_NAME/ {print $2}' /opt/elasticbeanstalk/deployment/env 2>/dev/null || \
  echo "unknown"
)"
LOG_GROUP="/eb/docker/${EB_ENV_NAME//[^A-Za-z0-9._/-]/-}"
REGION="$(curl -s --retry 3 --connect-timeout 2 http://169.254.169.254/latest/meta-data/placement/region || echo "${AWS_REGION:-us-east-1}")"

log "Environment = $EB_ENV_NAME, Log group = $LOG_GROUP, Region = $REGION"

### 1. Ensure CloudWatch Agent installed ######################################
if ! rpm -q amazon-cloudwatch-agent &>/dev/null; then
  log "Installing amazon-cloudwatch-agent..."
  dnf install -y amazon-cloudwatch-agent || fail "CloudWatch Agent install failed"
else
  log "CloudWatch Agent already installed"
fi

### 2. Create CloudWatch Agent config (idempotent) ############################
CW_DIR=/opt/aws/amazon-cloudwatch-agent/etc
mkdir -p "$CW_DIR"
cat > "$CW_DIR/amazon-cloudwatch-agent.json" <<EOF
{
  "logs": {
    "logs_collected": {
      "files": {
        "collect_list": [
          {
            "file_path": "$LOG_FILE",
            "log_group_name": "$LOG_GROUP",
            "log_stream_name": "{instance_id}",
            "retention_in_days": 30,
            "timezone": "UTC"
          },
          {
            "file_path": "/opt/aws/amazon-cloudwatch-agent/logs/amazon-cloudwatch-agent.log",
            "log_group_name": "$LOG_GROUP",
            "log_stream_name": "{instance_id}-CWAgent",
            "retention_in_days": 30,
            "timezone": "UTC"
          }
        ]
      }
    }
  }
}
EOF
log "Wrote CloudWatch Agent config"

### 3. Logrotate for docker-app.log ###########################################
cat >/etc/logrotate.d/docker-app <<'EOF'
/var/log/docker-app.log {
  daily
  rotate 7
  size 100M
  missingok
  notifempty
  copytruncate
  compress
}
EOF

### 4. Create forwarder script #################################################
mkdir -p /opt/docker-logs
WRAPPER=/opt/docker-logs/stream-docker-logs.sh
cat > "$WRAPPER" <<'EOS'
#!/usr/bin/env bash
set -euo pipefail
LOG_FILE="/var/log/docker-app.log"
touch "$LOG_FILE"
while true; do
  CID="$(docker ps -q --no-trunc | head -n1)"
  if [[ -z "$CID" ]]; then
    echo "[wrapper] No container yet; retry in 3s" >&2
    sleep 3
    continue
  fi
  echo "[wrapper] Tailing container $CID" >&2
  docker logs -f "$CID" >>"$LOG_FILE" 2>&1 || true
  echo "[wrapper] docker logs exited; restarting in 2s" >&2
  sleep 2
done
EOS
chmod +x "$WRAPPER"

### 5. systemd unit for forwarder #############################################
cat > /etc/systemd/system/docker-logs-forwarder.service <<EOF
[Unit]
Description=Forward Docker container logs to file for CloudWatch
After=docker.service
Requires=docker.service

[Service]
Type=simple
Restart=always
RestartSec=2
ExecStart=$WRAPPER

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now docker-logs-forwarder.service
log "Forwarder service started"

### 6. Start CloudWatch Agent with file config ################################
/opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -a stop || true
if /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
     -a start \
     -m ec2 \
     -c "file:${CW_DIR}/amazon-cloudwatch-agent.json" \
     -s; then
  log "CloudWatch Agent started with persisted file config"
else
  fail "CloudWatch Agent failed to start"
fi

### 7. Verification summary ####################################################
log "Verification:"
systemctl -q is-active docker-logs-forwarder.service && log "✔ docker-logs-forwarder active" || fail "docker-logs-forwarder inactive"
systemctl -q is-active amazon-cloudwatch-agent.service && log "✔ CWAgent active" || fail "CWAgent inactive"
test -s "$LOG_FILE" && log "✔ $LOG_FILE exists & non-empty" || warn "Log file empty (app may not have emitted yet)"
ls -1 "$CW_DIR"/amazon-cloudwatch-agent.d/ 2>/dev/null | grep -q . && log "✔ Agent runtime config persisted" || warn "Agent runtime config not found (but service is running)"

log "🎉 Post-deploy logging setup complete"
