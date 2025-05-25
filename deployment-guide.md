# 🚀 Full-Stack Deployment Guide: `alg-fullstackpractice.top`

This guide documents the current state and setup of the full-stack deployment, including backend (FastAPI), frontend (Streamlit), RDS (PostgreSQL), domain routing, TLS, and infrastructure management using Elastic Beanstalk, Docker, and AWS.

---

## 📦 Stack Overview

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **DB**: AWS RDS (PostgreSQL)
- **Hosting**: AWS Elastic Beanstalk (Docker-based)
- **Domain**: `alg-fullstackpractice.top` via Namecheap, DNS managed in **Route 53**
- **TLS/HTTPS**: AWS Certificate Manager (ACM)

---

## ✅ Current Setup Summary

### Backend

- **EB Env Name**: `full-stack-practice-backend-env`
- **Custom Domain**: `api.alg-fullstackpractice.top`
- **HTTPS**: Enabled via ACM
- **Health Check**: `/health` endpoint
- **RDS Access**:
  - RDS SG (`sg-06494eb922b51d5d6`) allows access **from** EC2 SG `sg-0604b0025e3841f42`
  - EC2 instance **attached** to SG `sg-0604b0025e3841f42` and EB-managed SG
- **Environment config saved as**: `backend-with-sg`
- **Deployed with**: `backend/scripts/deploy.sh` (used by `make deploy-backend`)

### Frontend

- **EB Env Name**: `full-stack-practice-frontend-env`
- **Custom Domain**: `www.alg-fullstackpractice.top`
- **HTTPS**: Enabled via ACM
- **No DB access** required

---

## 🛡️ Security Group Design

| SG Name              | SG ID                  | Attached To     | Purpose                            |
| -------------------- | ---------------------- | --------------- | ---------------------------------- |
| `eb-backend-access`  | `sg-0604b0025e3841f42` | Backend EC2     | Grants access to RDS               |
| `rds-access-from-eb` | `sg-06494eb922b51d5d6` | RDS DB instance | Allows 5432 from backend SG        |
| Auto-generated EB SG | `sg-0b3ae44d30cc7a391` | Backend EC2     | Default internal EB routing        |
| Auto-generated EB LB | `sg-060e559f55d2843dc` | Load Balancer   | Allows inbound traffic from public |

> ✅ All SGs are actively used and necessary. No unused SGs remain after cleanup.

---

## 🛠️ Makefile Integration

```makefile
create-backend:
	cd backend && \
	eb create full-stack-practice-backend-env \
	--cfg backend-with-sg \
	--profile deployer-full-stack-practice
```

Used to **recreate the backend** environment with saved security group and instance settings.

```makefile
deploy-backend:
	@echo "🚀 Deploying Backend..."
	@backend/scripts/deploy.sh deployer-full-stack-practice backend full-stack-practice-backend-env
```

`deploy.sh` checks if environment exists:

- If not: runs `eb create --cfg backend-with-sg`
- If yes: runs `eb deploy`

---

## 🔐 Secrets Management

- **DB Password**: Fetched from AWS Secrets Manager using a custom `get_secret_value` function
- **Other Secrets**: Managed as environment variables or SSM Parameters (e.g., OpenAI API Key)

---

## 🌍 Domain & HTTPS Setup

### Route 53

- Hosted zone for `alg-fullstackpractice.top`
- CNAME records:
  - `www.alg-fullstackpractice.top → <frontend EB CNAME>`
  - `api.alg-fullstackpractice.top → <backend EB CNAME>`

### ACM

- Cert includes both:
  - `www.alg-fullstackpractice.top`
  - `api.alg-fullstackpractice.top`
- Attached to both frontend and backend environments (via load balancer listener)

---

## 📦 Redeployment Workflow

### Clean Up:

```bash
make clean-backend
```

### Recreate Environment:

```bash
make create-backend
```

### Redeploy:

```bash
make deploy-backend
```

---

## 🧹 Cost Management Checklist

- [ ] Run `make clean-backend` and `make clean-frontend` before weekends or off hours
- [ ] Confirm termination in EB console
- [ ] Keep saved config (`backend-with-sg`) up to date if changes are made

---

## 🛠️ Next Steps

- [ ] Automate backend deployment in GitHub Actions (CI/CD)
- [ ] Save frontend config (e.g., `frontend-with-acm`)
- [ ] Optionally export SG logic to Terraform later for scalability
