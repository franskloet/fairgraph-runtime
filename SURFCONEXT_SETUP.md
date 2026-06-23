# SURFconext Authentication Setup Guide

This guide details the steps required to transition the FAIRGraph platform from the local mock OIDC developer setup to the live/test SURFconext institutional authentication provider.

---

## 1. Register FAIRGraph with SURFconext

Before modifying your container configurations, your FAIRGraph deployment must be registered as a Service Provider (SP) in the SURFconext dashboard:

1. **Access Dashboard**: Log in to the [SURFconext SP Dashboard](https://sp.surfconext.nl/) (or the test/sandbox equivalent).
2. **Create Entity**: Register a new OIDC client connection for your FAIRGraph installation.
3. **Configure Redirect URI**: Specify the callback URL where SURFconext should send users after authentication. 
   - **Local testing**: `http://localhost:3000/login`
   - **Production**: `https://<YOUR-FAIRGRAPH-DOMAIN>/login`
4. **Obtain Client Credentials**: Keep note of the generated **Client ID** and **Client Secret**.
5. **Request User Attributes**: Ensure your client is authorized to request:
   - `openid`
   - `profile`
   - `email`
   - Any group/role attribute claim you plan to use for user mapping (e.g. `eduperson_entitlement`).

---

## 2. Update Docker Compose Configuration

Open your **[docker-compose.yml](file:///home/frans/Development/fair/fairgraph-2/docker-compose.yml)** file and apply the following updates to configure the environment variables:

### Step A: Configure the Central Router Gateway
Locate the `central_router` service and update its `environment` variables to point to the live SURFconext servers:

```yaml
  central_router:
    # ...
    environment:
      - AUTH_MODE=oidc                                      # Switch from 'mock' to 'oidc'
      - OIDC_ISSUER_URL=https://connect.surfconext.nl       # SURFconext issuer (use connect.test.surfconext.nl for test environment)
      - OIDC_CLIENT_ID=your-surfconext-client-id            # Your registered Client ID
      - OIDC_CLIENT_SECRET=your-surfconext-client-secret    # Your registered Client Secret
      - OIDC_AUDIENCE=your-surfconext-client-id             # Must match the audience inside the JWT
      - OIDC_REDIRECT_URI=http://localhost:3000/login       # Must match registered redirect URI in SURFconext dashboard
```

### Step B: Configure the Specialized Database Slices
To ensure each database instance (e.g. `clinical_api`, `plant_api`, `genomic_api`, `questionnaires_api`) can directly decode and verify the JWT tokens passed by the central router or frontend:

Update the variables under **each** database API service:

```yaml
  # Configure this for clinical_api, genomic_api, plant_api, and questionnaires_api
  clinical_api:
    # ...
    environment:
      - AUTH_MODE=oidc
      - OIDC_ISSUER_URL=https://connect.surfconext.nl
      - OIDC_JWKS_URL=https://connect.surfconext.nl/oauth2/certs # SURFconext public keys certs URL
```

---

## 3. Deploy and Verify

1. **Rebuild and restart the services**:
   ```bash
   docker compose up -d --build
   ```
2. **Access the Application**:
   Navigate to the login page (`http://localhost:3000/login` or your custom domain).
3. **Trigger Auth Flow**:
   Click **"Sign in with SURFconext"**. You should now be redirected to the actual SURFconext portal where you can select your home institution and log in with your institutional credentials.

---

## 4. User Role Management in FAIRGraph

FAIRGraph automatically integrates OIDC authenticated users with the local database:

1. **Auto-Registration**: The first time a user logs in via SURFconext, the Central Router creates an entry for them in `config/users_registry.json` with a default `"user"` role.
2. **Permissions Assignment**: Administrators can log in via local developer credentials, access the **Admin Panel -> Manage Users** tab, locate the newly registered OIDC user by their username/email, and assign database instances, custom roles, or groups to them.
