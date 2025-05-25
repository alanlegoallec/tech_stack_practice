.PHONY: \
  build-dev \
  clean clean-all clean-backend clean-frontend \
  clear-env \
  copy-vscode-extensions-install-script \
  debug-internal debug-remote dev prod \
  deploy-backend deploy-frontend \
  logs-backend logs-frontend \
  ssm-connect \
  test-coverage

###############################################################################
# 🔧 Configurable Variables
###############################################################################

# AWS CLI profiles
DEPLOY_PROFILE=deployer-full-stack-practice
ADMIN_PROFILE=admin-debug

# App directories
FRONTEND_DIR=frontend
BACKEND_DIR=backend

###############################################################################
# 🚀 Docker Targets
###############################################################################

# Start containers in development mode
dev:
	docker compose -f docker-compose.yaml --profile dev up --build -d

# Start containers in production mode
prod:
	docker compose -f docker-compose.yaml --profile prod up --build -d

# Start containers in remote debugging mode (outside the container)
debug-remote:
	docker compose -f docker-compose.yaml -f docker-compose.debug-remote.yaml --profile debug-remote up --build -d

# Start containers in internal debugging mode (from inside container)
debug-internal:
	docker compose -f docker-compose.yaml -f docker-compose.debug-internal.yaml --profile debug-internal up --build -d

# Clean up all Docker containers, volumes, images, and networks
clean:
	@bash scripts/clean_docker.sh

###############################################################################
# ☁️ Elastic Beanstalk Deployment
###############################################################################

deploy-frontend:
	@echo "🚀 Deploying Frontend..."
	@$(FRONTEND_DIR)/scripts/deploy.sh $(DEPLOY_PROFILE) $(FRONTEND_DIR) full-stack-practice-frontend-env

deploy-backend:
	@echo "🚀 Deploying Backend..."
	@$(BACKEND_DIR)/scripts/deploy.sh $(DEPLOY_PROFILE) $(BACKEND_DIR) full-stack-practice-backend-env

deploy-all:
	@echo "🚀 Deploying Frontend and Backend in parallel..."
	@$(MAKE) deploy-frontend & \
	 $(MAKE) deploy-backend & \
	 wait
	@echo "✅ Deployment complete."

###############################################################################
# 🔥 Elastic Beanstalk Cleanup (admin-only)
###############################################################################

clean-frontend:
	cd $(FRONTEND_DIR) && eb terminate full-stack-practice-frontend-env --force --profile $(ADMIN_PROFILE)

clean-backend:
	cd $(BACKEND_DIR) && eb terminate full-stack-practice-backend-env --force --profile $(ADMIN_PROFILE)

clean-all:
	@echo "🧹 Terminating frontend and backend environments in parallel..."
	$(MAKE) clean-frontend &
	$(MAKE) clean-backend &
	wait
	@echo "✅ Both environments terminated."

###############################################################################
# 📜 Logs and Debug Utilities
###############################################################################

logs-frontend:
	@echo "📜 Tailing Frontend logs from CloudWatch..."
	aws logs tail /eb/docker/frontend --follow --profile $(DEPLOY_PROFILE)

logs-backend:
	@echo "📜 Tailing Backend logs from CloudWatch..."
	aws logs tail /eb/docker/backend --follow --profile $(DEPLOY_PROFILE)

ssm-connect:
	./scripts/ssm-connect.sh

test-coverage:
	docker compose -f docker-compose.yaml --profile dev up --build -d
	docker compose -f docker-compose.yaml --profile dev run --rm tests pytest --cov=backend --cov-report=xml --cov-report=term-missing --cov-fail-under=75
	docker compose -f docker-compose.yaml --profile dev down

###############################################################################
# 🛠️ Utilities
###############################################################################

# Help user clear shell environment variables manually
clear-env:
	@echo "Cannot unset variables from Makefile. Please run:"
	@echo "    source scripts/clear-env.sh"
	@echo "or"
	@echo "    . scripts/clear-env.sh"

# Copy VSCode extension install script to app folders
copy-vscode-extensions-install-script:
	@echo "Copying install-vscode-extensions.sh to backend and frontend scripts directories..."
	cp scripts/install-vscode-extensions.sh $(BACKEND_DIR)/scripts/
	cp scripts/install-vscode-extensions.sh $(FRONTEND_DIR)/scripts/
	@echo "✅ Successfully copied to both directories."

# Display directory structure, helpful to debug with LLMs
tree:
	tree -L 5 -a -I '.git|.pytest_cache|__pycache__|path-to-local-vscode-extensions|*app_versions*'
