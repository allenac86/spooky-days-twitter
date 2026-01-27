# spooky-days-twitter

[![CI](https://github.com/allenac86/spooky-days-twitter/actions/workflows/ci.yml/badge.svg)](https://github.com/allenac86/spooky-days-twitter/actions/workflows/ci.yml)
[![CD](https://github.com/allenac86/spooky-days-twitter/actions/workflows/cd.yml/badge.svg)](https://github.com/allenac86/spooky-days-twitter/actions/workflows/cd.yml)
[![Security Scan](https://github.com/allenac86/spooky-days-twitter/actions/workflows/security-scan.yml/badge.svg)](https://github.com/allenac86/spooky-days-twitter/actions/workflows/security-scan.yml)
[![Code Coverage](https://codecov.io/gh/allenac86/spooky-days-twitter/branch/main/graph/badge.svg)](https://codecov.io/gh/allenac86/spooky-days-twitter)

A serverless application that generates images of various "National Days" with a spooky twist using OpenAI's DALL-E 3 and automatically posts them to Twitter (X) Monday through Friday at 8:00 AM EST.

**Status:** 🟢 Live and actively posting

## Architecture

**AWS Services Used:**
- **ACM** - SSL/TLS certificates for secure CloudFront connections
- **CloudFront** - Content delivery network for static site hosting with access logging enabled to S3
- **CloudWatch Dashboard** - Dashboard for CloudFront, DynamoDB, Lambda, and S3 metrics
- **CloudWatch Logs** - Lambda function logging and monitoring
- **EventBridge** - Cron-based scheduling (Mon-Fri at 1:00 PM UTC / 8:00 AM EST)
- **DynamoDB** - Job tracking and post history
- **IAM** - Role-based access control and permissions
- **KMS** - Encryption for Secrets Manager and S3 buckets at rest with automatic key rotation
- **Lambda** - Serverless compute for image generation, Twitter posting, and an API for the UI
- **Lambda Layers** - Dependencies for Python Lambdas (OpenAI SDK, Tweepy, boto3)
- **Route 53** - DNS management for custom domain
- **S3** - Storage for Lambda code packages, generated images, configuration, and static site hosting (KMS-encrypted with public access blocked)
- **Secrets Manager** - Secure storage for OpenAI and Twitter API credentials (KMS-encrypted)

**Application Flow:**

1. **EventBridge Cron Trigger** - Every weekday morning at 8:00 AM EST, EventBridge triggers the Image Generation Lambda
2. **Image Generation Lambda** - Retrieves the national-days.json configuration from S3, fetches OpenAI API credentials from Secrets Manager, generates spooky-themed images using DALL-E 3, uploads encrypted images to S3 (`images/` folder), and inserts job records into DynamoDB with status "uploaded"
3. **S3 Event Notification** - When an image is uploaded to S3, it automatically triggers the Twitter Post Lambda
4. **Twitter Post Lambda** - Downloads the image from S3, retrieves Twitter API credentials from Secrets Manager, posts the image to Twitter with a caption, and updates the DynamoDB record with the caption and status "posted"

**Infrastructure:**
- Managed via Terraform Cloud
- CI/CD via GitHub Actions (build → deploy pipeline)
- Lambda Layers built using official AWS Lambda Docker images for binary compatibility

**Technology**
- **Python**
- **Node.js**
- **React**
- **Terraform**
- **GitHub Actions**

Architecture Diagram (AI generated using Eraser [https://www.eraser.io/ai/aws-diagram-generator]):

<img width="4297" height="1745" alt="image" src="https://github.com/user-attachments/assets/b0748c4f-33da-49f5-8749-a92640fd22e1" />


## Twitter Profile
([https://x.com/spooky_days_gpt]):

<img width="655" height="548" alt="image" src="https://github.com/user-attachments/assets/03a83fb0-a93e-4cb7-9ddd-ce7debb347c1" />


## Example Twitter Post:

<img width="650" height="583" alt="image" src="https://github.com/user-attachments/assets/e9f94c35-df8e-404a-a65b-ad8fdf54c874" />


## CI/CD Pipeline

The project includes a comprehensive CI/CD pipeline with quality gates, security scanning, and automated deployments. The lint, test, and security-scan stages run in parallel. The build runs after successful execution of the lint, test, and security-scan stages. Once build is successful, packages are uploaded to AWS, and Terraform variables pointing to the new packages are updated in the Terraform Cloud Workspace, the deploy stage triggers a Terraform run to deploy the updated infrastructure and point to the latest code packages.

### Pipeline Stages

**1. Code Quality (Linting)**
- **Ruff** - Python linter and formatter
  - Enforces PEP 8 style guidelines
  - 88 character line length
  - Checks for code quality issues (pyflakes, bugbear, pyupgrade)
  - Import sorting (isort)
  - Format verification to ensure consistent code style
- **ESLint** - JavaScript/TypeScript linter for Node.js Lambda
  - Enforces code quality and style for gallery API Lambda
  - Flat config with modern rules
  - **Pipeline behavior:** Failures block the pipeline

**2. Testing**
- **pytest** - Unit testing framework for the Python Lambdas
  - Runs unit tests for image_gen and twitter_post Lambdas
  - Branch coverage analysis with pytest-cov
  - Mocking of AWS services (S3, DynamoDB, Secrets Manager) using moto
  - Mocking of external APIs (OpenAI, Twitter)
- **Jest** - Unit testing framework for the Node.js Lambda
  - Runs unit tests for gallery API Lambda
  - Coverage reporting with LCOV
  - **Pipeline behavior:** Test failures block the pipeline
- **Coverage Reporting:**
  - Results uploaded to Codecov for tracking
  - Terminal output with missing coverage report

**3. Security Scanning**
- **Bandit** - Python SAST (Static Application Security Testing)
  - Scans Lambda code for common security issues
  - Severity threshold: High and Critical
  - Results uploaded to GitHub Security tab (SARIF format)
- **Gitleaks** - Secret detection
  - Scans entire repository history for exposed secrets
  - Prevents API keys, tokens, and credentials from being committed
- **pip-audit** - Python dependency vulnerability scanning
  - Checks all dependencies in requirements.txt files
  - Identifies known CVEs in Python packages
  - Scans both image_gen and twitter_post dependencies
- **Semgrep** - Node.js SAST
  - Scans gallery API Lambda for security issues
  - Results uploaded to GitHub Security tab (SARIF format)
- **npm audit** - Node.js dependency vulnerability scanning
  - Checks dependencies in gallery API Lambda
- **Trivy** - Infrastructure as Code (IaC) scanning
  - Scans Terraform configurations for security misconfigurations
  - Severity threshold: High and Critical
  - Results uploaded to GitHub Security tab (SARIF format)
- **Pipeline behavior:** Security findings are reported but don't block deployment (continue-on-error)

**4. Build**
- Package Lambda function code (.zip files)
- Build Lambda Layers using official AWS Lambda Docker images
  - Ensures binary compatibility with Lambda runtime
  - Separate layers for image_gen and twitter_post dependencies
- Upload artifacts to S3
- Update Terraform Cloud workspace variables
- Conditional layer publishing (controlled via GitHub variable)
- **Pipeline behavior:** Build failures block deployment

**5. Deploy**
- Triggers deployment workflow
- Requires dev environment approval
- Updates Lambda functions with new code

### Security Findings

All security scan results are available in the [GitHub Security tab](https://github.com/allenac86/spooky-days-twitter/security) with automated SARIF uploads for Bandit and Trivy scans.

### Pre-Commit Hooks

The repository includes pre-commit hooks to catch issues before they're committed:

**Setup (one-time):**
```bash
python -m pip install pre-commit
python -m pre_commit install
```

**Hooks configured:**
- **Ruff** - Auto-fixes linting issues and formats code before commit
- **Gitleaks** - Blocks commits containing secrets or credentials

The hooks run automatically on `git commit`. To manually run on all files:
```bash
python -m pre_commit run --all-files
```


### Roadmap

### Reliability & Error Handling
- Add SQS-based retry and DLQ for both image generation and Twitter Lambdas
- On failure, event is retried after 20 minutes via SQS
- Second failure sends event to DLQ
- Add idempotency decorator for twitter_post Lambda
- Enhance retry logic with exponential backoff

### Frontend & User Experience
- Build a React frontend (Vite + React Bootstrap) to display a gallery of all images posted to Twitter
- Host the frontend as a static site on S3, served via CloudFront with TLS and a custom domain managed by Route 53
- Add an admin dashboard protected by Cognito authentication to manually trigger adhoc image generation and view twitter account metrics

### API & Security
- Implement a Node.js/TypeScript Lambda for gallery and admin API
- Route API requests through API Gateway, secured with Cognito User Pool authorizer
- Log all admin/API actions to DynamoDB for audit

### Testing & Quality
- Refactor all Lambda tests into organized subdirectories under `/tests/` -- IN PROGRESS --
- Add Jest and ESLint tooling for Node.js Lambda, with pre-commit hooks and security scanning
- Maintain high code coverage and CI/CD quality gates for the new Lambda and UI

### Observability
- Enable X-Ray tracing and CloudWatch dashboards for all Lambdas
- Configure alarms for Lambda errors, DLQ messages, and API failures

### Documentation
- Document threat model
- Add cost estimate breakdown

### Multi-Environment (Stretch)
- Support separate dev and prod environments via Terraform Cloud
