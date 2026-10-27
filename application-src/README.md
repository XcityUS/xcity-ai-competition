# Official XCITY application frontend

The public form is `application.html` on the official GitHub Pages website. It is a native React form, not an embedded remote page. It calls the private-storage API over cookie-free CORS. The API accepts only the organiser's exact origin; file/admin routes remain private. Browser-held management keys stay in URL fragments and explicit API headers, never query parameters or the public repository.

Rebuild from this directory with `npm ci && npm run build`. This writes the generated `../application.html` and hashed `../application-assets/`. The API URL is public configuration; no secret is bundled. Local preview at localhost:8765 uses the isolated local API at 127.0.0.1:8787. See the private backend project for deployment, storage and notification configuration.

The form is embedded only in `practice.html#apply`, not the two-track homepage. `brief/practice-schedule.json` sets `registration_mode` to `interest` (current) or `application` (only after the organiser opens the call). It is independent of the retired server final-upload switch. In interest mode collect four basic contact fields; in application mode explain that XCITY sends the form by email and applicants reply with materials. Neither mode shows draft or upload controls. Existing private fragment links still open `LegacyApplication` to preserve prior records.

Registration: 31 December 2026; completed email application: 31 January 2027, both 23:59 UTC. Selection: February 2027. The backend stores these new contact registrations using its existing draft status; that internal status does not mean a complete application. No automatic mail transport is configured; staff must send the application pack manually until engineer integration is ready.

Passive update subscriptions on the home/Agent pages are separate. Applying does not subscribe an applicant to marketing updates. Only display an email-delivery success after the configured server reports successful delivery.
