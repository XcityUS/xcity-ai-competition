# Official XCITY application frontend

The public form is `application.html` on the official GitHub Pages website. It is a native React form, not an embedded remote page. It calls the private-storage API over cookie-free CORS. The API accepts only the organiser's exact origin; file/admin routes remain private. Browser-held management keys stay in URL fragments and explicit API headers, never query parameters or the public repository.

Rebuild from this directory with `npm ci && npm run build`. This writes the generated `../application.html` and hashed `../application-assets/`. The API URL is public configuration; no secret is bundled. Local preview at localhost:8765 uses the isolated local API at 127.0.0.1:8787. See the private backend project for deployment, storage and notification configuration.

Schedule is recorded in `brief/practice-schedule.json`. Registration and draft preparation are open; final submission is controlled by the server and remains closed until the organiser explicitly opens it. Do not infer opening from the presence of a final deadline. Registration: 31 December 2026; complete application: 31 January 2027, both at 23:59 UTC. Selection: February 2027.

Passive update subscriptions on the home/Agent pages are separate. Applying does not subscribe an applicant to marketing updates. Only display an email-delivery success after the configured server reports successful delivery.
