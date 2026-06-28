# Tech Spec: ideaweb v1
## Stack

* Frontend: 
  * UI Library: React (using Create React App)
  * State Management: Redux
  * CSS Framework: Tailwind CSS
* Backend: 
  * Runtime: Node.js (14.x)
  * Framework: Express.js
  * Database: MongoDB (Atlas)
* Storage: Cloudinary (for image and file storage)
* Authentication: Auth0 (for user authentication and authorization)

## Hosting

* Primary Platform: Vercel (for fast and secure deployment)
* Secondary Platform: Netlify (for edge caching and CDN)
* Free-tier-first: Yes, both Vercel and Netlify offer free tiers for small projects

## Data Model

* Collections:
  * `projects`: stores project metadata (e.g., name, description, owner)
  * `pages`: stores page metadata (e.g., title, content, layout)
  * `components`: stores reusable UI components (e.g., headers, footers)
  * `users`: stores user metadata (e.g., username, email, role)
* Key Fields:
  * `projectId`: unique identifier for each project
  * `pageId`: unique identifier for each page
  * `componentId`: unique identifier for each component
  * `userId`: unique identifier for each user

## API Surface

* Endpoints:
  * `GET /projects`: retrieve a list of all projects
  * `GET /projects/:projectId`: retrieve a single project by ID
  * `POST /projects`: create a new project
  * `PUT /projects/:projectId`: update an existing project
  * `DELETE /projects/:projectId`: delete a project
  * `GET /pages`: retrieve a list of all pages
  * `GET /pages/:pageId`: retrieve a single page by ID
  * `POST /pages`: create a new page
  * `PUT /pages/:pageId`: update an existing page
  * `DELETE /pages/:pageId`: delete a page
  * `GET /components`: retrieve a list of all components
  * `GET /components/:componentId`: retrieve a single component by ID
  * `POST /components`: create a new component
  * `PUT /components/:componentId`: update an existing component
  * `DELETE /components/:componentId`: delete a component
  * `GET /users`: retrieve a list of all users
  * `GET /users/:userId`: retrieve a single user by ID
  * `POST /users`: create a new user
  * `PUT /users/:userId`: update an existing user
  * `DELETE /users/:userId`: delete a user

## Security Model

* Authentication: Auth0 will handle user authentication and authorization
* Secrets: environment variables will store sensitive data (e.g., API keys, database credentials)
* IAM: role-based access control will be implemented using Auth0's built-in features

## Observability

* Logs: will be stored in a centralized logging service (e.g., Splunk, ELK)
* Metrics: will be collected using a metrics service (e.g., Prometheus, New Relic)
* Traces: will be collected using a tracing service (e.g., Jaeger, Zipkin)

## Build/CI

* Build tool: Webpack
* CI tool: GitHub Actions
* Deployment: will be automated using Vercel's and Netlify's APIs
* Testing: will be implemented using Jest and Enzyme for unit testing, and Cypress for end-to-end testing