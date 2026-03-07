# SICOP Health Email Templates

Custom email templates for Supabase Auth that match the SICOP Health Intelligence brand identity.

## Templates Included

| Template | File | Purpose |
|----------|------|---------|
| Invitation | `supabase-invite-email.html` | User invited to create account |
| Confirm Signup | `supabase-confirm-signup.html` | Email verification after signup |
| Reset Password | `supabase-reset-password.html` | Password reset request |
| Magic Link | `supabase-magic-link.html` | Passwordless login |
| Change Email | `supabase-change-email.html` | Email address change confirmation |

## Brand Identity Applied

- **Primary Background**: `#141310` (dark)
- **Card Background**: `#1a1f1a`
- **Accent Sage**: `#84a584`
- **Text Cream**: `#f9f5df`
- **Text Light**: `#f2f5f9`
- **Typography**: Montserrat (display), Raleway (accent), Plus Jakarta Sans (body)
- **Border Radius**: 24px cards, 60px buttons (pill shape)

## Supabase Configuration

To use these templates in your Supabase project:

### 1. Go to Supabase Dashboard
Navigate to: **Authentication → Email Templates**

### 2. Copy Template Content
Copy the HTML content from each file and paste into the corresponding template in Supabase:

- **Invite user** → `supabase-invite-email.html`
- **Confirm signup** → `supabase-confirm-signup.html`
- **Reset password** → `supabase-reset-password.html`
- **Magic Link** → `supabase-magic-link.html`
- **Change Email Address** → `supabase-change-email.html`

### 3. Configure URL Placeholders
Supabase uses the following variables in templates:

| Variable | Description |
|----------|-------------|
| `{{ .SiteURL }}` | Your site URL (configured in Auth settings) |
| `{{ .ConfirmationURL }}` | The confirmation/action link |
| `{{ .Email }}` | User's email address |
| `{{ .Token }}` | The confirmation token (if needed) |

### 4. Set Site URL
In Supabase Dashboard → Authentication → URL Configuration:
- Set **Site URL** to your production domain (e.g., `https://sicop-health.com`)
- Add redirect URLs as needed

### 5. Test Emails
Use the "Send test email" feature in Supabase to verify templates render correctly.

## Email Client Compatibility

These templates include:
- **Outlook/MSO conditionals**: `[if mso]` tables for Windows Outlook
- **Responsive design**: Mobile-optimized with `@media` queries
- **Inline-ready styles**: Can be inlined with tools like [MJML](https://mjml.io/) or [Premailer](https://premailer.io/) if needed
- **Web-safe fonts**: Fallback stack for all font families

## Customization

To modify templates:
1. Edit the HTML files in this directory
2. Keep the Supabase variables (`{{ .SiteURL }}`, `{{ .ConfirmationURL }}`) intact
3. Re-upload to Supabase dashboard

## Testing Checklist

- [ ] Test in Gmail (web)
- [ ] Test in Gmail (mobile app)
- [ ] Test in Apple Mail (iOS/macOS)
- [ ] Test in Outlook (Windows)
- [ ] Verify all links work correctly
- [ ] Confirm token expiration messages are clear
- [ ] Check mobile responsiveness
